#!/usr/bin/env python

"""test_setup
----------------------------------

Tests for `skbuild.setup` function.
"""

import os
import pprint
import sys
import textwrap
from unittest.mock import patch

import py.path
import pytest
from setuptools import Distribution as setuptool_Distribution
from distutils.core import Distribution as distutils_Distribution

from skbuild import setup as skbuild_setup
from skbuild.constants import CMAKE_INSTALL_DIR, SKBUILD_DIR
from skbuild.exceptions import SKBuildError
from skbuild.platform_specifics import get_platform
from skbuild.setuptools_wrap import strip_package
from skbuild.utils import push_dir, to_platform_path

from . import (
    _tmpdir,
    execute_setup_py,
    initialize_git_repo_and_commit,
    is_site_reachable,
    push_argv,
)


@pytest.mark.parametrize("distribution_type", ["unknown", "py_modules", "packages", "skbuild"])
def test_distribution_is_pure(distribution_type, tmpdir):

    skbuild_setup_kwargs = {}

    if distribution_type == "unknown":
        is_pure = False

    elif distribution_type == "py_modules":
        is_pure = True
        hello_py = tmpdir.join("hello.py")
        hello_py.write("")
        skbuild_setup_kwargs["py_modules"] = ["hello"]

    elif distribution_type == "packages":
        is_pure = True
        init_py = tmpdir.mkdir("hello").join("__init__.py")
        init_py.write("")
        skbuild_setup_kwargs["packages"] = ["hello"]

    elif distribution_type == "skbuild":
        is_pure = False
        cmakelists_txt = tmpdir.join("CMakeLists.txt")
        cmakelists_txt.write(
            """
            cmake_minimum_required(VERSION 3.5.0)
            project(test NONE)
            install(CODE "execute_process(
              COMMAND \\${CMAKE_COMMAND} -E sleep 0)")
            """
        )
    else:
        raise Exception(f"Unknown distribution_type: {distribution_type}")

    platform = get_platform()
    original_write_test_cmakelist = platform.write_test_cmakelist

    def write_test_cmakelist_no_languages(_self, _languages):
        original_write_test_cmakelist([])

    with patch.object(type(platform), "write_test_cmakelist", new=write_test_cmakelist_no_languages):

        with push_dir(str(tmpdir)), push_argv(["setup.py", "build"]):
            distribution = skbuild_setup(
                name="test",
                version="0.0.1",
                description="test object returned by setup function",
                author="The scikit-build team",
                license="MIT",
                **skbuild_setup_kwargs,
            )
            assert issubclass(distribution.__class__, (distutils_Distribution, setuptool_Distribution))
            assert is_pure == distribution.is_pure()


@pytest.mark.parametrize("cmake_args", [[], ["--", "-DVAR:STRING=43", "-DVAR_WITH_SPACE:STRING=Ciao Mondo"]])
def test_cmake_args_keyword(cmake_args, capfd):
    tmp_dir = _tmpdir("cmake_args_keyword")

    tmp_dir.join("setup.py").write(
        textwrap.dedent(
            """
        from skbuild import setup
        setup(
            name="test_cmake_args_keyword",
            version="1.2.3",
            description="a minimal example package",
            author='The scikit-build team',
            license="MIT",
            cmake_args=[
                "-DVAR:STRING=42",
                "-DVAR_WITH_SPACE:STRING=Hello World"
            ]

        )
        """
        )
    )
    tmp_dir.join("CMakeLists.txt").write(
        textwrap.dedent(
            """
        cmake_minimum_required(VERSION 3.5.0)
        project(test NONE)
        message(STATUS "VAR[${VAR}]")
        message(STATUS "VAR_WITH_SPACE[${VAR_WITH_SPACE}]")
        install(CODE "execute_process(
          COMMAND \\${CMAKE_COMMAND} -E sleep 0)")
        """
        )
    )

    with execute_setup_py(tmp_dir, ["build"] + cmake_args, disable_languages_test=True):
        pass

    out, _ = capfd.readouterr()

    if not cmake_args:
        assert "VAR[42]" in out
        assert "VAR_WITH_SPACE[Hello World]" in out
    else:
        assert "VAR[43]" in out
        assert "VAR_WITH_SPACE[Ciao Mondo]" in out


