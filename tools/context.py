from contextlib import contextmanager


@contextmanager
def temporary_state(obj, **kwargs):
    previous = {key: getattr(obj, key) for key in kwargs.keys()}
    for key, value in kwargs.items():
        setattr(obj, key, value)
    try:
        yield
    finally:
        for key, value in previous.items():
            setattr(obj, key, value)