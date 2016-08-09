#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_command_line
----------------------------------

Tests for various command line functionality.
"""

from . import project_setup_py_test, push_dir


@project_setup_py_test(("samples", "hello"), ["--help"])
def test_help(capsys):
    out, err = capsys.readouterr()
    assert "scikit-build options" in out
    assert "--build-type" in out
    assert "Global options:" in out
    assert "usage:" in out


def test_no_command():
    with push_dir():

        @project_setup_py_test(("samples", "hello"), [""])
        def run():
            pass

        failed = False
        try:
            run()
        except SystemExit as e:
            failed = e.args[0].startswith('invalid command name')

        assert failed


def test_too_many_separators():
    with push_dir():

        @project_setup_py_test(("samples", "hello"), ["--"] * 3)
        def run():
            pass

        failed = False
        try:
            run()
        except SystemExit as e:
            failed = e.args[0].startswith('ERROR: Too many')

        assert failed
