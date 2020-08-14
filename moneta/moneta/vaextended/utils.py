# decorator to add a function to a class
def extend_class(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator