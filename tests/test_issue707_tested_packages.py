from . import (
    project_setup_py_test,
)



def test_install_command(capfd):
    @project_setup_py_test("issue-707-nested-packages", ["install"], disable_languages_test=True)
    def build():
        pass

    build()
    capfd.readouterr()

    # Verify that both
    import hello
    hello.hello("World")
    captured = capfd.readouterr()
    assert captured.out == "Hello, World!\n"

    hello.goodbye.goodbye("World")
    captured = capfd.readouterr()
    assert captured.out == "Goodbye, World!\n"
