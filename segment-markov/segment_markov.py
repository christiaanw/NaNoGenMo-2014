"""
Parts of this code copyright (c) 2008-2009 by Peter Norvig,
downloaded from norvig.com/ngrams

That code came under the MIT licencse: 
http://www.opensource.org/licenses/mit-license.php
"""

import re, string, random, glob, operator, heapq
from collections import defaultdict
from math import log10

def memo(f):
    "Memoize function f."
    table = {}
    def fmemo(*args):
        if args not in table:
            table[args] = f(*args)
        return table[args]
    fmemo.memo = table
    return fmemo


################ Word Segmentation (p. 223)

@memo
def segment(text):
    "Return a list of words that is the best segmentation of text."
    if not text: return []
    candidates = ([first]+segment(rem) for first,rem in splits(text))
    return max(candidates, key=Pwords)

def splits(text, L=20):
    "Return a list of all possible (first, rem) pairs, len(first)<=L."
    return [(text[:i+1], text[i+1:]) 
            for i in range(min(len(text), L))]

def Pwords(words): 
    "The Naive Bayes probability of a sequence of words."
    return product(Pw(w) for w in words)

#### Support functions (p. 224)

def product(nums):
    "Return the product of a sequence of numbers."
    return reduce(operator.mul, nums, 1)

class Pdist(dict):
    "A probability distribution estimated from counts in datafile."
    def __init__(self, data=[], N=None, missingfn=None):
        for key,count in data:
            self[key] = self.get(key, 0) + int(count)
        self.N = float(N or sum(self.itervalues()))
        self.missingfn = missingfn or (lambda k, N: 1./N)
    def __call__(self, key): 
        if key in self: return self[key]/self.N  
        else: return self.missingfn(key, self.N)

def datafile(name, sep='\t'):
    "Read key,value pairs from file."
    for line in file(name):
        yield line.split(sep)

def avoid_long_words(key, N):
    "Estimate the probability of an unknown word."
    return 10./(N * 10**len(key))

N = 1024908267229 ## Number of tokens

Pw  = Pdist(datafile('count_1w.txt'), N, avoid_long_words)

#### segment2: second version, with bigram counts, (p. 226-227)

def cPw(word, prev):
    "Conditional probability of word, given previous word."
    try:
        return P2w[prev + ' ' + word]/float(Pw[prev])
    except KeyError:
        return Pw(word)

P2w = Pdist(datafile('count_2w.txt'), N)

@memo 
def segment2(text, prev='<S>'): 
    "Return (log P(words), words), where words is the best segmentation." 
    if not text: return 0.0, [] 
    candidates = [combine(log10(cPw(first, prev)), first, segment2(rem, first)) 
                  for first,rem in splits(text)] 
    return max(candidates) 

def combine(Pfirst, first, (Prem, rem)): 
    "Combine first and rem results into one (probability, words) pair." 
    return Pfirst+Prem, [first]+rem

# Generating a Markov string

def select_weighted(d):
    '''selects a random key from a dictionary
    using the values as weights
    '''
    offset = random.randint(0, sum(d.itervalues())-1)
    for k, v in d.iteritems():
       if offset < v:
           return k
       offset -= v

fd = {}
cfd = defaultdict(dict)

for ngram, count in datafile('count_3l.txt'):
    fd[ngram] = int(count)
    cfd[ngram[:-1]][ngram[-1]] = int(count)

result = select_weighted(fd)
for i in range(100):
    context = result[-2:]
    result += select_weighted(cfd[context])

print result
print segment(result)
print segment2(result)


