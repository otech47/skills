#!/usr/bin/env python3
import argparse
import base64
import hashlib
import io
import json
import math
import re
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
import wave
from pathlib import Path


class Invalid(ValueError):
    pass


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def pcm_from_wav(data):
    try:
        with wave.open(io.BytesIO(data)) as source:
            channels, width, rate = source.getnchannels(), source.getsampwidth(), source.getframerate()
            # Kokoro sends a streaming WAV length. Count the PCM bytes, not the header frames.
            pcm = source.readframes(source.getnframes())
    except (wave.Error, EOFError) as error:
        raise Invalid("speech response is not a PCM WAV") from error
    if channels != 1 or width != 2 or rate < 8000 or not pcm or len(pcm) % (channels * width):
        raise Invalid("speech must be nonempty mono 16-bit PCM with complete samples")
    return pcm, rate


def wav_bytes(pcm, rate):
    destination = io.BytesIO()
    with wave.open(destination, "wb") as output:
        output.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        output.writeframes(pcm)
    return destination.getvalue()


def lexical(text):
    return "".join(re.findall(r"\w", text.casefold()))


def validate_words(words, text, duration):
    if not isinstance(words, list) or not words:
        raise Invalid("speech response has no word alignment")
    prior, aligned = 0.0, []
    for index, word in enumerate(words):
        if not isinstance(word, dict) or not isinstance(word.get("word"), str):
            raise Invalid("speech response has an invalid word record")
        start, end = word.get("start_time"), word.get("end_time")
        if any(isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) for t in (start, end)):
            raise Invalid("word alignment contains a nonnumeric timestamp")
        if index == 0 and -0.05 <= start < 0 < end:
            word = word | {"source_start_time": start, "source_end_time": end, "start_time": 0.0, "alignment_adjustment": "first token overlaps Kokoro's leading audio trim by at most 50 ms"}
            start = 0.0
        if start < 0 or end <= start or start < prior - 0.001:
            raise Invalid("word alignment is unordered or outside the measured audio")
        if end > duration + 0.001:
            if lexical(word["word"]):
                raise Invalid("spoken-word alignment exceeds the measured audio")
            word = word | {"source_start_time": start, "source_end_time": end, "start_time": min(start, duration), "end_time": duration, "alignment_adjustment": "unspoken punctuation clipped to audio boundary"}
        aligned.append(word)
        prior = end
    if lexical("".join(word["word"] for word in words)) != lexical(text):
        raise Invalid("alignment text differs from narration; spell out numbers and abbreviations")
    return aligned


