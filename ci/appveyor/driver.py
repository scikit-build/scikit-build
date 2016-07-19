
import json
import os
import os.path
import shlex
import shutil
import struct
import subprocess
import sys
import zipfile

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen


def log(s):
    print(s)
    sys.stdout.flush()


class DriverContext(object):
    def __init__(self, driver, env_file="env.json"):
        self.driver = driver
        self.env_file = env_file

    def __enter__(self):
        self.driver.load_env(self.env_file)
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None and exc_value is None and traceback is None:
            self.driver.save_env()

        self.driver.unload_env()


class Driver(object):
    def __init__(self):
        self.env = None
        self._env_file = None

    def load_env(self, env_file="env.json"):
        if self.env is not None:
            self.unload_env()

        self.env = {}
        self.env.update(os.environ)
        self._env_file = env_file

        if os.path.exists(self._env_file):
            self.env.update(json.load(open(self._env_file)))

        self.env = {str(k): str(v) for k, v in self.env.items()}

    def save_env(self, env_file=None):
        if env_file is None:
            env_file = self._env_file

        with open(env_file, "w") as env:
            json.dump(self.env, env)

    def unload_env(self):
        self.env = None

    def env_prepend(self, key, *values):
        self.env[key] = os.pathsep.join(
            list(values) + self.env.get(key, "").split(os.pathsep))

    def check_call(self, *args, **kwds):
        kwds["env"] = kwds.get("env", self.env)
        return subprocess.check_call(*args, **kwds)

    def env_context(self, env_file="env.json"):
        return DriverContext(self, env_file)

    def drive_install(self):
        log("Filesystem root:")
        self.check_call(["dir", "C:\\"])

        log("Installed SDKs:")
        self.check_call(["dir", "C:\\Program Files\\Microsoft SDKs\\Windows\\"])

        local_path = os.path.join(
            "ci", "appveyor", "run-with-visual-studio.cmd")
        remote_script = urlopen("https://raw.githubusercontent.com"
                                "/ogrisel/python-appveyor-demo"
                                "/f54ec3593bcea682098a59b560c1850c19746e10"
                                "/appveyor/run_with_env.cmd")
        with open(local_path, "wb") as local_script:
            shutil.copyfileobj(remote_script, local_script)

        # Implement workaround for 64-bit Visual Studio 2008
        if self.env["PYTHON_ARCH"] == "64":
            log("Downloading 64-bit Visual Studio Fix")
            remote_zip = urlopen(
                "https://github.com/menpo/condaci/raw/master/vs2008_patch.zip")
            with open("C:\\vs2008_patch.zip", "wb") as local_zip:
                shutil.copyfileobj(remote_zip, local_zip)

            log("Unpacking 64-bit Visual Studio Fix")
            with zipfile.ZipFile("C:\\vs2008_patch.zip") as local_zip:
                local_zip.extractall("C:\\vs2008_patch")

            log("Applying 64-bit Visual Studio Fix")
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
            log("Applying MinGW PATH fix")

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
        self.env_prepend(
            "PATH", os.path.join(python_root, "Scripts"), python_root)

        self.env["SKBUILD_CMAKE_CONFIG"] = "Release"

        log("Python Version:")
        log(sys.version)
        log("    {}-bit".format(struct.calcsize("P")*8))

        self.check_call([
            "python", "-m", "pip",
            "install", "--disable-pip-version-check",
            "--user", "--upgrade", "pip"
        ])

        self.check_call(["python", "-m", "pip", "install", "wheel"])

        log("Downloading CMake")
        remote_file = urlopen(
            "https://cmake.org/files/v3.5/cmake-3.5.2-win32-x86.zip")

        with open("C:\\cmake.zip", "wb") as local_file:
            shutil.copyfileobj(remote_file, local_file)

        log("Unpacking CMake")

        try:
            os.mkdir("C:\\cmake")
        except OSError:
            pass

        with zipfile.ZipFile("C:\\cmake.zip") as local_zip:
            local_zip.extractall("C:\\cmake")

        self.env_prepend("PATH", "C:\\cmake\bin")

        self.check_call([
            "python", "-m", "pip", "install", "-r", "requirements.txt"])

        self.check_call([
            "python", "-m", "pip", "install", "-r", "requirements-dev.txt"])

    def drive_build(self):
        self.check_call(["python", "setup.py", "build"])

    def drive_test(self):
        extra_test_args = shlex.split(self.env.get("EXTRA_TEST_ARGS", ""))
        self.check_call(
            ["python", "-m", "nose", "-v", "-w", "tests"] + extra_test_args)

    def drive_after_test(self):
        self.check_call(["python", "setup.py", "bdist_wheel"])
        self.check_call(["python", "setup.py", "bdist_wininst"])
        self.check_call(["python", "setup.py", "bdist_msi"])

        if os.path.exists("dist"):
            self.check_call(["dir", "dist"], shell=True)

if __name__ == "__main__":
    d = Driver()
    stage = sys.argv[1]

    with d.env_context():
        if stage == "install":
            d.drive_install()
        elif stage == "build":
            d.drive_build()
        elif stage == "test":
            d.drive_test()
        elif stage == "after_test":
            d.drive_after_test()
        else:
            raise Exception("invalid stage: {}".format(stage))