@pytest.mark.parametrize(
    "cmake_install_dir, expected_failed, error_code_type",
    (
        (None, True, str),
        ("", True, str),
        (str(py.path.local.get_temproot().join("scikit-build")), True, SKBuildError),
        ("banana", False, str),
    ),
)
def test_cmake_install_dir_keyword(cmake_install_dir, expected_failed, error_code_type, capsys, caplog):

    # -------------------------------------------------------------------------
    # "SOURCE" tree layout:
    #
    # ROOT/
    #
    #     CMakeLists.txt
    #     setup.py
    #
    #     apple/
    #         __init__.py
    #
    # -------------------------------------------------------------------------
    # "BINARY" distribution layout
    #
    # ROOT/
    #
    #     apple/
    #         __init__.py
    #

    tmp_dir = _tmpdir("cmake_install_dir_keyword")

    setup_kwarg = ""
    if cmake_install_dir is not None:
        setup_kwarg = f"cmake_install_dir={str(cmake_install_dir)!r}"

    tmp_dir.join("setup.py").write(
        textwrap.dedent(
            """
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
        """.format(
                setup_kwarg=setup_kwarg
            )
        )
    )

    # Install location purposely set to "." so that we can test
    # usage of "cmake_install_dir" skbuild.setup keyword.
    tmp_dir.join("CMakeLists.txt").write(
        textwrap.dedent(
            """
        cmake_minimum_required(VERSION 3.5.0)
        project(banana NONE)
        file(WRITE "${CMAKE_BINARY_DIR}/__init__.py" "")
        install(FILES "${CMAKE_BINARY_DIR}/__init__.py" DESTINATION ".")
        """
        )
    )

    tmp_dir.ensure("apple", "__init__.py")

    failed = False
    message = ""
    try:
        with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
            pass
    except SystemExit as e:
        # Error is not of type SKBuildError, it is expected to be
        # raised by distutils.core.setup
        failed = isinstance(e.code, error_code_type)
        message = str(e)

    out, _ = capsys.readouterr()
    out += caplog.text

    assert failed == expected_failed
    if failed:
        if error_code_type == str:
            assert message == "error: package directory " "'{}' does not exist".format(
                os.path.join(CMAKE_INSTALL_DIR(), "banana")
            )
        else:
            assert message.strip().startswith("setup parameter 'cmake_install_dir' " "is set to an absolute path.")
    else:
        init_py = to_platform_path(f"{CMAKE_INSTALL_DIR()}/banana/__init__.py")
        assert f"copying {init_py}" in out


@pytest.mark.parametrize("cmake_with_sdist", [True, False])
def test_cmake_with_sdist_keyword(cmake_with_sdist, capfd):
    tmp_dir = _tmpdir("cmake_with_sdist")

    tmp_dir.join("setup.py").write(
        textwrap.dedent(
            """
        from skbuild import setup
        setup(
            name="cmake_with_sdist_keyword",
            version="1.2.3",
            description="a minimal example package",
            author='The scikit-build team',
            license="MIT",
            cmake_with_sdist={cmake_with_sdist}
        )
        """.format(
                cmake_with_sdist=cmake_with_sdist
            )
        )
    )
    tmp_dir.join("CMakeLists.txt").write(
        textwrap.dedent(
            """
        cmake_minimum_required(VERSION 3.5.0)
        project(test NONE)
        install(CODE "execute_process(
          COMMAND \\${CMAKE_COMMAND} -E sleep 0)")
        """
        )
    )

    initialize_git_repo_and_commit(tmp_dir)

    with execute_setup_py(tmp_dir, ["sdist"], disable_languages_test=True):
        pass

    out, _ = capfd.readouterr()

    if cmake_with_sdist:
        assert "Generating done" in out
    else:
        assert "Generating done" not in out


