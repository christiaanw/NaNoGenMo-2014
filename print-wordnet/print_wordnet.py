#!/bin/env/python

import sys
from nltk.corpus import wordnet as wn
from pattern.en import referenced


def sentence(string):
    sent = string[:1].upper() + string[1:]
    if not sent.endswith('. '):
        sent += '. '
    sent = sent.replace('_', ' ')
    return sent    

def enum_or(words):
    if len(words) == 1:
        return referenced(words[0])     

    r = [referenced(w) for w in words]
    return '{0}, or {1}'.format(', '.join(r[:-1]), r[-1])

def describe(synset):
    names = synset.lemma_names
    name = referenced(names[0])
    definition = synset.definition.strip()
    string = "{0} is {1}".format(name, definition)
    if len(names) > 1:
        string += ', also known as {0}'.format(enum_or(names[1:]))
    return sentence(string)

def specify(synset, hyponyms):
    name = referenced(synset.lemma_names[0])
    string = name
    hyp_names = [s.lemma_names[0] for s in hyponyms]
    if len(hyp_names) == 1:
        string += ' can, more specifically, be a {0}'.format(hyp_names[0])
    else:
        string += ' is either {0}. '.format(enum_or(hyp_names))
    return sentence(string)

def generate(synset):
    string = str()
    string += describe(synset)
    hyponyms = synset.hyponyms()
    if hyponyms:
        string += specify(synset, hyponyms)
    string += '\n\n'
    for h in hyponyms:
        string += generate(h)
    return string

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Usage: %s word outputfile.txt' % sys.argv[0])
    
    root = wn.synsets(sys.argv[1])[0]
    
    with open(sys.argv[2], "w") as fp:
        fp.write(generate(root).encode('utf-8'))
