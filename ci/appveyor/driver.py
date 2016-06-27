
import json
import os
import os.path
import shlex
import shutil
import struct
import subprocess
import sys
import time
import zipfile

try:
    from urllib.error import URLError
    from urllib.error import HTTPError
    from urllib.error import ContentTooShortError

    from urllib.request import urlopen
except ImportError:
    from urllib2 import URLError
    from urllib2 import HTTPError
    from urllib  import ContentTooShortError

    from urllib2 import urlopen

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

    def load_env(self, env_file="env.json"):
        if self.env is not None:
            self.unload_env()

        self.env = {}
        self.env.update(os.environ)
        self._env_file = env_file

        if os.path.exists(self._env_file):
            self.env.update(json.load(open(self._env_file)))

    def save_env(self, env_file=None):
        if env_file is None:
            env_file = self._env_file

        with open(self.env_file, "w") as env:
            json.dump(self.env, env)

    def unload_env(self):
        self.env = None

    def env_prepend(self, key, *values):
        self.env[key] = os.pathsep.join(
            values + self.env.get(key, "").split(os.pathsep))

    def check_call(*args, **kwds):
        kwds["env"] = kwds.get("env", self.env)
        return subprocess.check_call(*args, **kwds)

    def env_context(self, env_file="env.json"):
        return DriverContext(self, env_file)

    def drive_init(self):
        print("RDP Connection Information (In case of hanging build)")

        local_path = os.path.join("ci", "appveyor", "enable-rdp.ps1")
        if not os.path.exists(local_path):

            remote_script_url = (
                "https://raw.githubusercontent.com"
                "/appveyor/ci/master/scripts/enable-rdp.ps1")
            with urlopen(remote_script_url) as remote_script:

                with open(local_path, "w") as local_script:
                    shutil.copyfileobj(remote_script, local_script)

        self.check_call(["powershell.exe", "-File", local_path])

    def drive_install(self):
        # query appveyor for the latest builds
        account = self.env["APPVEYOR_ACCOUNT_NAME"]
        slug = self.env["APPVEYOR_PROJECT_SLUG"]
        build_number = self.env["APPVEYOR_BUILD_NUMBER"]
        pr_number = self.env["APPVEYOR_PULL_REQUEST_NUMBER"]

        current_builds = [
            build for build in

            json.load(urlopen(
                ("https://ci.appveyor.com"
                 "/api/projects/{}/{}"
                 "/history/recordsNumber=50").format(account, slug)
            ))["builds"]

            if build["pullRequestId"] == pr_number
        ]

        if current_builds and current_builds[0]["buildNumber"] != build_number:
            raise Exception("There are newer queued builds for this "
                            "pull request, failing early.")

        print("Filesystem root:")
        self.check_call(["dir", "C:\\"])

        print("Installed SDKs:")
        self.check_call(["dir", "C:\\Program Files\\Microsoft SDKs\\Windows\\"])

        local_path = os.path.join(
            "ci", "appveyor", "run-with-visual-studio.cmd")
        with urlopen("https://raw.githubusercontent.com"
                     "/ogrisel/python-appveyor-demo"
                     "/f54ec3593bcea682098a59b560c1850c19746e10"
                     "/appveyor/run_with_env.cmd'") as remote_script:
            with open(local_path, "w") as local_script:
                shutil.copyfileobj(remote_script, local_script)

        ### TODO CONFIGURE VISUAL STUDIO

        python_root = self.env["PYTHON"]
        self.env_prepend(
            "PATH", os.path.join(python_root, "Scripts"), python_root)

        self.env["SKBUILD_CMAKE_CONFIG"] = "Release"

        print("Python Version:")
        print(sys.version)
        print("    {}-bit".format(struct.calcsize("P")*8))

        self.check_call([
            "python", "-m", "pip",
            "install", "--disable-pip-version-check",
            "--user", "--upgrade", "pip"
        ])

        self.check_call(["python", "-m", "pip", "install", "wheel"])

        with urlopen("https://cmake.org"
                     "/files/v3.5/cmake-3.5.2-win32-x86.zip") as remote_file:

            with zipfile.ZipFile(remote_file) as remote_zip:
                remote_zip.extractall("C:\\cmake")

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
            ["python", "-m", "nose", "-v", "-w", "tests"]
            + extra_test_args)

    def drive_after_test(self):
        self.check_call(["python", "setup.py", "bdist_wheel"])
        self.check_call(["python", "setup.py", "bdist_wininst"])
        self.check_call(["python", "setup.py", "bdist_msi"])

        if os.path.exists("dist"):
            self.check_call(["dir", "dist"])

    def drive_on_finish(self):
        if self.env.get("BLOCK", "0") == "1":
            lock_file_path = os.path.join(
                self.env["USERPROFILE"], "Dekstop", "spin-lock.txt")

            with open(lock_file_path, "w") as f:
                f.write("")

            while os.path.exists(lock_file_path):
                time.sleep(5)

if __name__ == "__main__":
    d = Driver()
    stage = sys.argv[1]

    with d.env_context():
        if stage == "init":
            d.drive_init()
        elif stage == "install":
            d.drive_install()
        elif stage == "build":
            d.drive_build()
        elif stage == "test":
            d.drive_test()
        elif stage == "after_test":
            d.drive_after_test()
        elif stage == "on_finish":
            d.drive_on_finish()
        else:
            raise Exception("invalid stage: {}".format(stage))

