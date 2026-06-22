"""test_setup
----------------------------------

Tests for the `skbuild.setup` function, now provided by the
scikit-build-core setuptools wrapper.
"""

from __future__ import annotations

import pathlib
import tempfile
import textwrap

import pytest
from setuptools import Distribution

from skbuild import setup as skbuild_setup
from skbuild.exceptions import SKBuildError

from . import (
    _tmpdir,
    cmake_build_dir,
    execute_setup_py,
    push_argv,
    push_dir,
    push_env,
)

TRIVIAL_CMAKELISTS = textwrap.dedent(
    """
    cmake_minimum_required(VERSION 3.15...3.26)
    project(test NONE)
    install(CODE "execute_process(
      COMMAND \\${CMAKE_COMMAND} -E sleep 0)")
    """
)


def _make_minimal_project(name: str) -> pathlib.Path:
    """Create a project directory containing a trivial ``CMakeLists.txt`` and
    an empty ``pyproject.toml`` (required by the scikit-build-core backend)."""
    tmp_dir = _tmpdir(name)
    (tmp_dir / "pyproject.toml").write_text("")
    (tmp_dir / "CMakeLists.txt").write_text(TRIVIAL_CMAKELISTS)
    return tmp_dir


def _build_lib_files(base: str = ".") -> set[str]:
    """Return the relative paths (as posix strings) of all files found under
    the setuptools build directory (``build/lib*``)."""
    files: set[str] = set()
    for lib_dir in pathlib.Path(base).glob("build/lib*"):
        files |= {path.relative_to(lib_dir).as_posix() for path in lib_dir.rglob("*") if path.is_file()}
    return files


# -----------------------------------------------------------------------------
# Wrapper behavior (no CMake build required)
# -----------------------------------------------------------------------------


def test_setup_returns_distribution():
    tmp_dir = _make_minimal_project("setup_returns_distribution")

    with push_dir(str(tmp_dir)), push_argv(["setup.py", "--name"]):
        distribution = skbuild_setup(
            name="test_setup_returns_distribution",
            version="0.0.1",
        )

    assert isinstance(distribution, Distribution)
    # The wrapper always enables the CMake build, so the distribution is
    # never pure.
    assert not distribution.is_pure()


def test_cmake_with_sdist_keyword_unsupported():
    tmp_dir = _make_minimal_project("cmake_with_sdist_unsupported")

    with push_dir(str(tmp_dir)), push_argv(["setup.py", "--name"]):
        with pytest.raises(SKBuildError, match="cmake_with_sdist not supported yet"):
            skbuild_setup(
                name="test_cmake_with_sdist",
                version="0.0.1",
                cmake_with_sdist=True,
            )


def test_cmake_install_target_keyword_unsupported():
    tmp_dir = _make_minimal_project("cmake_install_target_unsupported")

    with push_dir(str(tmp_dir)), push_argv(["setup.py", "--name"]):
        with pytest.raises(SKBuildError, match="cmake_install_target not supported yet"):
            skbuild_setup(
                name="test_cmake_install_target",
                version="0.0.1",
                cmake_install_target="install-runtime",
            )


def test_cmake_languages_keyword_warns():
    tmp_dir = _make_minimal_project("cmake_languages_warns")

    with push_dir(str(tmp_dir)), push_argv(["setup.py", "--name"]):
        with pytest.warns(UserWarning, match="cmake_languages no longer has any effect"):
            distribution = skbuild_setup(
                name="test_cmake_languages",
                version="0.0.1",
                cmake_languages=["C"],
            )

    assert isinstance(distribution, Distribution)


def test_cmake_minimum_required_version_keyword_warns():
    tmp_dir = _make_minimal_project("cmake_minimum_required_version")

    with push_dir(str(tmp_dir)), push_argv(["setup.py", "--name"]):
        with pytest.warns(UserWarning, match="Set via pyproject.toml"):
            skbuild_setup(
                name="test_cmake_minimum_required_version",
                version="0.0.1",
                cmake_minimum_required_version="3.5",
            )


