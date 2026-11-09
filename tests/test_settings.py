from claude_meter.settings import Settings


def test_defaults_when_file_missing(tmp_path):
    assert Settings.load(tmp_path / "settings.json") == Settings(show_in_dock=True)


def test_round_trip(tmp_path):
    path = tmp_path / "nested" / "settings.json"
    Settings(show_in_dock=False).save(path)
    assert Settings.load(path) == Settings(show_in_dock=False)


def test_garbage_file_yields_defaults(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text("not json")
    assert Settings.load(path) == Settings()
    path.write_text("[1, 2]")
    assert Settings.load(path) == Settings()


def test_wrong_type_is_ignored(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text('{"show_in_dock": "no", "unknown": 1}')
    assert Settings.load(path).show_in_dock is True
