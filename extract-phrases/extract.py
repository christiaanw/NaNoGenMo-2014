#!/usr/bin/python
import re
import random
from pattern.search import Pattern, STRICT, search
from pattern.en import parsetree, wordnet

import os
import glob
import fnmatch
import zipfile

# To remove legalese from Project Gutenberg etexts
# Regexes stolen from https://github.com/leonardr/In-Dialogue

START = re.compile("Start[^\n]*Project Gutenberg", re.I)
END = re.compile("End[^\n]*Project Gutenberg", re.I)

def clean_gutenberg(text):
    start, start2 = START.search(text).span()
    end, end2 = END.search(text, start2+2048).span()
    return text[start2:end]

# Functions stolen from https://github.com/antiboredom/patent-generator

def re_search(text, search_string, strict=False):
    tree = parsetree(text, lemmata=True)
    if strict:
        results = search(search_string, tree, STRICT)
    else:
        results = search(search_string, tree)
    return results


def search_out(text, search_string, strict=False):
    results = re_search(text, search_string, strict)
    output = []
    for match in results:
        sent = []
        for word in match:
            sent.append(word.string)
        output.append(" ".join(sent))
    return output

def contains(text, search_string):
    results = re_search(text, search_string)
    return len(results) > 0

def hypernym_search(text, search_word):
    output = []
    synset = wordnet.synsets(search_word)[0]
    pos = synset.pos
    possible_words = re_search(text, pos)
    for match in possible_words:
        word = match[0].string
        synsets = wordnet.synsets(word)
        if len(synsets) > 0:
            hypernyms = synsets[0].hypernyms(recursive=True)
            if any(search_word == h.senses[0] for h in hypernyms):
                output.append(word)
    return set(output)


def hypernym_combo(text, category, search_pattern):
    possibilities = search_out(text, search_pattern)
    output = []
    for p in possibilities:
        if len(hypernym_search(p, category)) > 0:
            output.append(p)
    return output


def list_hypernyms(search_word):
    output = []
    for synset in wordnet.synsets(search_word):
        hypernyms = synset.hypernyms(recursive=True)
        output.append([h.senses[0] for h in hypernyms])
    return output


def random_hyponym(word):
    to_return = ''
    hyponyms = list_hyponyms(word)
    if len(hyponyms) > 0:
        to_return = random.choice(hyponyms)
    return to_return


def list_hyponyms(word):
    output = []
    synsets = wordnet.synsets(word)
    if len(synsets) > 0:
        hyponyms = synsets[0].hyponyms(recursive=True)
        output = [h.senses[0] for h in hyponyms]
    return output

REGEX = re.compile(r'\r\nLanguage: English\r\n')

if __name__ == '__main__':
##    root = os.getcwd()
    root = '/path/to/unpacked/gutenberg/iso'
    for path, dirs, files in os.walk(root):
        for zfilename in fnmatch.filter(files, '*.ZIP'):
            zfilepath = os.path.join(path, zfilename)
            zfile = zipfile.ZipFile(zfilepath)
            for filename in fnmatch.filter(zfile.namelist(), '*.txt'):
                string = zfile.read(filename)
                if REGEX.search(string) is not None:
                    text = clean_gutenberg(string)
                    for result in set(hypernym_combo(text, 'organism', 'JJ NN')):
                        try:
                            with open('persons.txt', 'a') as f:
                                f.write(result + '\n')
                        except UnicodeEncodeError:
                            pass
                    for result in set(search_out(text, 'VBG IN NN')):
                        try:
                            with open('actions.txt', 'a') as f:
                                f.write(result + '\n')
                        except UnicodeEncodeError:
                            pass

                    for result in set(search_out(text, 'VBG DT NN')):
                        try:
                            with open('actions.txt', 'a') as f:
                                f.write(result + '\n')
                        except UnicodeEncodeError:
                            pass
