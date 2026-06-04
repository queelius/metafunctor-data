import datetime
import hashlib
import subprocess
from pathlib import Path

import yaml

from jigsaw_tools.generate_puzzle import (
    current_week_id,
    write_puzzle,
    commit_and_push,
    build_seed_event,
    pick_grid_size,
    pick_rotation_enabled,
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
    puzzle_dir = write_puzzle(tmp_path, "2026-W17", image_bytes, "a prompt", "gpt-image-1", 8, False)
    assert (puzzle_dir / "source.png").read_bytes() == image_bytes
    meta = yaml.safe_load((puzzle_dir / "meta.yaml").read_text())
    assert meta["model"] == "gpt-image-1"
    assert meta["prompt"] == "a prompt"
    assert meta["seed"] == hashlib.sha256(image_bytes).hexdigest()[:16]
    assert meta["grid_size"] == 8
    assert meta["rotation"] is False


def test_commit_and_push_invokes_git(tmp_path: Path, monkeypatch):
    calls: list[list[str]] = []
    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        class R: returncode = 0
        return R()
    monkeypatch.setattr(subprocess, "run", fake_run)
    puzzle_dir = tmp_path / "jigsaw" / "2026-W17"
    puzzle_dir.mkdir(parents=True)
    commit_and_push(tmp_path, puzzle_dir, "2026-W17", "a prompt", 8, False)
    assert any(call[0] == "git" and "add" in call for call in calls)
    assert any(call[0] == "git" and "commit" in call for call in calls)
    assert any(call[0] == "git" and "push" in call for call in calls)


def test_seed_event_has_required_envelope():
    ev = build_seed_event("2026-W21", "a quiet harbor", 8, False)
    assert ev["op"] == "seed_puzzle"
    assert ev["actor"] == "jigsaw-cron"
    assert ev["ts"].endswith("Z")
    assert ev["v"] == 1


def test_pick_grid_size_deterministic_per_week():
    a = pick_grid_size("2026-W17")
    b = pick_grid_size("2026-W17")
    assert a == b
    assert a in [8, 10, 12]


def test_pick_grid_size_varies_across_weeks():
    sizes = [pick_grid_size(f"2026-W{i:02d}") for i in range(1, 13)]
    assert len(set(sizes)) > 1


def test_pick_rotation_enabled_deterministic():
    a = pick_rotation_enabled("2026-W17")
    b = pick_rotation_enabled("2026-W17")
    assert a == b
    assert isinstance(a, bool)
