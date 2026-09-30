"""Default skill vocabulary for a provider's registry.

Derived (not duplicated) from catalog.seed_data — the union of every skill the
default service catalog requires. One source of truth: when the draft changes,
both seeds follow. Nothing invented here that the catalog doesn't reference.
"""

from __future__ import annotations

from catalog.seed_data import SERVICES


def _default_skills() -> list[str]:
    names: set[str] = set()
    for row in SERVICES:
        for skill_name, _min_level in row["skills"]:
            names.add(skill_name)
    return sorted(names)


DEFAULT_SKILLS: list[str] = _default_skills()
