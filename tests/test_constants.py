import os
import sys

from skbuild.constants import SKBUILD_DIR, set_skbuild_plat_name, skbuild_plat_name


def test_set_skbuild_plat_name():
    try:
        previous_plat_name = skbuild_plat_name()
        set_skbuild_plat_name("plat-name")
        assert os.path.join("_skbuild", "plat-name-{}.{}".format(*sys.version_info[:2])) == SKBUILD_DIR()
    finally:
        set_skbuild_plat_name(previous_plat_name)