def test_cmake_minimum_required_version_keyword():
    tmp_dir = _tmpdir("cmake_minimum_required_version")

    tmp_dir.join("setup.py").write(
        textwrap.dedent(
            """
        from skbuild import setup
        setup(
            name="cmake_with_sdist_keyword",
            version="1.2.3",
            description="a minimal example package",
            author='The scikit-build team',
            license="MIT",
            cmake_minimum_required_version='99.98.97'
        )
        """
        )
    )
    tmp_dir.join("CMakeLists.txt").write(
        textwrap.dedent(
            """
        cmake_minimum_required(VERSION 3.5.0)
        project(test NONE)
        install(CODE "execute_process(
          COMMAND \\${CMAKE_COMMAND} -E sleep 0)")
        """
        )
    )

    try:
        with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
            pass
    except SystemExit as e:
        # Error is not of type SKBuildError, it is expected to be
        # raised by distutils.core.setup
        failed = isinstance(e.code, SKBuildError)
        message = str(e)
        assert failed
        assert "CMake version 99.98.97 or higher is required." in message


@pytest.mark.deprecated
@pytest.mark.filterwarnings("ignore:setuptools.installer is deprecated:Warning")
@pytest.mark.skipif(
    os.environ.get("CONDA_BUILD", "0") == "1",
    reason="running tests expecting network connection in Conda is not possible. "
    "See https://github.com/conda/conda/issues/508",
)
@pytest.mark.skipif(not is_site_reachable("https://pypi.org/simple/cmake/"), reason="pypi.org website not reachable")
@pytest.mark.xfail(
    sys.platform.startswith("cygwin"), strict=False, reason="Cygwin needs a release of scikit-build first"
)
def test_setup_requires_keyword_include_cmake(mocker, capsys):

    mock_setup = mocker.patch("skbuild.setuptools_wrap.setuptools.setup")

    tmp_dir = _tmpdir("setup_requires_keyword_include_cmake")

    setup_requires = ["cmake>=3.10"]

    tmp_dir.join("setup.py").write(
        textwrap.dedent(
            """
        from skbuild import setup
        setup(
            name="cmake_with_sdist_keyword",
            version="1.2.3",
            description="a minimal example package",
            author='The scikit-build team',
            license="MIT",
            setup_requires=[{setup_requires}]
        )
        """.format(
                setup_requires=",".join(["'%s'" % package for package in setup_requires])
            )
        )
    )
    tmp_dir.join("CMakeLists.txt").write(
        textwrap.dedent(
            """
        cmake_minimum_required(VERSION 3.5.0)
        project(test NONE)
        install(CODE "execute_process(
          COMMAND \\${CMAKE_COMMAND} -E sleep 0)")
        """
        )
    )

    with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
        assert mock_setup.call_count == 1
        setup_kw = mock_setup.call_args[1]
        assert setup_kw["setup_requires"] == setup_requires

        import cmake

        out, _ = capsys.readouterr()
        if "Searching for cmake>=3.10" in out:
            assert cmake.__file__.lower().startswith(str(tmp_dir).lower())


@pytest.mark.parametrize("distribution_type", ("pure", "skbuild"))
def test_script_keyword(distribution_type, capsys, caplog):

    # -------------------------------------------------------------------------
    #
    # "SOURCE" tree layout for "pure" distribution:
    #
    # ROOT/
    #     setup.py
    #     foo.py
    #     bar.py
    #
    # "SOURCE" tree layout for "pure" distribution:
    #
    # ROOT/
    #     setup.py
    #     CMakeLists.txt
    #
    # -------------------------------------------------------------------------
    # "BINARY" distribution layout is identical for both
    #
    # ROOT/
    #     foo.py
    #     bar.py
    #

    tmp_dir = _tmpdir("script_keyword")

    tmp_dir.join("setup.py").write(
        textwrap.dedent(
            """
        from skbuild import setup
        setup(
            name="test_script_keyword",
            version="1.2.3",
            description="a package testing use of script keyword",
            author='The scikit-build team',
            license="MIT",
            scripts=['foo.py', 'bar.py'],
            packages=[],
        )
        """
        )
    )

    if distribution_type == "skbuild":
        tmp_dir.join("CMakeLists.txt").write(
            textwrap.dedent(
                """
            cmake_minimum_required(VERSION 3.5.0)
            project(foo NONE)
            file(WRITE "${CMAKE_BINARY_DIR}/foo.py" "# foo.py")
            file(WRITE "${CMAKE_BINARY_DIR}/bar.py" "# bar.py")
            install(
                FILES
                    "${CMAKE_BINARY_DIR}/foo.py"
                    "${CMAKE_BINARY_DIR}/bar.py"
                DESTINATION "."
                )
            """
            )
        )

        messages = [
            "copying {}/{}.py -> " "{}/setuptools/scripts-".format(CMAKE_INSTALL_DIR(), module, SKBUILD_DIR())
            for module in ["foo", "bar"]
        ]

    elif distribution_type == "pure":
        tmp_dir.join("foo.py").write("# foo.py")
        tmp_dir.join("bar.py").write("# bar.py")

        messages = [
            "copying {}.py -> " "{}/setuptools/scripts-".format(module, SKBUILD_DIR()) for module in ["foo", "bar"]
        ]

    with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
        pass

    out, _ = capsys.readouterr()
    out += caplog.text
    for message in messages:
        assert to_platform_path(message) in out


