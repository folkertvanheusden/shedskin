# test changes for examples3

# division
a = 9/2
print(a)
b = 9//2
print(b)

# bytes
c = b'blup'
d = c[1]
print(d)
for x in c:
    print(x)

n = 66
bla = b'%c%c' % (n, n+1)
print(bla)

bs = set()
bs.add(b'wop')
print(b'wo'+b'p' in bs)

hup = b'huphup'
hup2 = hup[2:-1]
print(hup2)

# bytearray
ba = bytearray(c)
ba[2] = ord('a')
print(ba)

# reduce
from functools import reduce

print(reduce(lambda a,b: a+b, [3,5,7]))
print(reduce(lambda a,b: a-b, set([3,5,7]), 1))

