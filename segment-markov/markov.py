# simple Markov model from letter frequencies

from nltk import ingrams
from nltk.probability import FreqDist, ConditionalFreqDist
import random

NGRAM_FILES = {1 : 'english_monograms.txt',
               2 : 'count_2l.txt',
               3 : 'count_3l.txt'}

def select_weighted(d):
    '''selects a random key from a dictionary
    using the values as weights
    '''
    offset = random.randint(0, sum(d.itervalues())-1)
    for k, v in d.iteritems():
       if offset < v:
           return k
       offset -= v

class MarkovModel(object):
    def __init__(self, order, string):
        self.order = order
        if self.order > 1:
            self.backoff = MarkovModel(order - 1, string)
            self.cfd = ConditionalFreqDist()
            self.charset = self.backoff.charset
            for ngram in ingrams(string, order):
                context, char = ngram[:-1], ngram[-1]
                self.cfd[context][char] += 1

        else:
            self.backoff = None
            self.n = 0
            self.fd = FreqDist(string)
            self.charset = set(self.fd.keys())


    def _generate_one(self, start):
        '''Takes iterable (string, tuple or list) and generate
        a new letter for a context of size n-1

        Trucuates larger contexts in accord with model order
        Backs off for smaller contexts
        '''
        
        if self.order > 1:
            context = tuple(start)[1-self.order:]
            if context in self.cfd:
                return select_weighted(self.cfd[context])
            else: # go to the backoff model
                return self.backoff._generate_one(context)
##                return self.backoff._generate_one(context[2-self.order:])
            
        else: # unigrams: there is only a frequency distribution
            return select_weighted(self.fd)

    def generate(self, start=tuple(), n=100):
        result = list(start)
        for i in range(n):
            context = tuple(result[1-self.order:])
            result.append(self._generate_one(context))
        return result



class MyMarkovModel(MarkovModel):
    def __init__(self, order):
        self.order = order
        self.filename = NGRAM_FILES[self.order]
       
        if 3 >= self.order >= 2:
            self.backoff = MyMarkovModel(order - 1)
            self.cfd = ConditionalFreqDist()
            self.charset = self.backoff.charset
            for ngram, count in self.get_data():
                context, char = tuple(ngram[:-1]), ngram[-1]
                self.cfd[context][char] = count

        elif self.order == 1:
            self.backoff = None
            self.n = 0
            self.fd = FreqDist()
            for char, count in self.get_data():
                self.fd[char] = count
            self.charset = set(self.fd.keys())

        else:
            raise NotImplemented

    def get_data(self):
        with open(self.filename) as fp:
            for line in fp.readlines():
                ngram, count = line.lower().split()
                count = int(count)
                yield ngram, count

def main():
    from ngrams import segment2
    m = MyMarkovModel(3)
    string = ''.join(m.generate())
    score, segmented = segment2(string)
    return ' '.join(segmented)

if __name__ == "__main__":
    print main()
    

                
