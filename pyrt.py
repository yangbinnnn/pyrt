import os
import marshal
import functools
import hashlib

class SandBOX(object):
    def __init__(self, py, func, args, kwargs):
        self.dir = "/dev/shm"
        self.resource = []
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.py = py
        self.box = None
        self._init_sandbox()

    def run(self):
        try:
            pfunc = self._dump(self.func.func_code)
            pargs = self._dump(self.args)
            pkwargs = self._dump(self.kwargs)
            presult = os.path.join(self.dir, self.md5(pfunc + pargs + pkwargs))
            self.resource.append(presult)
            cmd = self._gencmd(pfunc, pargs, pkwargs, presult)
            print os.popen(cmd).read()
            return self._load(presult)
        finally:
            for p in self.resource:
                if os.path.exists(p):
                    os.unlink(p)

    def _init_sandbox(self):
        sandbox = r'''
import sys
import types
import marshal
def run(pfunc, pargs, pkwargs, presult):
    func_code = marshal.load(open(pfunc, "rb"))
    args = marshal.load(open(pargs, "rb"))
    kwargs = marshal.load(open(pkwargs, "rb"))
    func = types.FunctionType(func_code, globals(), func_code.co_name)
    result = func(*args, **kwargs)
    with open(presult, "wb") as f:
        marshal.dump(result, f)

if __name__ == '__main__':
    func, args, kwargs, result = sys.argv[1:5]
    run(func, args, kwargs, result)
        '''
        path = os.path.join(self.dir, self.md5(sandbox))
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(sandbox)
        self.resource.append(path)
        self.box = path

    def _gencmd(self, pfunc, pargs, pkwargs, presult):
        assert self.box, "sandbox not init"
        fmt = {"py": self.py, "sandbox": self.box, "func": pfunc, 
               "args": pargs, "kwargs": pkwargs, "result": presult}
        return "{py} {sandbox} {func} {args} {kwargs} {result}".format(**fmt)

    def _dump(self, obj):
        obj = marshal.dumps(obj)
        path = os.path.join(self.dir, self.md5(obj))
        with open(path, "wb") as f:
            f.write(obj)
        self.resource.append(path)
        return path

    def _load(self, path):
        return marshal.load(open(path, "rb"))

    def md5(self, s):
        return hashlib.md5(s).hexdigest()


def pyrt(path):
    def decorate(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            assert os.path.exists(path), "%s not found" % path
            box = SandBOX(path, func, args, kwargs)
            return box.run()
        return wrap
    return decorate