def test_cmake_args_string_raises():
    tmp_dir = _make_minimal_project("cmake_args_string")

    with push_dir(str(tmp_dir)), push_argv(["setup.py", "--name"]):
        with pytest.raises(TypeError, match="cmake_args must be a list, not a string"):
            skbuild_setup(
                name="test_cmake_args_string",
                version="0.0.1",
                cmake_args="-DVAR:STRING=42",
            )


# -----------------------------------------------------------------------------
# End-to-end tests (require CMake)
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("via_env", [False, True], ids=["keyword", "env"])
def test_cmake_args_keyword(via_env, capfd):
    tmp_dir = _tmpdir("cmake_args_keyword")
    (tmp_dir / "pyproject.toml").write_text("")

    cmake_args_kwarg = "" if via_env else """cmake_args=["-DVAR:STRING=42", "-DVAR_WITH_SPACE:STRING=Hello World"],"""

    (tmp_dir / "setup.py").write_text(
        textwrap.dedent(
            f"""
        from skbuild import setup
        setup(
            name="test_cmake_args_keyword",
            version="1.2.3",
            description="a minimal example package",
            author='The scikit-build team',
            license="MIT",
            {cmake_args_kwarg}
        )
        """
        )
    )
    (tmp_dir / "CMakeLists.txt").write_text(
        textwrap.dedent(
            """
        cmake_minimum_required(VERSION 3.15...3.26)
        project(test NONE)
        message(STATUS "VAR[${VAR}]")
        message(STATUS "VAR_WITH_SPACE[${VAR_WITH_SPACE}]")
        install(CODE "execute_process(
          COMMAND \\${CMAKE_COMMAND} -E sleep 0)")
        """
        )
    )

    cmake_args_env = "-DVAR:STRING=43" if via_env else None
    with push_env(CMAKE_ARGS=cmake_args_env), execute_setup_py(tmp_dir, ["build"]):
        pass

    out, _ = capfd.readouterr()

    if via_env:
        assert "VAR[43]" in out
    else:
        assert "VAR[42]" in out
        assert "VAR_WITH_SPACE[Hello World]" in out


@pytest.mark.parametrize(
    "cmake_install_dir",
    [
        None,
        str(pathlib.Path(tempfile.gettempdir()) / "scikit-build"),
        "banana",
    ],
    ids=["default", "absolute", "banana"],
)
def test_cmake_install_dir_keyword(cmake_install_dir):
    # -------------------------------------------------------------------------
    # "SOURCE" tree layout:
    #
    # ROOT/
    #
    #     CMakeLists.txt
    #     pyproject.toml
    #     setup.py
    #
    #     apple/
    #         __init__.py
    #
    #     banana/
    #         __init__.py
    #
    # The CMakeLists.txt installs ``banana.py`` into the install root. With
    # ``cmake_install_dir='banana'``, the file belongs to the ``banana``
    # package and is copied into ``build/lib*``; without it, the file does not
    # belong to any package and becomes a setuptools data file.

    tmp_dir = _tmpdir("cmake_install_dir_keyword")
    (tmp_dir / "pyproject.toml").write_text("")

    setup_kwarg = ""
    if cmake_install_dir is not None:
        setup_kwarg = f"cmake_install_dir={cmake_install_dir!r},"

    (tmp_dir / "setup.py").write_text(
        textwrap.dedent(
            f"""
        from skbuild import setup
        setup(
            name="test_cmake_install_dir",
            version="1.2.3",
            description="a package testing use of cmake_install_dir",
            author='The scikit-build team',
            license="MIT",
            packages=['apple', 'banana'],
            {setup_kwarg}
        )
        """
        )
    )

    # Install location purposely set to "." so that we can test
    # usage of "cmake_install_dir" skbuild.setup keyword.
    (tmp_dir / "CMakeLists.txt").write_text(
        textwrap.dedent(
            """
        cmake_minimum_required(VERSION 3.15...3.26)
        project(banana NONE)
        file(WRITE "${CMAKE_BINARY_DIR}/banana.py" "")
        install(FILES "${CMAKE_BINARY_DIR}/banana.py" DESTINATION ".")
        """
        )
    )

    for package in ["apple", "banana"]:
        init_py = tmp_dir / package / "__init__.py"
        init_py.parent.mkdir(parents=True, exist_ok=True)
        init_py.touch(exist_ok=True)

    if cmake_install_dir is not None and pathlib.Path(cmake_install_dir).is_absolute():
        with pytest.raises(SystemExit, match="cmake_install_dir must be a relative path"):
            with execute_setup_py(tmp_dir, ["build"]):
                pass
        return

    with execute_setup_py(tmp_dir, ["build"]):
        build_files = _build_lib_files()
        assert "apple/__init__.py" in build_files
        assert "banana/__init__.py" in build_files

        skbuild_dir = cmake_build_dir()
        assert skbuild_dir is not None

        if cmake_install_dir == "banana":
            # The CMake-installed module belongs to the "banana" package.
            assert "banana/banana.py" in build_files
            assert (skbuild_dir / "cmake-install" / "banana" / "banana.py").exists()
        else:
            # The CMake-installed module does not belong to any package; like
            # classic scikit-build, a top-level module becomes a py_module.
            assert "banana.py" in build_files
            assert "banana/banana.py" not in build_files
            assert (skbuild_dir / "cmake-install" / "banana.py").exists()


