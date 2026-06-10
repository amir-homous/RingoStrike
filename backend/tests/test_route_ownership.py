from collections import defaultdict


def test_active_routes_do_not_duplicate_method_path_ownership(client):
    app = client.application
    ownership = defaultdict(list)

    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue

        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            ownership[(method, rule.rule)].append(rule.endpoint)

    duplicates = {
        f"{method} {path}": endpoints
        for (method, path), endpoints in ownership.items()
        if len(endpoints) > 1
    }

    assert duplicates == {}


def test_canonical_route_owners_remain_registered(client):
    app = client.application

    expected = {
        ("GET", "/me/stats"): "stats_bp.me_stats",
        (
            "GET",
            "/me/enrollments/<int:enrollment_id>/leaderboard",
        ): "leaderboard_bp.enrollment_leaderboard_route",
        (
            "GET",
            "/api/public/profile/<username>",
        ): "public_profile_bp.public_profile",
        (
            "GET",
            "/me/ringo/today",
        ): "mission_bp.today_ringo_guidance_route",
        (
            "GET",
            "/debug/sqlite/schema/<table>",
        ): "debug_bp.debug_sqlite_schema",
    }

    actual = {}

    for rule in app.url_map.iter_rules():
        for method in rule.methods - {"HEAD", "OPTIONS"}:
            actual[(method, rule.rule)] = rule.endpoint

    for key, endpoint in expected.items():
        assert actual[key] == endpoint
