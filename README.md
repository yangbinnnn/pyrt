# pyrt

#1

```
def foo():
    # default python runtime
    pass

@pyrt("/path/to/pyrt/bin/python")
def func():
    # specific python runtime
    pass

```

#2
```
def main():
    with pyrt("/path/to/pyrt/bin/python"):
        # specific python runtime
        pass
```