def test_invalid_cmake_source_dir_fails():
    tmp_dir = _make_minimal_project("invalid_cmake_source_dir")

    (tmp_dir / "setup.py").write_text(
        textwrap.dedent(
            """
        from skbuild import setup
        setup(
            name="test_invalid_cmake_source_dir",
            version="1.2.3",
            description="a package with an invalid cmake_source_dir",
            author='The scikit-build team',
            license="MIT",
            cmake_source_dir='nonexistent',
        )
        """
        )
    )

    with pytest.raises(SystemExit, match="cmake_source_dir must be an existing directory"):
        with execute_setup_py(tmp_dir, ["build"]):
            pass


def test_sdist_does_not_run_cmake():
    tmp_dir = _make_minimal_project("sdist_without_cmake")

    (tmp_dir / "setup.py").write_text(
        textwrap.dedent(
            """
        from skbuild import setup
        setup(
            name="sdist_without_cmake",
            version="1.2.3",
            description="a minimal example package",
            author='The scikit-build team',
            license="MIT",
            cmake_with_sdist=False,
        )
        """
        )
    )

    with execute_setup_py(tmp_dir, ["sdist"]):
        sdists = list(pathlib.Path("dist").glob("*.tar.gz"))
        assert len(sdists) == 1
        assert cmake_build_dir() is None


