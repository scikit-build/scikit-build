import goodbye
import hello


def test_hello(capfd):
    hello.hello("World")
    captured = capfd.readouterr()
    assert captured.out == "Hello, World!\n"


def test_elevation():
    assert hello.elevation() == 21463


def test_goodbye(capfd):
    goodbye.goodbye("World")
    captured = capfd.readouterr()
    assert captured.out == "Goodbye, World!\n"


def test_elevation_g():
    assert goodbye.elevation_g() == 21463
