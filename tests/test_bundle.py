import os
import plistlib
import subprocess
import sys

from claude_meter import bundle


def test_build_creates_a_self_describing_bundle(tmp_path):
    app = bundle.build(tmp_path, venv_python=tmp_path / "venv" / "bin" / "python")

    assert app == tmp_path / "Claude Meter.app"
    with open(app / "Contents" / "Info.plist", "rb") as fh:
        info = plistlib.load(fh)
    assert info["CFBundleName"] == "Claude Meter"
    assert info["CFBundleIdentifier"] == "com.github.aki77.claude-meter"
    assert info["CFBundleExecutable"] == "claude-meter"
    assert info["LSUIElement"] is True
    assert (app / "Contents" / "Resources" / "AppIcon.icns").stat().st_size > 0

    interpreter = app / "Contents" / "MacOS" / "Claude Meter"
    assert interpreter.is_symlink()
    assert interpreter.resolve().is_file()

    launcher = app / "Contents" / "MacOS" / "claude-meter"
    assert os.access(launcher, os.X_OK)
    text = launcher.read_text()
    assert str(tmp_path / "venv" / "bin" / "python") in text
    assert "-m claude_meter" in text


def test_build_replaces_an_existing_bundle(tmp_path):
    stale = tmp_path / "Claude Meter.app" / "Contents" / "stale"
    stale.mkdir(parents=True)
    bundle.build(tmp_path)
    assert not stale.exists()


def test_interpreter_binary_bypasses_the_framework_stub():
    binary = bundle.interpreter_binary()
    assert binary.is_file()
    assert not binary.is_symlink()
    # The interpreter run through the bundle still behaves as this venv's python.
    result = subprocess.run(
        [str(binary), "-c", "import sys; print(sys.prefix)"],
        env={**os.environ, "__PYVENV_LAUNCHER__": sys.executable},
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == sys.prefix
