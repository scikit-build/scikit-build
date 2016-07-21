
import json
import os
import os.path
import struct
import subprocess
import sys

try:
    from urllib.request import urlopen
except ImportError:
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
        self._env_file = None

    def log(self, *s):
        print(" ".join(s))
        sys.stdout.flush()

    def urlopen(self, *args, **kwargs):
        return urlopen(*args, **kwargs)

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
        self.log("Python Version:")
        self.log(sys.version)
        self.log("    {}-bit".format(struct.calcsize("P") * 8))

        self.check_call([
            "python", "-m", "pip",
            "install", "--disable-pip-version-check",
            "--upgrade", "pip"
        ])

        self.check_call([
            "python", "-m", "pip", "install", "-r", "requirements.txt"])

        self.check_call([
            "python", "-m", "pip", "install", "-r", "requirements-dev.txt"])

    def drive_build(self):
        self.check_call(["python", "setup.py", "build"])

    def drive_style(self):
        self.check_call(["python", "-m", "flake8", "-v"])

    def drive_test(self):
        extra_test_args = self.env.get("EXTRA_TEST_ARGS", "")
        addopts = []
        if extra_test_args:
            addopts.extend(["--addopts", extra_test_args])

        self.check_call(
            ["python", "setup.py", "test"] + addopts)

    def drive_after_test(self):
        self.check_call(["python", "setup.py", "bdist_wheel"])
        self.check_call(["python", "setup.py", "bdist_wininst"])
        self.check_call(["python", "setup.py", "bdist_msi"])

if __name__ == "__main__":
    from appveyor_driver import AppveyorDriver
    from circle_driver import CircleDriver
    from travis_driver import TravisDriver

    driver_table = {
        "appveyor": AppveyorDriver,
        "circle": CircleDriver,
        "travis": TravisDriver,
    }

    stage_table = {
        "install": "drive_install",
        "build": "drive_build",
        "style": "drive_style",
        "test": "drive_test",
        "after_test": "drive_after_test",
    }

    class_key, stage_key = sys.argv[1:3]
    try:
        DriverClass = driver_table[class_key]
    except KeyError:
        raise KeyError("invalid driver implementation: {}".format(class_key))
    try:
        stage = stage_table[stage_key]
    except KeyError:
        raise KeyError("invalid stage: {}".format(stage_key))

    d = DriverClass()
    with d.env_context():
        getattr(d, stage)()
