# version code 988
# Please fill out this stencil and submit using the provided submission script.

import random
from GF2 import one
from vecutil import list2vec
from independence import GF2_rank


## Problem 1
def randGF2(): return random.randint(0,1)*one

a0 = list2vec([one, one,   0, one,   0, one])
b0 = list2vec([one, one,   0,   0,   0, one])

def random_6_vec():
    return list2vec([randGF2() for index in range(6)])

def choose_secret_vector(s,t):
    done = False
    result = random_6_vec()
    while not done:
        if ((result*a0 == s) and (result*b0 == t)):
            done = True
        else:
            result = random_6_vec()
    return result

def test_3_pairs(pairs):
    ##print(len(pairs))
    ##print(pairs)
    result = True;
    if (len(pairs) <= 6):
        result = result and (GF2_rank(pairs) == len(pairs))
    else:
        for remove in range(int(len(pairs)/2)):
            if (remove == 0):
                result = result & test_3_pairs(pairs[2:])
            elif (remove == (len(pairs) - 1)):
                result = result & test_3_pairs(pairs[:2*remove])
            else:
                result = result & test_3_pairs(pairs[:2*remove] + pairs[2*remove + 2:])
    return result
        

def additional_pair(existing_vecs):
    done = False
    (a,b) = (random_6_vec(), random_6_vec())
    while not done:
        test_vecs = existing_vecs + [a, b]
        if (test_3_pairs(test_vecs)):
            done = True
        else:
            (a,b) = (random_6_vec(), random_6_vec())
    return (a,b)

## Problem 2
# Give each vector as a Vec instance
secret_a0 = list2vec([one, one,   0, one,   0, one])
secret_b0 = list2vec([one, one,   0,   0,   0, one])
(secret_a1, secret_b1) = additional_pair([secret_a0, secret_b0])
##print(secret_a1)
##print (secret_b1)
(secret_a2 , secret_b2) = additional_pair([secret_a0, secret_b0, secret_a1, secret_b1])
##print(secret_a2)
##print(secret_b2)
(secret_a3 , secret_b3) = additional_pair([secret_a0, secret_b0, secret_a1, secret_b1, secret_a2, secret_b2])
##print(secret_a3)
##print(secret_b3)
(secret_a4 , secret_b4) = additional_pair([secret_a0, secret_b0, secret_a1, secret_b1, secret_a2, secret_b2, secret_a3, secret_b3])
##print(secret_a4)
##print(secret_b4)

