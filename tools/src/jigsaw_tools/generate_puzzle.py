"""Generate the current ISO week's jigsaw image and commit it.

Run from the metafunctor-data repo root. Idempotent: if this week's source.png
already exists, exits 0 without doing anything (manual workflow_dispatch is
the recovery path for a bad image; delete source.png first).
"""

from __future__ import annotations

import base64
import datetime
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import yaml
from openai import OpenAI

from .prompts import pick_prompt


def current_week_id(today: datetime.date | None = None) -> str:
    today = today or datetime.date.today()
    year, week, _ = today.isocalendar()
    return f"{year}-W{week:02d}"


def generate_image(prompt: str, model: str, base_url: str | None) -> bytes:
    if base_url:
        client = OpenAI(base_url=base_url)
    else:
        # The OpenAI SDK reads OPENAI_BASE_URL from env when no base_url
        # is passed. GitHub Actions substitutes unset vars as empty string,
        # which the SDK then tries to use as the URL and fails. Pop the env
        # var before constructing the client so the SDK uses its default.
        os.environ.pop("OPENAI_BASE_URL", None)
        client = OpenAI()
    response = client.images.generate(model=model, prompt=prompt, size="1024x1024", n=1)
    if not response.data or not response.data[0].b64_json:
        raise RuntimeError("Image API returned no b64_json")
    return base64.b64decode(response.data[0].b64_json)


def write_puzzle(repo_root: Path, week_id: str, image_bytes: bytes, prompt: str, model: str, grid_size: int, rotation: bool) -> Path:
    puzzle_dir = repo_root / "jigsaw" / week_id
    puzzle_dir.mkdir(parents=True, exist_ok=True)
    (puzzle_dir / "source.png").write_bytes(image_bytes)
    seed = hashlib.sha256(image_bytes).hexdigest()[:16]
    (puzzle_dir / "meta.yaml").write_text(yaml.safe_dump({
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "model": model,
        "prompt": prompt,
        "seed": seed,
        "grid_size": grid_size,
        "rotation": rotation,
    }))
    return puzzle_dir


def commit_and_push(repo_root: Path, puzzle_dir: Path, week_id: str, prompt: str, grid_size: int, rotation: bool) -> None:
    body = yaml.safe_dump({
        "op": "seed_puzzle",
        "week": week_id,
        "prompt": prompt,
        "grid_size": grid_size,
        "rotation": rotation,
        "v": 1,
    })
    subprocess.run(["git", "add", str(puzzle_dir.relative_to(repo_root))], cwd=repo_root, check=True)
    subprocess.run([
        "git",
        "-c", "user.name=jigsaw-cron",
        "-c", "user.email=cron@metafunctor.com",
        "commit",
        "-m", f"jigsaw: seed {week_id}",
        "-m", body,
    ], cwd=repo_root, check=True)
    subprocess.run(["git", "push"], cwd=repo_root, check=True)


GRID_SIZES = [8, 10, 12]


def pick_grid_size(week_id: str) -> int:
    """Deterministic per-week grid size from a small list."""
    digits = "".join(ch for ch in week_id if ch.isdigit())
    idx = int(digits) % len(GRID_SIZES) if digits else 0
    return GRID_SIZES[idx]


def pick_rotation_enabled(week_id: str) -> bool:
    """Half of weeks have rotation enabled."""
    digits = "".join(ch for ch in week_id if ch.isdigit())
    return (int(digits) if digits else 0) % 2 == 1


def main() -> int:
    repo_root = Path(os.environ.get("REPO_ROOT", ".")).resolve()
    week_id = os.environ.get("WEEK_ID") or current_week_id()
    if (repo_root / "jigsaw" / week_id / "source.png").exists():
        print(f"{week_id} already generated; exiting.")
        return 0
    prompt = pick_prompt(week_id)
    grid_size = pick_grid_size(week_id)
    rotation = pick_rotation_enabled(week_id)
    model = os.environ.get("OPENAI_IMAGE_MODEL") or "gpt-image-1"
    base_url = os.environ.get("OPENAI_BASE_URL") or None
    image_bytes = generate_image(prompt, model, base_url)
    puzzle_dir = write_puzzle(repo_root, week_id, image_bytes, prompt, model, grid_size, rotation)
    commit_and_push(repo_root, puzzle_dir, week_id, prompt, grid_size, rotation)
    print(f"Generated and committed {week_id} (grid {grid_size}, rotation {rotation}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
