from __future__ import print_function

# __init__ not called
from testdata import Material

# ugly imports
from testdata.bert193 import *
print(os.getcwd(), len(sys.argv))

# isinstance problem
from testdata.bert193 import zeug
print(isinstance(zeug(), zeug))

# dict corruption
x = 62
S = {}
t2 = (-25,9)
for i in range(-x, x+1):
   for j in range(-x, x+1):
       S[i, j] = 'hi'
if t2 in S:
    print("we got 'em")

# cast subtype in container
class Bla:
    pass
class Sub(Bla):
    pass
blas = [Bla()]
blas = [Sub()]

# generator and FAST_FOR_NEG
def gen(s):
    for i in range(1,10,s):
        yield i

for i in gen(2):
    print(i)

