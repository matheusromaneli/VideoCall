from threading import Thread

class Callable():
    def __init__(self, func, **kwargs) -> None:            
        self.func = func
        self.kwargs = kwargs

    def __call__(self, *args, **kwds):
        return self.func(*args, **self.kwargs, **kwds)

def thread(fn, args):
    t = Thread(target=fn, args=args, daemon=True)
    t.start()
