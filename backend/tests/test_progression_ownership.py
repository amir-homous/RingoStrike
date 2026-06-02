from pathlib import Path

from services.stats_service import build_level_progress


BACKEND_DIR = Path(__file__).resolve().parents[1]


def test_level_progress_bundle_uses_canonical_helpers():
    assert build_level_progress(0) == {
        "xp": 0,
        "level": 1,
        "next_level_xp": 100,
        "progress_percent": 0,
    }

    assert build_level_progress(100) == {
        "xp": 100,
        "level": 2,
        "next_level_xp": 283,
        "progress_percent": 0,
    }


def test_progression_level_calculation_is_not_duplicated_in_services():
    offenders = []

    for path in (BACKEND_DIR / "services").glob("*.py"):
        if path.name == "stats_service.py":
            continue

        source = path.read_text()

        forbidden_fragments = [
            "total_xp // 100",
            "total_points // 100",
            "level * 100",
            "def _level_bundle",
        ]

        for fragment in forbidden_fragments:
            if fragment in source:
                offenders.append(f"{path.name}: {fragment}")

    assert offenders == []
