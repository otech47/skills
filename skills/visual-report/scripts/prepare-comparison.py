#!/usr/bin/env python3
"""Prepare both report modes for one or two models without launching inference."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re
import secrets
import stat


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    "check-render.sh", "check-render.cjs", "render-page.cjs",
    "freeze-diagrams.sh", "stamp-signature.py", "read-session-effort.py",
    "read-codex-session.py", "roll-flair.sh", "roll-flair.py",
    "package.json", "package-lock.json",
)
COLORS = {
    "bg", "surface", "surface-2", "ink", "ink-soft", "ink-faint", "line",
    "accent", "accent-soft", "good", "warn",
}
STARTUP_PROMPT = "Read ./runner.md and complete its task."
RUNNER = """# report task

Read `input/task.md` and the frozen evidence in `input/packet/`. Read `skill/guide.md` completely and follow its report method. Resolve the guide's `references/`, `assets/`, and `scripts/` paths from `skill/`.

When the guide names the prose-style skill, read and apply the frozen copy at `skill/references/prose-style.md`.

If a named dataviz skill is unavailable, use an ordinary chart with units, a truthful scale and denominators, and labeled uncertainty. Do not fetch an unrelated skill.

Use only the frozen packet as subject evidence. Do not perform live research, search subject memories, open old reports, inspect other authors' outputs, or read coordinator files. Source links may appear in the report without being fetched. Record missing evidence and qualify affected claims. Do not fill gaps with invented facts.

Use this directory as the report workspace. Write the final self-contained HTML to `outputs/report.html`, planning records and appendices to `files/`, and checks and screenshots beneath this directory. These paths replace the guide's scratch-creation and report-location instructions. Keep all work local. Do not open a browser window, publish, or send the report. Headless rendering for the required checks is allowed.

Use the supplied template's fixed light and dark palette. Decorative flair is disabled in this skill copy. Do not roll colors, add generated flair, or change global toggles, configuration, trust, permissions, or hooks. Follow the current authorization and sandbox rules. This snapshot separates task inputs procedurally; it is not a filesystem sandbox.

Stamp the final report with its actual creator, recorded effort, and available session counters before its final render check. Read only this run's exact transcript for attribution. Use unknown when the record is unavailable and explain that gap in `files/run-notes.md`. Keep the signed original at `outputs/report.html`. Signature masking belongs only to later review copies prepared by the coordinator.

