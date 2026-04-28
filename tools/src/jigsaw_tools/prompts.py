"""Rotating prompt list for weekly puzzle generation.

Add new prompts at the end. The cron picks deterministically based on week_id
so the same week id always produces the same prompt. Edit prompts via PR;
no admin UI in V1.
"""

PROMPTS: list[str] = [
    "An impressionist landscape at dawn over a quiet meadow, oil-painting style, soft lightfall through low fog, no text",
    "A cyberpunk alleyway with neon kanji signs, raining, reflective puddles, no people, no text",
    "An art-nouveau botanical illustration of a fictional flower with vines and gold accents, no text",
    "A retro 1970s travel poster of an imagined coastal city, flat colors, geometric shapes, no text",
    "A storybook watercolor of a small wooden house on a hill at twilight, fireflies, no text",
    "A minimalist Japanese garden scene with raked sand, three stones, a small bridge, ink-wash style, no text",
    "A hard-edged modernist abstract painting in saturated reds, blues, and ochres, no text",
    "An underwater coral reef with bioluminescent fish and a single shipwreck silhouette, no text",
    "A dense pine forest in winter at golden hour, painterly, low angle, no text",
    "A high-altitude photograph of farmland geometry, square fields in patchwork, no text",
]


def pick_prompt(week_id: str) -> str:
    """Deterministic per-week-id selection from PROMPTS."""
    digits = "".join(ch for ch in week_id if ch.isdigit())
    idx = int(digits) % len(PROMPTS) if digits else 0
    return PROMPTS[idx]
