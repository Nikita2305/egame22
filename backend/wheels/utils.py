from functools import wraps

def debug_print(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print("start",func.__qualname__)
        ret = func(self, *args, **kwargs)
        return ret
    return wrapper
