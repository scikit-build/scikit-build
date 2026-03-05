"""test_utils
------------------------

Tests for utils functions.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from skbuild.utils import (
    PythonModuleFinder,
    mkdir_p,
    push_dir,
    to_platform_path,
    to_unix_path,
)

from . import SAMPLES_DIR, list_ancestors, push_env

saved_cwd = os.getcwd()


def setup_module():
    """setup any state specific to the execution of the given module."""
    os.chdir(Path(__file__).parent)


def teardown_module():
    """teardown any state that was previously setup with a setup_module
    method.
    """
    os.chdir(saved_cwd)


def test_push_dir(tmp_path):
    old_cwd = os.getcwd()
    try:
        level1 = tmp_path / "level1"
        level1.mkdir()
        level2 = level1 / "level2"
        level2.mkdir()

        os.chdir(str(level2))
        assert Path.cwd().name == "level2"

        # No directory
        with push_dir():
            os.chdir(Path.cwd().parent)
            assert Path.cwd().name == "level1"
        assert Path.cwd().name == "level2"

        # With existing directory
        with push_dir(directory=str(Path.cwd().parent)):
            assert Path.cwd().name == "level1"
        assert Path.cwd().name == "level2"

        foo_directory = tmp_path / "foo"

        # With non existing directory
        failed = False
        try:
            with push_dir(directory=str(foo_directory)):
                pass
        except OSError:
            failed = True
        assert failed
        assert not foo_directory.is_dir()

        # With make_directory option
        with push_dir(directory=foo_directory, make_directory=True):
            assert os.getcwd() == str(foo_directory)
        assert Path.cwd().name == "level2"
        assert foo_directory.is_dir()
    finally:
        os.chdir(old_cwd)


def test_push_dir_decorator(tmp_path):
    old_cwd = os.getcwd()
    try:
        level1 = tmp_path / "level1"
        level1.mkdir()
        level2 = level1 / "level2"
        level2.mkdir()
        os.chdir(str(level2))
        assert Path.cwd().name == "level2"

        # No directory
        @push_dir()
        def test_default():
            os.chdir(Path.cwd().parent)
            assert Path.cwd().name == "level1"

        test_default()
        assert Path.cwd().name == "level2"

        # With existing directory
        @push_dir(directory=str(Path.cwd().parent))
        def test():
            assert Path.cwd().name == "level1"

        test()
        assert Path.cwd().name == "level2"

        foo_directory = tmp_path / "foo"

        # With non existing directory
        failed = False
        try:

            @push_dir(directory=str(foo_directory))
            def test():
                pass

            test()
        except OSError:
            failed = True
        assert failed
        assert not foo_directory.is_dir()

        # With make_directory option
        @push_dir(directory=foo_directory, make_directory=True)
        def test():
            assert os.getcwd() == str(foo_directory)

        test()
        assert Path.cwd().name == "level2"
        assert foo_directory.is_dir()
    finally:
        os.chdir(old_cwd)


def test_mkdir_p(tmp_path):
    assert tmp_path.is_dir()

    foo_bar_dir = tmp_path / "foo" / "bar"

    mkdir_p(foo_bar_dir)
    assert foo_bar_dir.is_dir()

    # Make sure calling function twice does not raise an exception
    mkdir_p(foo_bar_dir)
    assert foo_bar_dir.is_dir()


def test_push_env():
    assert "SKBUILD_NEW_VAR" not in os.environ

    os.environ["SKBUILD_ANOTHER_VAR"] = "abcd"
    assert "SKBUILD_ANOTHER_VAR" in os.environ

    saved_env = dict(os.environ)

    # Setting and un-setting variables can be done simultaneously
    with push_env(SKBUILD_NEW_VAR="1234", SKBUILD_ANOTHER_VAR=None):
        assert "SKBUILD_NEW_VAR" in os.environ
        assert "SKBUILD_ANOTHER_VAR" not in os.environ
        assert os.getenv("SKBUILD_NEW_VAR") == "1234"

    assert "SKBUILD_NEW_VAR" not in os.environ
    assert "SKBUILD_ANOTHER_VAR" in os.environ
    assert saved_env == dict(os.environ)

    # Trying to unset an unknown variable should be a no-op
    with push_env(SKBUILD_NOT_SET=None):
        assert saved_env == dict(os.environ)
    assert saved_env == dict(os.environ)

    # Calling without argument should be a no-op
    with push_env():
        assert saved_env == dict(os.environ)
    assert saved_env == dict(os.environ)


def test_python_module_finder():
    modules = PythonModuleFinder(["bonjour", "hello"], {}, []).find_all_modules(str(SAMPLES_DIR / "hello-cpp"))
    assert sorted(modules) == sorted(
        [
            ("bonjour", "__init__", to_platform_path("bonjour/__init__.py")),
            ("hello", "__init__", to_platform_path("hello/__init__.py")),
            ("hello", "__main__", to_platform_path("hello/__main__.py")),
        ]
    )


@pytest.mark.parametrize(
    ("input_path", "expected_path"),
    [
        (None, None),
        ("", ""),
        ("/bar/foo/baz", f"{os.sep}bar{os.sep}foo{os.sep}baz"),
        ("C:\\bar\\foo\\baz", f"C:{os.sep}bar{os.sep}foo{os.sep}baz"),
        ("C:\\bar/foo\\baz/", f"C:{os.sep}bar{os.sep}foo{os.sep}baz{os.sep}"),
    ],
)
def test_to_platform_path(input_path, expected_path):
    assert to_platform_path(input_path) == expected_path


@pytest.mark.parametrize(
    ("input_path", "expected_path"),
    [
        (None, None),
        ("", ""),
        ("/bar/foo/baz", "/bar/foo/baz"),
        ("C:\\bar\\foo\\baz", "C:/bar/foo/baz"),
        ("C:\\bar/foo\\baz/", "C:/bar/foo/baz/"),
    ],
)
def test_to_unix_path(input_path, expected_path):
    assert to_unix_path(input_path) == expected_path


@pytest.mark.parametrize(
    ("input_path", "expected_ancestors"),
    [
        ("", []),
        (".", []),
        ("part1/part2/part3/part4", ["part1/part2/part3", "part1/part2", "part1"]),
        ("part1\\part2\\part3\\part4", []),
        ("/part1/part2/part3/part4", ["/part1/part2/part3", "/part1/part2", "/part1", "/"]),
        ("C:/part1/part2/part3/part4", ["C:/part1/part2/part3", "C:/part1/part2", "C:/part1", "C:"]),
    ],
)
def test_list_ancestors(input_path, expected_ancestors):
    assert list_ancestors(input_path) == expected_ancestors
