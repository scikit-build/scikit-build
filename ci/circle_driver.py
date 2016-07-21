
from driver import Driver


class CircleDriver(Driver):
    def drive_install(self):
        self.check_call(["sudo", "apt-get", "update"])
        self.check_call(["sudo", "apt-get", "install", "gfortran"])
        self.check_call([
            "wget", "--no-check-certificate", "--progress=dot",
            "https://cmake.org/files/v3.5/cmake-3.5.0-Linux-x86_64.tar.gz"
        ])
        self.check_call(["tar", "xzf", "cmake-3.5.0-Linux-x86_64.tar.gz"])
        self.check_call([
            "sudo", "rsync", "-avz", "cmake-3.5.0-Linux-x86_64/", "/usr/local"
        ])

        Driver.drive_install(self)

    def drive_after_test(self):
        self.check_call([
            "codecov", "-X", "gcov", "--required",
            "--file", "./tests/coverage.xml"
        ])

        Driver.drive_after_test(self)
