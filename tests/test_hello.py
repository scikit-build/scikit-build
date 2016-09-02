#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os

from skbuild.cmaker import SKBUILD_DIR


"""test_hello
----------------------------------

Tries to build and test the `hello` sample project.
"""

from . import project_setup_py_test, push_dir


def test_hello_builds():
    with push_dir():

        @project_setup_py_test(("samples", "hello"), ["build"],
                               clear_cache=True)
        def run():
            pass

        # Check that a project can be build twice in a row
        # See issue scikit-build#120
        run()
        run()


# @project_setup_py_test(("samples", "hello"), ["test"])
# def test_hello_works():
#     pass


@project_setup_py_test(("samples", "hello"), ["sdist"])
def test_hello_sdist():
    sdists_tar = glob.glob('dist/*.tar.gz')
    sdists_zip = glob.glob('dist/*.zip')
    assert sdists_tar or sdists_zip


@project_setup_py_test(("samples", "hello"), ["bdist_wheel"])
def test_hello_wheel():
    whls = glob.glob('dist/*.whl')
    assert len(whls) == 1
    assert not whls[0].endswith('-none-any.whl')


def test_hello_clean(capfd):
    with push_dir():

        skbuild_dir = os.path.join("tests", "samples", "hello", SKBUILD_DIR)

        @project_setup_py_test(("samples", "hello"), ["build"],
                               clear_cache=True)
        def run_build():
            pass

        run_build()

        assert os.path.exists(skbuild_dir)

        # XXX Since using capfd.disabled() context manager prevents
        # the output from being captured atfer it exits, we display
        # a separator allowing to differentiate the build and clean output.
        print("<<-->>")

        @project_setup_py_test(("samples", "hello"), ["clean"])
        def run_clean():
            pass

        run_clean()

        assert not os.path.exists(skbuild_dir)

        build_out, clean_out = capfd.readouterr()[0].split('<<-->>')
        assert 'Build files have been written to' in build_out
        assert 'Build files have been written to' not in clean_out
