from __future__ import annotations

if __name__ == "__main__":
    from . import _bonjour as bonjour
    from . import _hello as hello

    hello.hello()
    bonjour.bonjour()
