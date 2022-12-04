# overloading TODO support __iter__, __next__ combo?

class huppa:
    def __init__(self):
        self.count = 0

    def __str__(self):
        return 'huppa'

    def __bytes__(self):
        return b'huppa'

    def __truediv__(self, other):
        print('truediv')
        return self

    def __itruediv__(self, other):
        print('itruediv')
        return self

    def __floordiv__(self, other):
        print('floordiv')
        return self

    def __ifloordiv__(self, other):
        print('ifloordiv')
        return self

h = huppa()

print(str(h))
print(bytes(h))

print(h/h)
print(h//h)
h /= h
h //= h

# TODO os.popen2 disappeared? check
#os.popen2 improvement
#import os
#child_stdin, child_stdout = os.popen2(["echo", "a  text"], "r")
#print(repr(child_stdout.read()))
#child_stdin, child_stdout = os.popen2(iter(["echo", "a  text"]), "r")
#print(repr(child_stdout.read()))
#child_stdin, child_stdout = os.popen2(("echo", "a  text"), "r")
#print(repr(child_stdout.read()))
#child_stdin, child_stdout = os.popen2("echo a  text", "r")
#print(repr(child_stdout.read()))

xx = b'\x00hoi\x00'
print(xx)
print(repr(xx))

print(bytes())
print(bytes([1,2,3]))
print(bytes(set([1])))
print(bytes(0))
print(bytes(4))
print(bytes(7))
print(bytes(b'hop'))
print(bytes(bytes(7)))
print(bytes(bytearray(7)))

print(bytearray())
print(bytearray([1,2,3]))
print(bytes((250, 251)))
print(bytearray(0))
print(bytearray(4))
print(bytearray(7))
print(bytearray(b'hop'))
print(bytearray(bytearray(7)))
print(bytearray(bytes(7)))

print(b'hop %s' % b'hup')
print(b'hop %s' % bytearray(b'hup'))

print(int(b'123'))
