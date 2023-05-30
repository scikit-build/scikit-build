from __future__ import annotations

import os
import sys

print(os.environ)
print(sys.executable)

from skbuild import setup  # noqa: E402

setup(
    name="hello_no_language",
    version="1.2.3",
    description="a minimal example package",
    author="The scikit-build team",
    license="MIT",
)
