from threading import Thread

def thread(fn, args):
    t = Thread(target=fn, args=args, daemon=True)
    t.start()
