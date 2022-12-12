# check bounds after wrapping..
alist = list(range(5))  # TODO __getitem__ without list! :P
for i in range(-10,10):
    try:
        print(alist[i], i)
    except IndexError:
        print('nope', i)
try:
    print([][-1])
except IndexError:
    print('nope..')

# fix examples/Gh0stenstein
px = 0xff << 24
print (px == 0xff000000)

# some datetime tests
import datetime
print(datetime.datetime.today().date())
print(datetime.datetime.utcnow().date())

# float(str) inf
bignumstr = '1' + 500 * '0'
print(float(bignumstr))

# optimize: for .. in enumerate(str)
for ix, ex in enumerate('poehee'):
    print(ix, ex)

# optimize: name in (expr, expr, ..)
z = 12
print(z in (10,12,14))
print(z not in (7,8,9))
z = 8
print(z in (10,12,14))
print(z not in (7,8,9))

# different output in python3
a = set([1,2])                           # [Set(int)]
a.add(3)                                 # []
print(a)                                  # [Set(int)]

gs = frozenset([1])
h = {}
h[gs] = 4
print(h)

def mapp():
    allchr = [chr(c) for c in range(256)]
    return allchr
print(mapp()[66:86])
print(repr(''.join([chr(i) for i in range(66,87)])))

class ueuk(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return 'x'
    def __repr__(self):
        return 'ueukrepr!'

try:
    raise ueuk('aha! error.')
except ueuk as errx:
    print(errx)

# empty set?
blah2 = set([])
print(blah2)

b = [1,2,3]
g = iter(b)
for _ in range(5):
    print(next(g, -1))
print()

# --- slice assignment (random test)
#import random
#random.seed(10)
#
#for x in range(1000):
#    l,u,s = random.randrange(-5,5), random.randrange(-5,5), random.randrange(-5,5)
#    a = list(range(5))
#    print(a, 'lower', l, 'upper', u, 'step', s)
#    try:
#        z = list(range(random.randrange(0,5)))
#        print('xrange', z)
#        a[l:u:s] = z
#        print('done', a)
#    except ValueError as v:
#        print(v)

# --- float repr
#print(1/3.0)
#print(1.1234123412341234) TODO duplicate python's float repr..
print(1.1)
print(8.0)
print(9.12341234e20)
print(1.202)

#multidir fixes
from testdata import crap
print(crap.incrap())
import testdata.bert180 as bert
print(bert.hello(1))
from testdata import crap2
crap2.incrap2()
import testdata.crap2
tc2c2 = testdata.crap2.crap2()

# sorted, list.sort: reverse
print(sorted([5,1,3,2,4]))
print(sorted([5,1,3,2,4], reverse=True))

print(sorted(set([5,1,3,2,4])))
print(sorted(set([5,1,3,2,4]), reverse=True))

print(sorted('abcde'))
print(sorted('abcde', reverse=True))

ls = [1,4,5,2,3]
ls.sort(); print(ls)
ls.sort(reverse=True); print(ls)

# oct
print(oct(1==2), oct(1!=2))
print(oct(200), oct(-200), oct(0))

#int(), float(), str(); test all
print(int(), float(), list(), dict(), set(), tuple(), frozenset(),) # XXX repr(str())

# range segfault
broken_range = range(3,0,1)
print(list(broken_range))