@pytest.mark.parametrize("distribution_type", ("pure", "skbuild"))
def test_py_modules_keyword(distribution_type, capsys, caplog):

    # -------------------------------------------------------------------------
    #
    # "SOURCE" tree layout for "pure" distribution:
    #
    # ROOT/
    #     setup.py
    #     foo.py
    #     bar.py
    #
    # "SOURCE" tree layout for "skbuild" distribution:
    #
    # ROOT/
    #     setup.py
    #     CMakeLists.txt
    #
    # -------------------------------------------------------------------------
    # "BINARY" distribution layout is identical for both
    #
    # ROOT/
    #     foo.py
    #     bar.py
    #

    tmp_dir = _tmpdir("py_modules_keyword")

    tmp_dir.join("setup.py").write(
        textwrap.dedent(
            """
        from skbuild import setup
        setup(
            name="test_py_modules_keyword",
            version="1.2.3",
            description="a package testing use of py_modules keyword",
            author='The scikit-build team',
            license="MIT",
            py_modules=['foo', 'bar']
        )
        """
        )
    )

    if distribution_type == "skbuild":
        tmp_dir.join("CMakeLists.txt").write(
            textwrap.dedent(
                """
            cmake_minimum_required(VERSION 3.5.0)
            project(foobar NONE)
            file(WRITE "${CMAKE_BINARY_DIR}/foo.py" "# foo.py")
            file(WRITE "${CMAKE_BINARY_DIR}/bar.py" "# bar.py")
            install(
                FILES
                    "${CMAKE_BINARY_DIR}/foo.py"
                    "${CMAKE_BINARY_DIR}/bar.py"
                DESTINATION "."
                )
            """
            )
        )

        messages = [
            "copying {}/{}.py -> " "{}/setuptools/lib".format(CMAKE_INSTALL_DIR(), module, SKBUILD_DIR())
            for module in ["foo", "bar"]
        ]

    elif distribution_type == "pure":
        tmp_dir.join("foo.py").write("# foo.py")
        tmp_dir.join("bar.py").write("# bar.py")

        messages = ["copying {}.py -> " "{}/setuptools/lib".format(module, SKBUILD_DIR()) for module in ["foo", "bar"]]

    with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
        pass

    out, _ = capsys.readouterr()
    out += caplog.text
    for message in messages:
        assert to_platform_path(message) in out


@pytest.mark.parametrize(
    "package_parts, module_file, expected",
    [
        ([], "", ""),
        ([""], "file.py", "file.py"),
        ([], "foo/file.py", "foo/file.py"),
        (["foo"], "", ""),
        (["foo"], "", ""),
        (["foo"], "foo/file.py", "file.py"),
        (["foo"], "foo\\file.py", "file.py"),
        (["foo", "bar"], "foo/file.py", "foo/file.py"),
        (["foo", "bar"], "foo/bar/file.py", "file.py"),
        (["foo", "bar"], "foo/bar/baz/file.py", "baz/file.py"),
        (["foo"], "/foo/file.py", "/foo/file.py"),
    ],
)
def test_strip_package(package_parts, module_file, expected):
    assert strip_package(package_parts, module_file) == expected


