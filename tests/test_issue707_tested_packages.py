from __future__ import annotations


def test_install_command(capfd, monkeypatch, project_setup_py_test):
    with project_setup_py_test(
        "issue-707-nested-packages", ["build_ext", "--inplace"], disable_languages_test=True
    ) as tmp_dir:
        pass

    capfd.readouterr()
    monkeypatch.syspath_prepend(tmp_dir)

    # Verify that both
    import hello_nested

    hello_nested.hello("World")
    captured = capfd.readouterr()
    assert captured.out == "Hello, World!\n"

    hello_nested.goodbye_nested.goodbye("World")
    captured = capfd.readouterr()
    assert captured.out == "Goodbye, World!\n"
