class Callable():
    def __init__(self, func, **kwargs) -> None:            
        self.func = func
        self.kwargs = kwargs

    def __call__(self, *args, **kwds):
        return self.func(*args, **self.kwargs, **kwds)