def speech(text, args, cache):
    identity = {"format_version": 1, "provider": "kokoro-captioned-speech", "base_url": args.base_url, "voice": args.voice, "speed": args.speed, "text": text}
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    audio_path, words_path = cache / (key + ".wav"), cache / (key + ".words.json")
    hit = audio_path.exists() and words_path.exists()
    if hit:
        pcm, rate = pcm_from_wav(audio_path.read_bytes())
        words = json.loads(words_path.read_text())
    else:
        request = urllib.request.Request(args.base_url.rstrip("/") + "/dev/captioned_speech", json.dumps({"model": "kokoro", "input": text, "voice": args.voice, "speed": args.speed, "response_format": "wav", "stream": False, "return_timestamps": True}).encode(), {"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=args.timeout) as response:
                data = json.load(response)
        except urllib.error.HTTPError as error:
            raise Invalid(f"Kokoro returned HTTP {error.code}") from error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise Invalid("Kokoro endpoint is unavailable") from error
        except (json.JSONDecodeError, UnicodeError) as error:
            raise Invalid("Kokoro returned invalid JSON") from error
        try:
            pcm, rate = pcm_from_wav(base64.b64decode(data["audio"], validate=True))
            words = data["timestamps"]
        except (KeyError, TypeError, ValueError) as error:
            raise Invalid("Kokoro returned invalid audio or alignment") from error
    duration = len(pcm) / (2 * rate)
    try:
        aligned = validate_words(words, text, duration)
    except Invalid:
        if not hit:
            (cache / ("rejected-" + key + ".wav")).write_bytes(wav_bytes(pcm, rate))
            save_json(cache / ("rejected-" + key + ".words.json"), words)
            save_json(cache / ("rejected-" + key + ".json"), identity)
        raise
    if not hit:
        audio_path.write_bytes(wav_bytes(pcm, rate))
        save_json(words_path, words)
        save_json(cache / (key + ".json"), identity | {"duration": duration, "sample_rate": rate})
    return pcm, rate, aligned, key, hit


def display_text(words):
    text = " ".join(word["word"] for word in words)
    text = re.sub(r"\s+([,.;:!?%])", r"\1", text)
    text = re.sub(r"\s*(['\u2019])\s*", r"\1", text)
    text = re.sub(r"\s*-\s*", "-", text)
    return text.strip()


def stamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    secs, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}.{milliseconds:03}"


def fframes_stamp(seconds):
    minutes, remainder = divmod(round(seconds * 1000), 60000)
    secs, milliseconds = divmod(remainder, 1000)
    return f"{minutes:02}:{secs:02}.{milliseconds:03}"


def caption_groups(words):
    groups, pending = [], []
    for word in words:
        candidate = pending + [word]
        if pending and (len(display_text(candidate)) > 72 or candidate[-1]["end_time"] - candidate[0]["start_time"] > 5.0):
            groups.append(pending)
            pending = []
        pending.append(word)
        if re.search(r"[.!?]$", word["word"]):
            groups.append(pending)
            pending = []
    if pending:
        groups.append(pending)
    return groups


def generate(args):
    args.output.mkdir(parents=True, exist_ok=True)
    save_json(args.output / "generation.json", {"status": "generating"})
    save_json(args.output / "timing.json", {"status": "generating"})
    source = args.plan.read_bytes()
    source_hash = hashlib.sha256(source).hexdigest()
    plan = json.loads(source)
    scenes = plan.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise Invalid("plan must contain a nonempty scenes list")
    ids = set()
    for scene in scenes:
        if not isinstance(scene, dict) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", scene.get("id", "")) or scene["id"] in ids:
            raise Invalid("scene IDs must be unique lowercase names with optional hyphens")
        ids.add(scene["id"])
        phrases = scene.get("narration")
        if isinstance(phrases, str):
            phrases = [phrases]
        if not isinstance(phrases, list) or not phrases or any(not isinstance(p, str) or not p.strip() for p in phrases):
            raise Invalid("each scene needs narration text or a nonempty list of phrases")
        if not isinstance(scene.get("visual"), str) or not scene["visual"].strip():
            raise Invalid("each scene needs a visual description")
        scene["phrases"] = phrases
    cache = args.cache or args.output / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    (args.output / "scenes").mkdir(exist_ok=True)
    (args.output / "plan.json").write_bytes(source)
    combined, global_words, timeline, cues = bytearray(), [], [], []
    sample_rate, hits, requests = None, 0, 0
    for scene in scenes:
        scene_pcm, scene_words, phrase_timing = bytearray(), [], []
        for index, text in enumerate(scene["phrases"]):
            try:
                pcm, rate, words, key, hit = speech(text, args, cache)
            except Invalid as error:
                raise Invalid(f"scene {scene['id']}, phrase {index + 1}: {error}") from error
            hits += int(hit)
            requests += int(not hit)
            sample_rate = sample_rate or rate
            if rate != sample_rate:
                raise Invalid("speech sample rates differ between phrases")
            if rate % args.fps:
                raise Invalid("audio sample rate must divide evenly into the video frame rate")
            hold = args.scene_lead if index == 0 else args.phrase_hold
            scene_pcm.extend(b"\x00\x00" * round(hold * rate))
            local_start = len(scene_pcm) / (2 * rate)
            global_start = (len(combined) + len(scene_pcm)) / (2 * rate)
            shifted = [word | {"start_time": word["start_time"] + global_start, "end_time": word["end_time"] + global_start, "scene": scene["id"]} for word in words]
            global_words.extend(shifted)
            cues.extend(caption_groups(shifted))
            scene_words.extend([word | {"start_time": word["start_time"] + local_start, "end_time": word["end_time"] + local_start} for word in words])
            phrase_timing.append({"index": index, "start": global_start, "end": global_start + len(pcm) / (2 * rate), "duration": len(pcm) / (2 * rate), "cache_key": key, "audio": str((cache / (key + ".wav")).resolve()), "words": str((cache / (key + ".words.json")).resolve())})
            scene_pcm.extend(pcm)
        scene_pcm.extend(b"\x00\x00" * round(args.scene_hold * sample_rate))
        samples_per_frame = sample_rate // args.fps
        missing_samples = (-len(scene_pcm) // 2) % samples_per_frame
        scene_pcm.extend(b"\x00\x00" * missing_samples)
        start = len(combined) / (2 * sample_rate)
        duration = len(scene_pcm) / (2 * sample_rate)
        audio_path, words_path = f"scenes/{scene['id']}.wav", f"scenes/{scene['id']}.words.json"
        (args.output / audio_path).write_bytes(wav_bytes(scene_pcm, sample_rate))
        save_json(args.output / words_path, scene_words)
        timeline.append({"id": scene["id"], "visual": scene["visual"], "start": start, "end": start + duration, "duration": duration, "audio": audio_path, "words": words_path, "phrases": phrase_timing})
        combined.extend(scene_pcm)
    duration = len(combined) / (2 * sample_rate)
    (args.output / "narration.wav").write_bytes(wav_bytes(combined, sample_rate))
    save_json(args.output / "words.json", global_words)
    captions = ["WEBVTT", ""]
    fframes_captions = ["WEBVTT", ""]
    for index, words in enumerate(cues, 1):
        lines = textwrap.wrap(display_text(words), width=42, break_long_words=False, break_on_hyphens=False)
        if len(lines) > 2 or any(len(line) > 42 for line in lines):
            raise Invalid("caption cannot fit two 42-character lines; shorten the narration phrase")
        captions.extend([str(index), f"{stamp(words[0]['start_time'])} --> {stamp(words[-1]['end_time'])}", *lines, ""])
        if args.fframes_captions:
            fframes_captions.extend([str(index), f"{fframes_stamp(words[0]['start_time'])} --> {fframes_stamp(words[-1]['end_time'])}", "<br>".join(lines), ""])
    (args.output / "captions.vtt").write_text("\n".join(captions) + "\n")
    if args.fframes_captions:
        (args.output / "captions-fframes.vtt").write_text("\n".join(fframes_captions) + "\n")
    transcript = [f"# {plan.get('title', 'video transcript')}", ""]
    if plan.get("qualification"):
        transcript.extend([plan["qualification"], ""])
    for scene in scenes:
        transcript.extend([f"## {scene['id']}", "", f"Visual: {scene['visual']}", "", " ".join(scene["phrases"]), ""])
    (args.output / "transcript.md").write_text("\n".join(transcript))
    timing = {"version": 1, "status": "complete", "source_sha256": source_hash, "provider": "kokoro-captioned-speech", "voice": args.voice, "speed": args.speed, "sample_rate": sample_rate, "fps": args.fps, "duration": duration, "narration": "narration.wav", "captions": "captions.vtt", "transcript": "transcript.md", "words": "words.json", "holds": {"scene_lead": args.scene_lead, "phrase": args.phrase_hold, "scene_end": args.scene_hold}, "alignment_adjustments": sum("alignment_adjustment" in word for word in global_words), "scenes": timeline}
    if args.fframes_captions:
        timing["captions_fframes"] = "captions-fframes.vtt"
    save_json(args.output / "timing.json", timing)
    summary = {"status": "complete", "duration": duration, "scenes": len(scenes), "synthesized_phrases": requests, "cached_phrases": hits, "timing": str((args.output / "timing.json").resolve())}
    save_json(args.output / "generation.json", summary)
    print(json.dumps(summary))


def main():
    parser = argparse.ArgumentParser(description="Generate timed narration and phrase captions with local Kokoro.")
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--voice", default="af_heart")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--fps", type=int, default=30, help="Pad scene WAVs to whole video frames.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8880")
    parser.add_argument("--cache", type=Path)
    parser.add_argument("--fframes-captions", action="store_true", help="Also export one-line cues with total-minute timestamps for the pinned FFrames parser.")
    parser.add_argument("--scene-lead", type=float, default=0.6)
    parser.add_argument("--scene-hold", type=float, default=0.8)
    parser.add_argument("--phrase-hold", type=float, default=0.15)
    parser.add_argument("--timeout", type=float, default=180)
    args = parser.parse_args()
    endpoint = urllib.parse.urlsplit(args.base_url)
    if endpoint.scheme not in ("http", "https") or not endpoint.hostname or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment:
        parser.error("base URL must be an HTTP endpoint without credentials, query, or fragment")
    if not 1 <= args.fps <= 120 or not 0.25 <= args.speed <= 4 or not 0 < args.timeout <= 600 or any(not math.isfinite(value) or not 0 <= value <= 10 for value in (args.scene_lead, args.scene_hold, args.phrase_hold)):
        parser.error("speed, timeout, or hold duration is outside its supported range")
    try:
        generate(args)
    except (Invalid, OSError, ValueError, TypeError) as error:
        message = str(error) if isinstance(error, Invalid) else "invalid input, cache, or output path"
        if args.output.is_dir():
            save_json(args.output / "generation.json", {"status": "failed", "error": message})
            save_json(args.output / "timing.json", {"status": "failed", "error": message})
        print(f"narration failed: {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
