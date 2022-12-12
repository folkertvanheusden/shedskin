from __future__ import print_function

# defaultdict fixes
from collections import defaultdict
dnone = defaultdict()
#dnone = defaultdict(None)
dnone = defaultdict(None, [(8, 9)])
dnone = defaultdict(None, dnone)
dnone[4] = 5
try:
    print(dnone[5])
except KeyError:
    print('keyerror')
print(sorted(dnone.items()))

print(sorted(defaultdict(str, {1: 'hoi'}).items()))

# self variable (TODO: fix analyze_virtuals)
self = 4
print(self)

# bin, oct, hex
print(hex(200), hex(-200), hex(0))
print(bin(200), bin(-200), bin(0))

class A(object):
    def __index__(self):
        return 42
a = A()
print(bin(a))

print(bin(1==2), bin(1!=2))

# game of life
argv=[0,3,3]
r,c=list(map(int,argv[1:]))
p,g=r*c,range
z=g(p)
w=lambda x:sum((abs(x%r-v%r)<2)&(abs(x//r-v//r)<2)&d[v]for v in z)
for m in g(2**p):
 d=[m>>x&1 for x in z]
 if all(d[x]&(2<w(x)<5)|~d[x]&(w(x)!=3)for x in z):
  for x in g(c+1):print(''.join('.X'[y]for y in d[r*x:r*x+r]))

# unpacking and __getitem__ special cases
seq = [1,2,3]
seq = (1,2,3)
s1,s2,s3 = seq
print(s1,s2,s3)
seq3 = [4,5]
seq3 = None
seq3 = (4,5)
s1,s2 = seq3
print(s1,s2,s3)

# min/max and 'key' arg
blah = [1, 2, 3]
omkeer = lambda x: -x
print(min(blah), max(blah))
print(min(blah, key=omkeer), max(blah, key=omkeer))
print(min(1,2), max(1,2))
print(min(1,2, key=omkeer), max(1,2, key=omkeer))
print(min(1,2,3), max(1,2,3))
print(min(1,2,3, key=omkeer), max(1,2,3, key=omkeer))
print(min(1,2,3, key=int), max(1,2,3, key=str))

# zip()
zip0 = zip()
print(list(zip0))

# math.factorial
import math
for hm in range(13):
    print(math.factorial(hm), )
print()

# map 3 iterables of different types
def foo3(a, b, c):
    return '%d %.2f %s' % (a, b, c)
def flats():
    for x in range(3):
        yield chr(ord('A')+x)
print(list(map(foo3, range(3), map(float, list(range(1, 4))), flats())))


# dict(iter({str,pyseq}))
print(sorted(dict(['ab', 'cd']).items()))
print(sorted(dict(set([(1,2.0), (3,4.0)])).items()))
print(sorted(dict([[1,2], (3,4)]).items()))

# first-class booleans
bool_a = True
print(bool_a)
bool_a = not bool_a

bool_b = [bool_a, bool_a, True]
print(bool_b)

bool_c = bool_a + bool_a
print(bool_c)

bool_e = 7 > 8
print(bool_e)

if bool_e:
    print('e')
if not bool_e:
    print('!e')

queue = []
augmented = 0
if queue and not augmented:
    print('queue')

a_bool = bool('hoppa')
print(a_bool)

print(True & False, True & True, True & 1, 1 & False)
print(True-2, False*3, 2+True, 2-False, 4*True)

print(True*[1,2])

har3 = True & True & 1
print(har3)

niks = None
print(bool(niks), bool(None))

# generator expressions
ia = (2*x for x in range(10))
print(sum(ia))
ib = ((str(x+y) for x in range(10)) for y in range(4))
print([''.join(ur) for ur in ib])
ic = [(x+3 for x in range(10)) for y in range(4)]
print([sum(ar) for ar in ic])
id = ([2.0*(x+y) for x in range(10)] for y in range(4))
print(sum(sum(uhh) for uhh in id))
ie = ([x,y] for x in range(10) for y in range(4))
print(len(list(ie)))

class meuk:
    def layout(self):
        return (x for x in 'abc')

waf = meuk().layout()
print(list(waf))

# itertools.product fix
import itertools
print(list(itertools.product([0,1,2], [0,1,2])))
print(list(itertools.product([-1, 0, 1], repeat=2)))
print(list(itertools.product(iter([1, 2, 3]), iter([4, 5]), repeat = 2)))
print(list(itertools.product(iter([1, 2, 3]), iter([4, 5]), iter([6, 7, 8]), repeat = 2)))


#and,or mixing
1 or 'hoppa' or [1,2]
plb = 1 or 9
plc = not (1 or 9)
not (1 or 'hopsa')
pld = 1 and 9
ple = not (1 and 9)
if 1 or 'hoei':
    print('ba')
while 1 or 'hoei':
    print('uhoh')
    break
while (1 or ('blah' and 1)):
    break
print([plx for plx in range(4) if plx and 'hoei'])
print([plx for plx in range(4) if plx and 1])
if not (1 and 'hoei'):
    print('oh')

# copy, deepcopy and None
import copy

class TreeNode:
    def __init__(self):
        self.hoppa = [1]
        self.hoppa = None

tn = TreeNode()
tn2 = copy.deepcopy(tn)
blar = tn2.hoppa
blar2 = copy.copy(blar)

# SystemExit
import sys
try:
    exit(4)
except SystemExit as baratie:
    print('jaja deze ook')
try:
    sys.exit(4)
    sys.exit('hoppa')
    raise SystemExit()
except SystemExit as baratie:
    print('exit with', baratie.code, baratie)
    if False: # difference when run from this file
        sys.exit('aha')
        sys.exit(baratie.code)

# comparison model
class Bla:
    def __eq__(self, o):
        print(o.niks)
bla1 = Bla()
bla1 is None

# crash
print(None in [[None]])

# casting to builtins (inference not enough)
definiteinnerlist=[1]
outerlist=[[1]]
#emptyinnerlist=[]
outerlist.append(definiteinnerlist)
outerlist.append([])
outerlist[0] = []
print(outerlist)

dikkie={1:1}
dikkie2 = {1:dikkie}
dikkie2[2] = {}
dikkie2[3] = dikkie
print(sorted(dikkie2.items()))

# more test cases
#print(reduce(lambda a,b: a+b, '34'))
#print(reduce(lambda a,b: a+b, '345', '6'))
#print(reduce(lambda a,b: a+b, [3,5,7], 2))
#print(reduce(lambda a,b: a-b, set([3,5,7])))

print(any([1,2]), all([0,1]), any([]), all([]))
print(any(set([1,2])), all(set([0,1])), all({}))
print(any('  '), any(''), all('   '), all(''))

print([]==[[]])
print([]==None)
print(None==[[]])
print(None==[1])
print([None] == [[1]])
print([[1]] == [])
print([[]] == [[1]])
