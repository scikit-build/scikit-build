import pytest

from skbuild.utils import distribution_hide_listing, distutils_log

setuptools_logging = pytest.importorskip("setuptools.logging")


class SimpleNamespace(object):
    pass


def test_hide_listing(caplog):
    setuptools_logging.configure()

    distribution = SimpleNamespace()
    distribution.hide_listing = True

    with distribution_hide_listing(distribution):
        distutils_log.info("This is hidden")

    assert "This is hidden" not in caplog.text


def test_no_hide_listing(caplog):
    setuptools_logging.configure()

    distribution = SimpleNamespace()
    distribution.hide_listing = False

    with distribution_hide_listing(distribution):
        distutils_log.info("This is not hidden")

    assert "This is not hidden" in caplog.text
