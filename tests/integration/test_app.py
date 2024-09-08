import subprocess


def test__app__main() -> None:
    try:
        out = subprocess.run(["python", "-m", "autoarena"], timeout=5, capture_output=True)
        assert out.returncode == 0
    except subprocess.TimeoutExpired as e:
        assert e.stderr is not None
        assert "AutoArena ready" in e.stderr.decode("utf-8")
    except Exception as e:
        raise e