@pytest.mark.parametrize("has_cmake_package", [0, 1])  # noqa: C901
@pytest.mark.parametrize("has_cmake_module", [0, 1])
@pytest.mark.parametrize("has_hybrid_package", [0, 1])
@pytest.mark.parametrize("has_pure_package", [0, 1])
@pytest.mark.parametrize("has_pure_module", [0, 1])
@pytest.mark.parametrize("with_package_base", [0, 1])
def test_setup_inputs(
    has_cmake_package,
    has_cmake_module,
    has_hybrid_package,
    has_pure_package,
    has_pure_module,
    with_package_base,
    mocker,
):
    """This test that a project can have a package with some modules
    installed using setup.py and some other modules installed using CMake.
    """

    tmp_dir = _tmpdir("test_setup_inputs")

    package_base = "to/the/base" if with_package_base else ""
    package_base_dir = package_base + "/" if package_base else ""
    cmake_source_dir = package_base

    if cmake_source_dir and (has_cmake_package or has_cmake_module):
        pytest.skip(
            "unsupported configuration: "
            "python package fully generated by CMake does *NOT* work. "
            "At least __init__.py should be in the project source tree"
        )

    # -------------------------------------------------------------------------
    # Here is the "SOURCE" tree layout:
    #
    # ROOT/
    #
    #     setup.py
    #
    #     [<base>/]
    #
    #         pureModule.py
    #
    #         pure/
    #             __init__.py
    #             pure.py
    #
    #             data/
    #                 pure.dat
    #
    #     [<cmake_src_dir>/]
    #
    #         hybrid/
    #             CMakeLists.txt
    #             __init__.py
    #             hybrid_pure.dat
    #             hybrid_pure.py
    #
    #             data/
    #                 hybrid_data_pure.dat
    #
    #             hybrid_2/
    #                 __init__.py
    #                 hybrid_2_pure.py
    #
    #             hybrid_2_pure/
    #                 __init__.py
    #                 hybrid_2_pure_1.py
    #                 hybrid_2_pure_2.py
    #
    #
    # -------------------------------------------------------------------------
    # and here is the "BINARY" distribution layout:
    #
    # The comment "CMake" or "Setuptools" indicates which tool is responsible
    # for placing the file in the tree used to create the binary distribution.
    #
    # ROOT/
    #
    #     cmakeModule.py                 # CMake
    #
    #     cmake/
    #         __init__.py                # CMake
    #         cmake.py                   # CMake
    #
    #     hybrid/
    #         hybrid_cmake.dat           # CMake
    #         hybrid_cmake.py            # CMake
    #         hybrid_pure.dat            # Setuptools
    #         hybrid_pure.py             # Setuptools
    #
    #         data/
    #             hybrid_data_pure.dat   # CMake or Setuptools
    #             hybrid_data_cmake.dat  # CMake                  *NO TEST*
    #
    #         hybrid_2/
    #             __init__.py            # CMake or Setuptools
    #             hybrid_2_pure.py       # CMake or Setuptools
    #             hybrid_2_cmake.py      # CMake
    #
    #         hybrid_2_pure/
    #             __init__.py            # CMake or Setuptools
    #             hybrid_2_pure_1.py     # CMake or Setuptools
    #             hybrid_2_pure_2.py     # CMake or Setuptools
    #
    #     pureModule.py                  # Setuptools
    #
    #     pure/
    #         __init__.py                # Setuptools
    #         pure.py                    # Setuptools
    #
    #         data/
    #             pure.dat               # Setuptools

    tmp_dir.join("setup.py").write(
        textwrap.dedent(
            """
        from skbuild import setup
        #from setuptools import setup
        setup(
            name="test_hybrid_project",
            version="1.2.3",
            description=("an hybrid package mixing files installed by both "
                        "CMake and setuptools"),
            author='The scikit-build team',
            license="MIT",
            cmake_source_dir='{cmake_source_dir}',
            cmake_install_dir='{cmake_install_dir}',
            # Arbitrary order of packages
            packages=[
        {p_off}    'pure',
        {h_off}    'hybrid.hybrid_2',
        {h_off}    'hybrid',
        {c_off}    'cmake',
        {p_off}    'hybrid.hybrid_2_pure',
            ],
            py_modules=[
        {pm_off}   '{package_base}pureModule',
        {cm_off}   '{package_base}cmakeModule',
            ],
            package_data={{
        {p_off}        'pure': ['data/pure.dat'],
        {h_off}        'hybrid': ['hybrid_pure.dat', 'data/hybrid_data_pure.dat'],
            }},
            # Arbitrary order of package_dir
            package_dir = {{
        {p_off}    'hybrid.hybrid_2_pure': '{package_base}hybrid/hybrid_2_pure',
        {p_off}    'pure': '{package_base}pure',
        {h_off}    'hybrid': '{package_base}hybrid',
        {h_off}    'hybrid.hybrid_2': '{package_base}hybrid/hybrid_2',
        {c_off}    'cmake': '{package_base}cmake',
            }}
        )
        """.format(
                cmake_source_dir=cmake_source_dir,
                cmake_install_dir=package_base,
                package_base=package_base_dir,
                c_off="" if has_cmake_package else "#",
                cm_off="" if has_cmake_module else "#",
                h_off="" if has_hybrid_package else "#",
                p_off="" if has_pure_package else "#",
                pm_off="" if has_pure_module else "#",
            )
        )
    )

    src_dir = tmp_dir.ensure(package_base, dir=1)

    src_dir.join("CMakeLists.txt").write(
        textwrap.dedent(
            """
        cmake_minimum_required(VERSION 3.5.0)
        project(hybrid NONE)
        set(build_dir ${{CMAKE_BINARY_DIR}})

        {c_off} file(WRITE ${{build_dir}}/__init__.py "")
        {c_off} file(WRITE ${{build_dir}}/cmake.py "")
        {c_off} install(
        {c_off}     FILES
        {c_off}         ${{build_dir}}/__init__.py
        {c_off}         ${{build_dir}}/cmake.py
        {c_off}     DESTINATION cmake
        {c_off}     )

        {cm_off} file(WRITE ${{build_dir}}/cmakeModule.py "")
        {cm_off} install(
        {cm_off}     FILES ${{build_dir}}/cmakeModule.py
        {cm_off}     DESTINATION .)

        {h_off} file(WRITE ${{build_dir}}/hybrid_cmake.dat "")
        {h_off} install(
        {h_off}     FILES ${{build_dir}}/hybrid_cmake.dat
        {h_off}     DESTINATION hybrid)

        {h_off} file(WRITE ${{build_dir}}/hybrid_cmake.py "")
        {h_off} install(
        {h_off}     FILES ${{build_dir}}/hybrid_cmake.py
        {h_off}     DESTINATION hybrid)

        {h_off} file(WRITE ${{build_dir}}/hybrid_data_cmake.dat "")
        {h_off} install(
        {h_off}     FILES ${{build_dir}}/hybrid_data_cmake.dat
        {h_off}     DESTINATION hybrid/data)

        {h_off} file(WRITE ${{build_dir}}/hybrid_2_cmake.py "")
        {h_off} install(
        {h_off}     FILES ${{build_dir}}/hybrid_2_cmake.py
        {h_off}     DESTINATION hybrid/hybrid_2)

        install(CODE "message(STATUS \\\"Installation complete\\\")")
        """.format(
                c_off="" if has_cmake_package else "#",
                cm_off="" if has_cmake_module else "#",
                h_off="" if has_hybrid_package else "#",
            )
        )
    )

    # List path types: 'c', 'cm', 'h', 'p' or 'pm'
    try:
        path_types = list(
            zip(
                *filter(
                    lambda i: i[1],
                    [
                        ("c", has_cmake_package),
                        ("cm", has_cmake_module),
                        ("h", has_hybrid_package),
                        ("p", has_pure_package),
                        ("pm", has_pure_module),
                    ],
                )
            )
        )[0]
    except IndexError:
        path_types = []

    def select_paths(annotated_paths):
        """Return a filtered list paths considering ``path_types``.

        `annotated_paths`` is list of tuple ``(type, path)`` where type
        is either `c`, 'cm', `h`, `p` or 'pm'.

        """
        return filter(lambda i: i[0] in path_types, annotated_paths)

    # Commented paths are the one expected to be installed by CMake. For
    # this reason, corresponding files should NOT be created in the source
    # tree.
    for (_type, path) in select_paths(
        [
            # ('c', 'cmake/__init__.py'),
            # ('c', 'cmake/cmake.py'),
            # ('cm', 'cmakeModule.py'),
            ("h", "hybrid/__init__.py"),
            # ('h', 'hybrid/hybrid_cmake.dat'),
            # ('h', 'hybrid/hybrid_cmake.py'),
            ("h", "hybrid/hybrid_pure.dat"),
            ("h", "hybrid/hybrid_pure.py"),
            # ('h', 'hybrid/data/hybrid_data_cmake.dat'),
            ("h", "hybrid/data/hybrid_data_pure.dat"),
            ("h", "hybrid/hybrid_2/__init__.py"),
            # ('h', 'hybrid/hybrid_2/hybrid_2_cmake.py'),
            ("h", "hybrid/hybrid_2/hybrid_2_pure.py"),
            ("p", "hybrid/hybrid_2_pure/__init__.py"),
            ("p", "hybrid/hybrid_2_pure/hybrid_2_pure_1.py"),
            ("p", "hybrid/hybrid_2_pure/hybrid_2_pure_2.py"),
            ("pm", "pureModule.py"),
            ("p", "pure/__init__.py"),
            ("p", "pure/pure.py"),
            ("p", "pure/data/pure.dat"),
        ]
    ):
        assert _type in ["p", "pm", "h"]
        root = package_base if (_type == "p" or _type == "pm") else cmake_source_dir
        tmp_dir.ensure(os.path.join(root, path))

    # Do not call the real setup function. Instead, replace it with
    # a MagicMock allowing to check with which arguments it was invoked.
    mock_setup = mocker.patch("skbuild.setuptools_wrap.setuptools.setup")

    # Convenience print function
    def _pprint(desc, value=None):
        print(
            "-----------------\n"
            "{}:\n"
            "\n"
            "{}\n".format(desc, pprint.pformat(setup_kw.get(desc, {}) if value is None else value, indent=2))
        )

    with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):

        assert mock_setup.call_count == 1
        setup_kw = mock_setup.call_args[1]

        # packages
        expected_packages = []
        if has_cmake_package:
            expected_packages += ["cmake"]
        if has_hybrid_package:
            expected_packages += ["hybrid", "hybrid.hybrid_2"]
        if has_pure_package:
            expected_packages += ["hybrid.hybrid_2_pure", "pure"]

        _pprint("expected_packages", expected_packages)
        _pprint("packages")

        # package dir
        expected_package_dir = {
            package: (os.path.join(CMAKE_INSTALL_DIR(), package_base, package.replace(".", "/")))
            for package in expected_packages
        }
        _pprint("expected_package_dir", expected_package_dir)
        _pprint("package_dir")

        # package data
        expected_package_data = {}

        if has_cmake_package:
            expected_package_data["cmake"] = ["__init__.py", "cmake.py"]

        if has_hybrid_package:
            expected_package_data["hybrid"] = [
                "__init__.py",
                "hybrid_cmake.dat",
                "hybrid_cmake.py",
                "hybrid_pure.dat",
                "hybrid_pure.py",
                "data/hybrid_data_cmake.dat",
                "data/hybrid_data_pure.dat",
            ]
            expected_package_data["hybrid.hybrid_2"] = ["__init__.py", "hybrid_2_cmake.py", "hybrid_2_pure.py"]

        if has_pure_package:
            expected_package_data["hybrid.hybrid_2_pure"] = ["__init__.py", "hybrid_2_pure_1.py", "hybrid_2_pure_2.py"]
            expected_package_data["pure"] = [
                "__init__.py",
                "pure.py",
                "data/pure.dat",
            ]

        if has_cmake_module or has_pure_module:
            expected_modules = []
            if has_cmake_module:
                expected_modules.append(package_base_dir + "cmakeModule.py")
            if has_pure_module:
                expected_modules.append(package_base_dir + "pureModule.py")
            expected_package_data[""] = expected_modules

        _pprint("expected_package_data", expected_package_data)
        package_data = {p: sorted(files) for p, files in setup_kw["package_data"].items()}

        _pprint("package_data", package_data)

        # py_modules (corresponds to files associated with empty package)
        expected_py_modules = []
        if "" in expected_package_data:
            expected_py_modules = [os.path.splitext(module_file)[0] for module_file in expected_package_data[""]]
        _pprint("expected_py_modules", expected_py_modules)
        _pprint("py_modules")

        # scripts
        expected_scripts = []
        _pprint("expected_scripts", expected_scripts)
        _pprint("scripts")

        # data_files
        expected_data_files = []
        _pprint("expected_data_files", expected_data_files)
        _pprint("data_files")

        assert sorted(setup_kw["packages"]) == sorted(expected_packages)
        assert sorted(setup_kw["package_dir"]) == sorted(expected_package_dir)
        assert package_data == {p: sorted(files) for p, files in expected_package_data.items()}
        assert sorted(setup_kw["py_modules"]) == sorted(expected_py_modules)
        assert sorted(setup_kw["scripts"]) == sorted([])
        assert sorted(setup_kw["data_files"]) == sorted([])


