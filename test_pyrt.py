from pyrt import pyrt

@pyrt("/usr/bin/python")
def test():
    import sys
    print sys.version_info
    print sys.path[1]

@pyrt("/home/yangbin/.local/share/virtualenvs/pyrt-UWFCoLl1/bin/python")
def test1():
    import sys
    print sys.version_info
    print sys.path[1]

def main():
    test()
    test1()

if __name__ == '__main__':
    main()



