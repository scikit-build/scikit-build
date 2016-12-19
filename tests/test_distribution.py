
import os
import pytest

from path import Path

from . import initialize_git_repo_and_commit, prepare_project

DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../dist'))

# Test if package can be imported to allow testing on
# conda-forge where ``pytest-virtualenv`` is not available.
try:
    import pytest_virtualenv  # noqa: F401
    HAS_PYTEST_VIRTUALENV = True
except ImportError:
    HAS_PYTEST_VIRTUALENV = False


@pytest.mark.skipif(not HAS_PYTEST_VIRTUALENV,
                    reason="pytest_virtualenv not available. See #228")
def test_source_distribution(virtualenv):
    sdists = Path(DIST_DIR).files(pattern="*.tar.gz")
    if not sdists:
        pytest.skip("no source distribution available")
    assert len(sdists) == 1

    virtualenv.run("pip install %s" % sdists[0])
    assert "scikit-build" in virtualenv.installed_packages()

    prepare_project("hello", virtualenv.workspace, force=True)
    initialize_git_repo_and_commit(virtualenv.workspace, verbose=False)

    virtualenv.run("python setup.py bdist_wheel")


@pytest.mark.skipif(not HAS_PYTEST_VIRTUALENV,
                    reason="pytest_virtualenv not available. See #228")
def test_wheel(virtualenv):
    wheels = Path(DIST_DIR).files(pattern="*.whl")
    if not wheels:
        pytest.skip("no wheel available")
    assert len(wheels) == 1

    virtualenv.run("pip install %s" % wheels[0])
    assert "scikit-build" in virtualenv.installed_packages()

    prepare_project("hello", virtualenv.workspace, force=True)
    initialize_git_repo_and_commit(virtualenv.workspace, verbose=False)

    virtualenv.run("python setup.py bdist_wheel")