@pytest.mark.parametrize("has_cmake_package", [0, 1])
@pytest.mark.parametrize("has_hybrid_package", [0, 1])
@pytest.mark.parametrize("has_pure_package", [0, 1])
@pytest.mark.parametrize("has_pure_module", [0, 1])
@pytest.mark.parametrize("with_package_base", [0, 1])
def test_setup_inputs(
    has_cmake_package,
    has_hybrid_package,
    has_pure_package,
    has_pure_module,
    with_package_base,
):
    """This tests that a project can mix packages and modules installed using
    setup.py with files installed using CMake."""

    tmp_dir = _tmpdir("test_setup_inputs")
    (tmp_dir / "pyproject.toml").write_text("")

    package_base = "to/the/base" if with_package_base else ""

    # -------------------------------------------------------------------------
    # Here is the "SOURCE" tree layout:
    #
    # ROOT/
    #
    #     pyproject.toml
    #     setup.py
    #
    #     [<base>/]
    #
    #         CMakeLists.txt
    #
    #         pureModule.py
    #
    #         cmake/
    #             __init__.py
    #
    #         hybrid/
    #             __init__.py
    #             hybrid_pure.dat
    #             hybrid_pure.py
    #
    #         pure/
    #             __init__.py
    #             pure.py
    #
    # -------------------------------------------------------------------------
    # and here is the expected "BINARY" distribution layout (build/lib*):
    #
    # The comment "CMake" or "Setuptools" indicates which tool is responsible
    # for placing the file in the build tree.
    #
    # ROOT/
    #
    #     pureModule.py              # Setuptools
    #
    #     cmake/
    #         __init__.py            # Setuptools
    #         cmake_generated.py     # CMake
    #
    #     hybrid/
    #         __init__.py            # Setuptools
    #         hybrid_cmake.py        # CMake
    #         hybrid_pure.dat        # Setuptools
    #         hybrid_pure.py         # Setuptools
    #
    #     pure/
    #         __init__.py            # Setuptools
    #         pure.py                # Setuptools
    #
    # The CMake-installed file that does not belong to any package
    # (share/test/hybrid_data.dat) becomes a setuptools data file and is
    # staged under the CMake build directory instead.

    package_dir_kwarg = f"package_dir={{'': {package_base!r}}}," if with_package_base else ""

    (tmp_dir / "setup.py").write_text(
        textwrap.dedent(
            """
        from skbuild import setup
        setup(
            name="test_hybrid_project",
            version="1.2.3",
            description=("an hybrid package mixing files installed by both "
                        "CMake and setuptools"),
            author='The scikit-build team',
            license="MIT",
            cmake_source_dir='{cmake_source_dir}',
            cmake_install_dir='{cmake_install_dir}',
            packages=[
        {c_off}    'cmake',
        {h_off}    'hybrid',
        {p_off}    'pure',
            ],
            py_modules=[
        {pm_off}   'pureModule',
            ],
            package_data={{
        {h_off}        'hybrid': ['hybrid_pure.dat'],
            }},
            {package_dir_kwarg}
        )
        """.format(
                cmake_source_dir=package_base,
                cmake_install_dir=package_base,
                package_dir_kwarg=package_dir_kwarg,
                c_off="" if has_cmake_package else "#",
                h_off="" if has_hybrid_package else "#",
                p_off="" if has_pure_package else "#",
                pm_off="" if has_pure_module else "#",
            )
        )
    )

    src_dir = tmp_dir / package_base if package_base else tmp_dir
    src_dir.mkdir(parents=True, exist_ok=True)

    (src_dir / "CMakeLists.txt").write_text(
        textwrap.dedent(
            """
        cmake_minimum_required(VERSION 3.15...3.26)
        project(hybrid NONE)
        set(build_dir ${{CMAKE_BINARY_DIR}})

        {c_off} file(WRITE ${{build_dir}}/cmake_generated.py "")
        {c_off} install(
        {c_off}     FILES ${{build_dir}}/cmake_generated.py
        {c_off}     DESTINATION cmake)

        {h_off} file(WRITE ${{build_dir}}/hybrid_cmake.py "")
        {h_off} install(
        {h_off}     FILES ${{build_dir}}/hybrid_cmake.py
        {h_off}     DESTINATION hybrid)

        file(WRITE ${{build_dir}}/hybrid_data.dat "")
        install(
            FILES ${{build_dir}}/hybrid_data.dat
            DESTINATION share/test)
        """.format(
                c_off="" if has_cmake_package else "#",
                h_off="" if has_hybrid_package else "#",
            )
        )
    )

    source_files = []
    if has_cmake_package:
        source_files += ["cmake/__init__.py"]
    if has_hybrid_package:
        source_files += ["hybrid/__init__.py", "hybrid/hybrid_pure.py", "hybrid/hybrid_pure.dat"]
    if has_pure_package:
        source_files += ["pure/__init__.py", "pure/pure.py"]
    if has_pure_module:
        source_files += ["pureModule.py"]

    for path in source_files:
        source_path = src_dir / path
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.touch(exist_ok=True)

    with execute_setup_py(tmp_dir, ["build"]):
        expected_build_files = set()
        if has_cmake_package:
            expected_build_files |= {"cmake/__init__.py", "cmake/cmake_generated.py"}
        if has_hybrid_package:
            expected_build_files |= {
                "hybrid/__init__.py",
                "hybrid/hybrid_cmake.py",
                "hybrid/hybrid_pure.dat",
                "hybrid/hybrid_pure.py",
            }
        if has_pure_package:
            expected_build_files |= {"pure/__init__.py", "pure/pure.py"}
        if has_pure_module:
            expected_build_files.add("pureModule.py")

        assert _build_lib_files() == expected_build_files

        # The CMake-installed file outside of any package is staged as a
        # setuptools data file.
        skbuild_dir = cmake_build_dir()
        assert skbuild_dir is not None
        assert (skbuild_dir / "cmake-install" / "share" / "test" / "hybrid_data.dat").exists()