Complete the guide's render and visual checks. Record missing evidence, material assumptions, checked views, unsupported checks, and remaining limitations in `files/run-notes.md`. Return the report path and a brief result.
"""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def file_snapshot(path):
    path = Path(path)
    mode = path.lstat().st_mode
    if stat.S_ISLNK(mode):
        raise ValueError(f"symlink is not allowed: {path}")
    if not stat.S_ISREG(mode):
        raise ValueError(f"expected a regular file: {path}")
    return path.read_bytes(), stat.S_IMODE(mode)


def tree_snapshot(root, *, dependency_links=False):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"expected a directory without a symlink: {root}")
    boundary = root.resolve()
    files = {}

    def visit(path, relative, ancestors):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            if not dependency_links:
                raise ValueError(f"symlink is not allowed: {path}")
            target = path.resolve(strict=True)
            if not target.is_relative_to(boundary):
                raise ValueError(f"dependency symlink leaves its tree: {path}")
            visit(target, relative, ancestors)
        elif stat.S_ISDIR(mode):
            real = path.resolve()
            if real in ancestors:
                raise ValueError(f"dependency symlink cycle: {path}")
            for child in sorted(path.iterdir()):
                visit(child, relative / child.name, ancestors | {real})
        elif stat.S_ISREG(mode):
            files[relative.as_posix()] = file_snapshot(path)
        else:
            raise ValueError(f"unsupported file type: {path}")

    visit(root, Path(), set())
    return files


def tree_hashes(files):
    hashes = {name: sha256(value[0]) for name, value in sorted(files.items())}
    encoded = json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()
    return {"sha256": sha256(encoded), "files": hashes}


def palette(template):
    roots = re.findall(r":root\s*\{([^}]+)\}", template.decode(), re.S)
    result = []
    for block in roots:
        values = dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);", block))
        if COLORS <= values.keys():
            result.append({name: values[name].strip() for name in sorted(COLORS)})
    if len(result) != 2:
        raise ValueError("template must define complete fixed light and dark palettes")
    return result


def skill_snapshots(skill_root, original_root=None):
    skill_root = Path(skill_root)
    original_files = {
        "guide.md": file_snapshot(skill_root / "references/sequence.md"),
        "references/information-hierarchy.md": file_snapshot(skill_root / "references/information-hierarchy.md"),
        "assets/report-template.html": file_snapshot(skill_root / "assets/report-template.html"),
    }
    if original_root is not None:
        original_root = Path(original_root)
        for name, (data, _) in original_files.items():
            backup = original_root / ("SKILL.md" if name == "guide.md" else name)
            if data != file_snapshot(backup)[0]:
                raise ValueError(f"{name} differs from the preserved original at {backup}")

    shared = {
        f"scripts/{name}": file_snapshot(skill_root / "scripts" / name)
        for name in SCRIPTS
    }
    dependencies = tree_snapshot(skill_root / "scripts/node_modules", dependency_links=True)
    package = json.loads(shared["scripts/package.json"][0])
    for name in package.get("dependencies", {}):
        if f"{name}/package.json" not in dependencies:
            raise ValueError(f"installed script dependency is missing: {name}")
    shared.update({f"scripts/node_modules/{name}": data for name, data in dependencies.items()})
    shared["references/render-checks.md"] = file_snapshot(skill_root / "references/render-checks.md")
    shared["references/prose-style.md"] = file_snapshot(skill_root / "references/prose-style.md")
    for name in ("google-devdocs.md", "ast100.md"):
        source = skill_root / "references" / name
        if source.exists() or source.is_symlink():
            shared[f"references/{name}"] = file_snapshot(source)
    for name in ("flair-chrome.md", "flair-chrome.md.off"):
        source = skill_root / "references" / name
        if source.exists() or source.is_symlink():
            shared["references/flair-chrome.md.off"] = file_snapshot(source)
            break

    original_template = original_files["assets/report-template.html"]
    question_template = file_snapshot(skill_root / "assets/questions-template.html")
    if palette(original_template[0]) != palette(question_template[0]):
        raise ValueError("questions template palette differs from the original palette")

    sequence_files = dict(shared)
    sequence_files.update(original_files)
    question_files = dict(shared)
    question_files.update({
        "guide.md": file_snapshot(skill_root / "references/questions.md"),
        "references/visual-forms.md": file_snapshot(skill_root / "references/visual-forms.md"),
        "references/delivery.md": file_snapshot(skill_root / "references/delivery.md"),
        "assets/questions-template.html": question_template,
    })
    for files in (sequence_files, question_files):
        files["SKILL.md"] = files["guide.md"]
    return {"sequence": sequence_files, "questions": question_files}


def parse_model(value):
    model, separator, effort = value.rpartition(":")
    if not separator or not model.strip() or effort not in {"low", "medium", "high", "xhigh", "max", "ultra"}:
        raise ValueError(f"expected model:effort with a supported effort level: {value}")
    if any(character.isspace() for character in model):
        raise ValueError(f"model ID must not contain whitespace: {model}")
    return model, effort


def write_file(path, data, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)
    path.chmod(mode)


def write_tree(root, files):
    for relative, (data, mode) in files.items():
        write_file(root / relative, data, mode)


def prepare(packet, output, models, task, *, skill_root=SKILL_ROOT, original_root=None):
    packet, output, task = Path(packet).absolute(), Path(output).absolute(), Path(task).absolute()
    if output.is_symlink() or (output.exists() and (not output.is_dir() or any(output.iterdir()))):
        raise ValueError(f"output must be absent or an empty directory: {output}")
    parsed_models = [parse_model(value) for value in models]
    if not 1 <= len(parsed_models) <= 2 or len({model for model, _ in parsed_models}) != len(parsed_models):
        raise ValueError("supply one or two distinct models; each gets one run per guide")
    sources = [packet, Path(skill_root)]
    if original_root is not None:
        sources.append(Path(original_root))
    for source in sources:
        if output.resolve().is_relative_to(source.resolve()):
            raise ValueError(f"output must be outside input and skill directories: {source}")

    packet_files = tree_snapshot(packet)
    task_file = file_snapshot(task)
    if not task_file[0].strip():
        raise ValueError("task file is empty")
    inputs = {f"packet/{name}": data for name, data in packet_files.items()}
    inputs["task.md"] = task_file
    skills = skill_snapshots(skill_root, original_root)
    input_hashes = tree_hashes(inputs)
    skill_hashes = {mode: tree_hashes(files) for mode, files in skills.items()}
    cells = [(model, effort, mode) for model, effort in parsed_models for mode in skills]
    labels = list("ABCD"[:len(cells)])
    random.SystemRandom().shuffle(cells)
    random.SystemRandom().shuffle(labels)

    output.mkdir(parents=True, exist_ok=True)
    private = output / "coordinator"
    private.mkdir(mode=0o700)
    (output / "review").mkdir()
    runs = []
    for (model, effort, mode), label in zip(cells, labels):
        while True:
            run_id = secrets.token_hex(12)
            run_root = output / "runs" / run_id
            try:
                run_root.mkdir(parents=True, exist_ok=False)
                break
            except FileExistsError:
                continue
        (run_root / "input/packet").mkdir(parents=True)
        write_tree(run_root / "input", inputs)
        write_tree(run_root / "skill", skills[mode])
        write_file(run_root / "runner.md", RUNNER.encode())
        for directory in ("outputs", "files", "screenshots", "provenance"):
            (run_root / directory).mkdir()
        runs.append({
            "id": run_id, "label": label, "mode": mode, "model": model,
            "effort": effort, "status": "prepared", "cwd": str(run_root),
            "task": str(run_root / "input/task.md"),
            "guide": str(run_root / "skill/guide.md"),
            "raw_report": str(run_root / "outputs/report.html"),
            "review_report": str(output / "review" / f"{label}.html"),
            "hashes": {"input": input_hashes, "skill": skill_hashes[mode], "runner": sha256(RUNNER.encode())},
        })

    manifest = {
        "schema_version": 1, "status": "prepared",
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "startup_prompt": STARTUP_PROMPT,
        "isolation": "procedural input separation; no filesystem sandbox is created",
        "policies": {
            "flair": "disabled in copied skills only",
            "palette": "original fixed light and dark colors",
            "attribution": "preserve signed raw reports; mask signatures only in separate review copies",
            "scope": "preserve existing authorization, hooks, trust, and sandbox settings",
        },
        "sources": {
            "packet": str(packet), "task": str(task),
            "skill": str(Path(skill_root).resolve()),
            "original_verification_root": str(Path(original_root).resolve()) if original_root is not None else None,
            "packet_hashes": tree_hashes(packet_files), "task_sha256": sha256(task_file[0]),
        },
        "runs": runs,
    }
    manifest_path = private / "manifest.json"
    write_file(manifest_path, (json.dumps(manifest, indent=2) + "\n").encode())
    return manifest_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", action="append", required=True, metavar="MODEL:EFFORT")
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--original-root", type=Path,
                        help="optionally verify the retained original guide, hierarchy, and template against a backup")
    args = parser.parse_args(argv)
    try:
        path = prepare(args.packet, args.output, args.model, args.task, original_root=args.original_root)
    except (OSError, ValueError) as error:
        parser.exit(1, f"prepare-comparison: {error}\n")
    print(path)


if __name__ == "__main__":
    main()
