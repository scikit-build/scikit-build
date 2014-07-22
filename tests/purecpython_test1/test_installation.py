import os
import sys
import subprocess

from nose.tools import raises


def test_install():
    """Verify that pip installs the module with our wrapped distutils.setup call."""
    # backup our current dir
    backup_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    status = subprocess.check_call(["pip", "install", ".", ])
    os.chdir(backup_dir)
    assert(status == 0)


def test_import():
    """Verify import of libtest1."""
    import test1.test1


def test_test123():
    """Verify "test123" the method from the CPython extension."""
    from test1.test1 import test123
    assert(test123() == 123)


@raises(ImportError)
def test_cleanup():
    """Verify that the module is cleanly removed by pip"""
    status = subprocess.check_call(["pip", "uninstall", "-y", "test1"])
    import test1.test1
    reload(test1.test1)
