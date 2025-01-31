"""
My ScikitBuild Module Example
"""
__version__ = '0.1.0'

try:
    from . import submod
except Exception:
    print('ERROR submod NOT INCLUDED IN PACAKGE!')
    submod = None

try:
    from ._my_skb_mod_cython import cython_func
except Exception:
    print('ERROR _my_skb_mod_cython NOT INCLUDED IN PACAKGE!')
    cython_func = None

__all__ = ['cython_func', 'submod']
