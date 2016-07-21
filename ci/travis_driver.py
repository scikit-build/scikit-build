
from driver import Driver


class TravisDriver(Driver):
    def load_env(self, *args, **kwargs):
        Driver.load_env(self, *args, **kwargs)
        self.is_darwin = (self.env.get("TRAVIS_OS_NAME") == "osx")
        self.py_version = self.env.get("PYTHONVERSION")
        self.extra_test_args = self.env.get("EXTRA_TEST_ARGS", "")

    def drive_install(self):
        cmake_version = "3.5"
        cmake_os = "Linux"
        if self.is_darwin:
            cmake_os = "Darwin"

        cmake_name = "cmake-{}.0-{}-x86_64".format(cmake_version, cmake_os)
        cmake_package = ".".join((cmake_name, "tar", "gz"))

        self.log("Downloading", cmake_package)
        self.check_call([
            "wget", "--no-check-certificate", "--progress=dot",
            "https://cmake.org/files/v{}/{}".format(
                cmake_version, cmake_package)
        ])

        self.log("Extracting", cmake_package)
        self.check_call(["tar", "xzf", cmake_package])

        if self.is_darwin:
            prefix = "/usr/local/bin"
            self.log("Removing any existing CMake in", prefix)
            self.check_call(
                ["sudo", "rm", "-f"] + [
                    "/".join((prefix, subdir)) for subdir in
                    ("cmake", "cpack", "cmake-gui", "ccmake", "ctest")
                ]
            )

            self.log("Installing CMake in", prefix)
            self.check_call([
                "sudo",
                cmake_name + "/CMake.app/Contents/bin/cmake-gui",
                "--install"
            ])

            self.check_call(
                "\n".join((
                    "brew update",
                    "brew outdated pyenv || brew upgrade pyenv",
                    "eval \"$( pyenv init - )\"",
                    "pyenv install " + self.py_version,
                    "pyenv local " + self.py_version,
                    "echo 'Python Version:'",
                    (
                        "python -c \""
                        "import sys, struct ; "
                        "print(sys.version) ; "
                        "print('{}-bit'.format(struct.calcsize('P') * 8))"
                        "\""
                    ),
                    (
                        "pip install "
                        "--user --disable-pip-version-check --user --upgrade "
                        "pip"
                    ),
                    "pip install --user -r requirements.txt",
                    "pip install --user -r requirements-dev.txt",
                )),
                shell=True
            )

        else:
            self.log("Copying", cmake_name, "to /usr/local")
            self.check_call([
                "sudo", "rsync", "-avz", cmake_name + "/", "/usr/local"])

            Driver.drive_install(self)

    def drive_build(self):
        if self.is_darwin:
            self.check_call(
                "\n".join((
                    "eval \"$( pyenv init - )\"",
                    "pyenv local " + self.py_version,
                    "python setup.py build"
                ))
            )
        else:
            Driver.drive_build(self)

    def drive_style(self):
        if self.is_darwin:
            self.check_call(
                "\n".join((
                    "eval \"$( pyenv init - )\"",
                    "pyenv local " + self.py_version,
                    "python -m flake8 -v"
                ))
            )
        else:
            Driver.drive_style(self)

    def drive_test(self):
        if self.is_darwin:
            addopts = ""
            if self.extra_test_args:
                addopts = " --addopts " + self.extra_test_args

            self.check_call(
                "\n".join((
                    "eval \"$( pyenv init - )\"",
                    "pyenv local " + self.py_version,
                    "python setup.py test" + addopts
                ))
            )
        else:
            Driver.drive_test(self)

    def drive_after_test(self):
        if self.is_darwin:
            self.check_call(
                "\n".join((
                    "eval \"$( pyenv init - )\"",
                    "codecov -X gcov --required --file ./tests/coverage.xml",
                    "python setup.py bdist_wheel"
                )),
                shell=True
            )
        else:
            self.check_call([
                "codecov", "-X", "gcov", "--required",
                "--file", "./tests/coverage.xml"
            ])
            Driver.drive_after_test(self)
