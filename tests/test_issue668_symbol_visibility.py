from __future__ import annotations

import glob
import platform
import shutil
import subprocess

import pytest

from skbuild.constants import CMAKE_BUILD_DIR

from . import (
    _tmpdir,
    execute_setup_py,
    initialize_git_repo_and_commit,
    prepare_project,
    push_dir,
)


@pytest.mark.skipif(
    platform.system().lower() not in ["linux"], reason="Executable and Linkable Format (ELF) is specific to Linux"
)
@pytest.mark.parametrize("skip_override", ["ON", "OFF"])
def test_symbol_visibility(skip_override):
    with push_dir():
        tmp_dir = _tmpdir("test_issue668_symbol_visibility")
        project = "issue-668-symbol-visibility"
        prepare_project(project, tmp_dir)
        initialize_git_repo_and_commit(tmp_dir, verbose=True)

        with execute_setup_py(
            tmp_dir, ["build", f"-DSKBUILD_GNU_SKIP_LOCAL_SYMBOL_EXPORT_OVERRIDE:BOOL={skip_override}"]
        ):
            pass

        print(f"Running test with SKBUILD_GNU_SKIP_LOCAL_SYMBOL_EXPORT_OVERRIDE:BOOL={skip_override}")

        lib_dir = str(tmp_dir) + "/" + CMAKE_BUILD_DIR()
        libs = glob.glob(lib_dir + "/*.so")
        assert libs
        print(f"Examining the library file: {libs[0]}")

        readelf = shutil.which("readelf")
        assert readelf

        cppfilt = shutil.which("c++filt")
        assert cppfilt

        result = subprocess.Popen([readelf, "-s", "--wide", libs[0]], stdout=subprocess.PIPE)
        output = str(subprocess.check_output((cppfilt), stdin=result.stdout), "UTF-8")
        result.wait()
        assert result.stdout is not None
        result.stdout.close()

        for line in output.splitlines():
            # Looking for entries associated with get_map
            # ex.     62: 0000000000001260   164 FUNC    GLOBAL DEFAULT   14 get_map\n
            # NOTE: We want to ignore get_map::id_to_resourse entries
            if "get_map" in line.split():
                print(line)
                if skip_override == "ON":
                    assert "GLOBAL" in line
                else:
                    assert "LOCAL" in line
            # Looking for the PyInit_ entries
            # These should always be GLOBAL
            if "PyInit_" in line:
                print(line)
                assert "GLOBAL" in line