@pytest.mark.parametrize("with_cmake_source_dir", [0, 1])
def test_cmake_install_into_pure_package(with_cmake_source_dir):
    # -------------------------------------------------------------------------
    # "SOURCE" tree layout:
    #
    # (1) with_cmake_source_dir == 0
    #
    # ROOT/
    #
    #     CMakeLists.txt
    #     pyproject.toml
    #     setup.py
    #
    #     fruits/
    #         __init__.py
    #
    #
    # (2) with_cmake_source_dir == 1
    #
    # ROOT/
    #
    #     pyproject.toml
    #     setup.py
    #
    #     fruits/
    #         __init__.py
    #
    #     src/
    #
    #         CMakeLists.txt
    #
    # -------------------------------------------------------------------------
    # "BINARY" distribution layout (build/lib*):
    #
    # ROOT/
    #
    #     fruits/
    #
    #         __init__.py
    #         apple.py
    #         banana.py
    #
    #             data/
    #
    #                 apple.dat
    #                 banana.dat
    #

    tmp_dir = _tmpdir("cmake_install_into_pure_package")
    (tmp_dir / "pyproject.toml").write_text("")

    cmake_source_dir = "src" if with_cmake_source_dir else ""

    (tmp_dir / "setup.py").write_text(
        textwrap.dedent(
            f"""
        from skbuild import setup
        setup(
            name="test_cmake_install_into_pure_package",
            version="1.2.3",
            description="a package testing CMake installs into a pure package",
            author='The scikit-build team',
            license="MIT",
            packages=['fruits'],
            cmake_install_dir='fruits',
            cmake_source_dir='{cmake_source_dir}',
        )
        """
        )
    )

    cmake_src_dir = tmp_dir / cmake_source_dir
    cmake_src_dir.mkdir(parents=True, exist_ok=True)
    (cmake_src_dir / "CMakeLists.txt").write_text(
        textwrap.dedent(
            """
        cmake_minimum_required(VERSION 3.15...3.26)
        project(test NONE)
        file(WRITE "${CMAKE_BINARY_DIR}/apple.py" "# apple.py")
        file(WRITE "${CMAKE_BINARY_DIR}/banana.py" "# banana.py")
        install(
            FILES
                "${CMAKE_BINARY_DIR}/apple.py"
                "${CMAKE_BINARY_DIR}/banana.py"
            DESTINATION "."
            )
        file(WRITE "${CMAKE_BINARY_DIR}/apple.dat" "# apple.dat")
        file(WRITE "${CMAKE_BINARY_DIR}/banana.dat" "# banana.dat")
        install(
            FILES
                "${CMAKE_BINARY_DIR}/apple.dat"
                "${CMAKE_BINARY_DIR}/banana.dat"
            DESTINATION "data"
            )
        """
        )
    )

    fruits_init = tmp_dir / "fruits" / "__init__.py"
    fruits_init.parent.mkdir(parents=True, exist_ok=True)
    fruits_init.touch(exist_ok=True)

    with execute_setup_py(tmp_dir, ["build"]):
        assert _build_lib_files() == {
            "fruits/__init__.py",
            "fruits/apple.py",
            "fruits/banana.py",
            "fruits/data/apple.dat",
            "fruits/data/banana.dat",
        }
