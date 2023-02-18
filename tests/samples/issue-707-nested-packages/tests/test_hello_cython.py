from hello import goodbye
import hello


def test_hello(capfd):
    hello.hello("World")
    captured = capfd.readouterr()
    assert captured.out == "Hello, World!\n"


def test_goodbye(capfd):
    goodbye.goodbye("World")
    captured = capfd.readouterr()
    assert captured.out == "Goodbye, World!\n"
