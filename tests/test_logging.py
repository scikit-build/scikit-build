from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest

from skbuild.utils import distribution_hide_listing

setuptools_logging = pytest.importorskip("setuptools.logging")


def test_hide_listing(caplog):
    setuptools_logging.configure()

    distribution = SimpleNamespace()
    distribution.hide_listing = True

    with distribution_hide_listing(distribution):  # type: ignore[arg-type]
        logging.getLogger("wheel").info("This is hidden")

    assert "This is hidden" not in caplog.text


def test_no_hide_listing(caplog):
    setuptools_logging.configure()

    distribution = SimpleNamespace()
    distribution.hide_listing = False

    with distribution_hide_listing(distribution):  # type: ignore[arg-type]
        logging.getLogger("wheel").info("This is not hidden")

    assert "This is not hidden" in caplog.text
