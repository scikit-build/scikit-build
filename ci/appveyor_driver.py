
from driver import Driver

import os
import os.path
import shutil
import zipfile


class AppveyorDriver(Driver):
    def drive_install(self):
        self.log("Filesystem root:")
        self.check_call(["dir", "C:\\"])

        self.log("Installed SDKs:")
        self.check_call([
            "dir", "C:\\Program Files\\Microsoft SDKs\\Windows\\"])

        local_path = os.path.join(
            "ci", "appveyor", "run-with-visual-studio.cmd")
        remote_script = self.urlopen("https://raw.githubusercontent.com"
                                     "/ogrisel/python-appveyor-demo"
                                     "/f54ec3593bcea682098a59b560c1850c19746e10"
                                     "/appveyor/run_with_env.cmd")
        with open(local_path, "wb") as local_script:
            shutil.copyfileobj(remote_script, local_script)

        # Implement workaround for 64-bit Visual Studio 2008
        if self.env["PYTHON_ARCH"] == "64":
            self.log("Downloading 64-bit Visual Studio Fix")
            remote_zip = self.urlopen(
                "https://github.com/menpo/"
                "condaci/raw/master/vs2008_patch.zip")
            with open("C:\\vs2008_patch.zip", "wb") as local_zip:
                shutil.copyfileobj(remote_zip, local_zip)

            self.log("Unpacking 64-bit Visual Studio Fix")
            with zipfile.ZipFile("C:\\vs2008_patch.zip") as local_zip:
                local_zip.extractall("C:\\vs2008_patch")

            self.log("Applying 64-bit Visual Studio Fix")
            self.check_call(
                [
                    "cmd.exe",
                    "/E:ON",
                    "/V:ON",
                    "/C",
                    "C:\\vs2008_patch\\setup_x64.bat"
                ],
                cwd="C:\\vs2008_patch")

        # Implement workaround for MinGW on Appveyor
        if self.env.get("CMAKE_GENERATOR", "").lower().startswith("mingw"):
            self.log("Applying MinGW PATH fix")

            mingw_bin = os.path.normpath(
                os.path.join("C:\\", "MinGW", "bin")).lower()

            self.env["PATH"] = os.pathsep.join(
                dir for dir in
                self.env["PATH"].split(os.pathsep)

                if (
                    os.path.normpath(dir).lower() == mingw_bin or
                    not (
                        os.path.exists(os.path.join(dir, "sh.exe")) or
                        os.path.exists(os.path.join(dir, "sh.bat")) or
                        os.path.exists(os.path.join(dir, "sh"))
                    )
                )
            )

        python_root = self.env["PYTHON"]
        py_scripts = os.path.join(python_root, "Scripts")

        self.env["PYTHONSCRIPTS"] = py_scripts
        self.env_prepend("PATH", py_scripts, python_root)

        self.env["SKBUILD_CMAKE_CONFIG"] = "Release"

        self.log("Downloading CMake")
        remote_file = self.urlopen(
            "https://cmake.org/files/v3.5/cmake-3.5.2-win32-x86.zip")

        with open("C:\\cmake.zip", "wb") as local_file:
            shutil.copyfileobj(remote_file, local_file)

        self.log("Unpacking CMake")

        try:
            os.mkdir("C:\\cmake")
        except OSError:
            pass

        with zipfile.ZipFile("C:\\cmake.zip") as local_zip:
            local_zip.extractall("C:\\cmake")

        self.env_prepend("PATH", "C:\\cmake\bin")

        Driver.drive_install(self)

    def drive_after_test(self):
        Driver.drive_after_test(self)

        codecov = os.path.join(self.env["PYTHONSCRIPTS"], "codecov.exe")
        self.check_call([
            codecov, "-X", "gcov", "--required",
            "--file", ".\\tests\\coverage.xml"
        ])

        if os.path.exists("dist"):
            self.check_call(["dir", "dist"], shell=True)
