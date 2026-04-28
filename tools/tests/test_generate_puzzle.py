import datetime
import hashlib
import subprocess
from pathlib import Path

import yaml

from jigsaw_tools.generate_puzzle import (
    current_week_id,
    write_puzzle,
    commit_and_push,
)
from jigsaw_tools.prompts import PROMPTS, pick_prompt


def test_current_week_id_format():
    wid = current_week_id(datetime.date(2026, 4, 27))
    assert wid == "2026-W18"


def test_pick_prompt_deterministic_per_week_id():
    a = pick_prompt("2026-W17")
    b = pick_prompt("2026-W17")
    assert a == b
    assert a in PROMPTS


def test_pick_prompt_varies_across_weeks():
    weeks = [pick_prompt(f"2026-W{i:02d}") for i in range(1, 11)]
    assert len(set(weeks)) > 1


def test_write_puzzle_creates_dir_and_files(tmp_path: Path):
    image_bytes = b"\x89PNG\r\n\x1a\n" + b"fakepngdata" * 100
    puzzle_dir = write_puzzle(tmp_path, "2026-W17", image_bytes, "a prompt", "gpt-image-1")
    assert (puzzle_dir / "source.png").read_bytes() == image_bytes
    meta = yaml.safe_load((puzzle_dir / "meta.yaml").read_text())
    assert meta["model"] == "gpt-image-1"
    assert meta["prompt"] == "a prompt"
    assert meta["seed"] == hashlib.sha256(image_bytes).hexdigest()[:16]


def test_commit_and_push_invokes_git(tmp_path: Path, monkeypatch):
    calls: list[list[str]] = []
    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        class R: returncode = 0
        return R()
    monkeypatch.setattr(subprocess, "run", fake_run)
    puzzle_dir = tmp_path / "jigsaw" / "2026-W17"
    puzzle_dir.mkdir(parents=True)
    commit_and_push(tmp_path, puzzle_dir, "2026-W17", "a prompt")
    assert any(call[0] == "git" and "add" in call for call in calls)
    assert any(call[0] == "git" and "commit" in call for call in calls)
    assert any(call[0] == "git" and "push" in call for call in calls)
