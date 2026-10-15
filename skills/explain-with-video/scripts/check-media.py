#!/usr/bin/env python3
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys


def run(command):
    return subprocess.run(command, capture_output=True, text=True)


def seconds(value):
    parts = value.split(":")
    if len(parts) not in (2, 3) or not re.fullmatch(r"(?:\d{2,}:)?\d{2}:\d{2}\.\d{3}", value):
        raise ValueError("invalid WebVTT timestamp")
    numbers = [float(part) for part in parts]
    if numbers[-1] >= 60 or numbers[-2] >= 60:
        raise ValueError("invalid WebVTT timestamp")
    return sum(number * 60 ** index for index, number in enumerate(reversed(numbers)))


def check_captions(path, duration):
    errors, warnings, cues = [], [], []
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    if not text.startswith("WEBVTT\n"):
        return {"errors": ["captions must begin with WEBVTT"], "warnings": [], "cues": 0}
    previous_end = 0.0
    for block in re.split(r"\n\s*\n", text.strip())[1:]:
        lines = block.splitlines()
        if lines[0].startswith(("NOTE", "STYLE", "REGION")):
            continue
        offset = 0 if "-->" in lines[0] else 1
        if offset >= len(lines) or "-->" not in lines[offset]:
            errors.append("caption block has no timestamp")
            continue
        try:
            start_text, end_text = lines[offset].split(" --> ")
            start, end = seconds(start_text), seconds(end_text.split()[0])
        except (ValueError, IndexError):
            errors.append("caption block has an invalid timestamp")
            continue
        content = lines[offset + 1:]
        index = len(cues) + 1
        if start < 0 or end <= start or start < previous_end - 0.001:
            errors.append(f"caption {index} is unordered or overlaps")
        if end > duration + 0.05:
            errors.append(f"caption {index} ends beyond the media duration")
        if not content or len(content) > 2 or any(len(re.sub(r"<[^>]*>", "", line)) > 42 for line in content):
            errors.append(f"caption {index} must fit one or two lines of up to 42 characters")
        count = sum(len(re.sub(r"<[^>]*>", "", line)) for line in content)
        cps = count / (end - start) if end > start else 0
        if cps > 25:
            warnings.append(f"caption {index} exceeds 25 characters per second")
        cues.append({"start": start, "end": end, "characters_per_second": round(cps, 2)})
        previous_end = end
    if not cues:
        errors.append("captions contain no cues")
    return {"errors": errors, "warnings": warnings, "cues": len(cues), "first_start": cues[0]["start"] if cues else None, "last_end": cues[-1]["end"] if cues else None, "max_characters_per_second": max((cue["characters_per_second"] for cue in cues), default=0)}


def inspect(args):
    report = {"file": str(args.media.resolve()), "passed": False, "errors": [], "warnings": [], "manual_review": {"audio_listening": "not performed", "visual_review": "not performed"}}
    errors, warnings = report["errors"], report["warnings"]
    for executable in ("ffmpeg", "ffprobe"):
        if not shutil.which(executable):
            errors.append(f"{executable} is unavailable")
    if not args.media.is_file():
        errors.append("media file does not exist")
    if errors:
        return report
    digest = hashlib.sha256()
    with args.media.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    report["sha256"] = digest.hexdigest()
    report["bytes"] = args.media.stat().st_size
    probe = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(args.media)])
    if probe.returncode:
        errors.append("ffprobe cannot read the media")
        return report
    try:
        data = json.loads(probe.stdout)
        duration = float(data["format"]["duration"])
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError()
    except (json.JSONDecodeError, KeyError, ValueError):
        errors.append("media duration is missing or invalid")
        return report
    report["duration"] = duration
    videos = [stream for stream in data.get("streams", []) if stream.get("codec_type") == "video" and not stream.get("disposition", {}).get("attached_pic")]
    audios = [stream for stream in data.get("streams", []) if stream.get("codec_type") == "audio"]
    report["video"] = [{key: stream.get(key) for key in ("codec_name", "width", "height", "pix_fmt", "avg_frame_rate", "duration")} for stream in videos]
    report["audio"] = [{key: stream.get(key) for key in ("codec_name", "sample_rate", "channels", "duration")} for stream in audios]
    if not videos:
        errors.append("media has no video stream")
    for video in videos:
        try:
            fps = float(Fraction(video["avg_frame_rate"]))
        except (KeyError, ValueError, ZeroDivisionError):
            fps = 0
        if not fps > 0 or not video.get("width", 0) > 0 or not video.get("height", 0) > 0:
            errors.append("video dimensions or frame rate are invalid")
        report["video"][videos.index(video)]["fps"] = fps
        if args.width and video.get("width") != args.width:
            errors.append(f"video width is not {args.width}")
        if args.height and video.get("height") != args.height:
            errors.append(f"video height is not {args.height}")
    if not audios and not args.silent:
        errors.append("media has no audio stream")
    if not audios and args.silent:
        report["manual_review"]["audio_listening"] = "not applicable: silent video"
    decoded = run(["ffmpeg", "-v", "error", "-xerror", "-i", str(args.media), "-map", "0:v?", "-map", "0:a?", "-f", "null", "-"])
    report["decoded"] = decoded.returncode == 0 and not decoded.stderr.strip()
    if not report["decoded"]:
        errors.append("final media did not decode cleanly")
    if audios:
        measured = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(args.media), "-map", "0:a:0", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
        blocks = re.findall(r"\{[^{}]*\}", measured.stderr)
        try:
            loudness = json.loads(blocks[-1])
            integrated, peak = float(loudness["input_i"]), float(loudness["input_tp"])
            report["loudness"] = {"integrated_lufs": integrated if math.isfinite(integrated) else None, "true_peak_dbtp": peak if math.isfinite(peak) else None, "range_lu": float(loudness["input_lra"])}
            if measured.returncode or not math.isfinite(integrated) or not math.isfinite(peak):
                errors.append("audio is silent or loudness could not be measured")
            else:
                if peak >= 0:
                    errors.append("audio true peak reaches or exceeds 0 dBTP")
                if integrated < -24 or integrated > -12:
                    warnings.append("speech loudness is outside the review range of -24 to -12 LUFS")
                if peak > -1:
                    warnings.append("audio true peak exceeds -1 dBTP")
        except (IndexError, KeyError, ValueError, json.JSONDecodeError):
            errors.append("audio loudness could not be measured")
    if args.captions:
        try:
            caption_report = check_captions(args.captions, duration)
            report["captions"] = caption_report
            errors.extend(caption_report["errors"])
            warnings.extend(caption_report["warnings"])
        except (OSError, UnicodeError):
            errors.append("captions file cannot be read")
    elif not args.silent:
        errors.append("narrated video requires captions")
    report["passed"] = not errors
    return report


def main():
    parser = argparse.ArgumentParser(description="Decode final media and check streams, captions, and audio levels.")
    parser.add_argument("media", type=Path)
    parser.add_argument("--captions", type=Path)
    parser.add_argument("--silent", action="store_true", help="Allow an explicitly silent video without audio or captions.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    args = parser.parse_args()
    report = inspect(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"passed": report["passed"], "errors": report["errors"], "warnings": report["warnings"], "report": str(args.output.resolve())}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
