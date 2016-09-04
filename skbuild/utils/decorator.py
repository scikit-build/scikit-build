
from six import wraps

from . import push_dir as push_dir_manager


def push_dir(*pd_args, **pd_kwargs):
    def wrapper(func):
        @wraps(func)
        def decorator(*func_args, **func_kwargs):
            with push_dir_manager(*pd_args, **pd_kwargs):
                return func(*func_args, **func_kwargs)
        return decorator
    return wrapper