@pytest.mark.parametrize("with_cmake_source_dir", [0, 1])
def test_cmake_install_into_pure_package(with_cmake_source_dir, capsys, caplog):

    # -------------------------------------------------------------------------
    # "SOURCE" tree layout:
    #
    # (1) with_cmake_source_dir == 0
    #
    # ROOT/
    #
    #     CMakeLists.txt
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
    # "BINARY" distribution layout:
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

    cmake_source_dir = "src" if with_cmake_source_dir else ""

    tmp_dir.join("setup.py").write(
        textwrap.dedent(
            """
        from skbuild import setup
        setup(
            name="test_py_modules_keyword",
            version="1.2.3",
            description="a package testing use of py_modules keyword",
            author='The scikit-build team',
            license="MIT",
            packages=['fruits'],
            cmake_install_dir='fruits',
            cmake_source_dir='{cmake_source_dir}',
        )
        """.format(
                cmake_source_dir=cmake_source_dir
            )
        )
    )

    cmake_src_dir = tmp_dir.ensure(cmake_source_dir, dir=1)
    cmake_src_dir.join("CMakeLists.txt").write(
        textwrap.dedent(
            """
        cmake_minimum_required(VERSION 3.5.0)
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

    tmp_dir.ensure("fruits/__init__.py")

    with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
        pass

    messages = [
        "copying {}/{} -> " "{}/setuptools/lib".format(CMAKE_INSTALL_DIR(), module, SKBUILD_DIR())
        for module in [
            "fruits/__init__.py",
            "fruits/apple.py",
            "fruits/banana.py",
            "fruits/data/apple.dat",
            "fruits/data/banana.dat",
        ]
    ]

    out, _ = capsys.readouterr()
    out += caplog.text
    for message in messages:
        assert to_platform_path(message) in out


@pytest.mark.parametrize("zip_safe", [None, False, True])
def test_zip_safe_default(zip_safe, mocker):

    mock_setup = mocker.patch("skbuild.setuptools_wrap.setuptools.setup")

    tmp_dir = _tmpdir("zip_safe_default")

    setup_kwarg = ""
    if zip_safe is not None:
        setup_kwarg = f"zip_safe={zip_safe}"

    tmp_dir.join("setup.py").write(
        textwrap.dedent(
            """
        from skbuild import setup
        setup(
            name="zip_safe_default",
            version="1.2.3",
            description="a minimal example package",
            author='The scikit-build team',
            license="MIT",
            {setup_kwarg}
        )
        """.format(
                setup_kwarg=setup_kwarg
            )
        )
    )
    tmp_dir.join("CMakeLists.txt").write(
        textwrap.dedent(
            """
        cmake_minimum_required(VERSION 3.5.0)
        project(test NONE)
        install(CODE "execute_process(
          COMMAND \\${CMAKE_COMMAND} -E sleep 0)")
        """
        )
    )

    with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
        pass

    assert mock_setup.call_count == 1
    setup_kw = mock_setup.call_args[1]

    assert "zip_safe" in setup_kw
    if zip_safe is None:
        assert not setup_kw["zip_safe"]
    elif zip_safe:
        assert setup_kw["zip_safe"]
    else:  # zip_safe is False
        assert not setup_kw["zip_safe"]
