from pattern.en import referenced
import random
import subprocess

with open('persons.txt') as f:
    persons = f.read().split('\n')

with open('actions.txt') as f:
    actions = f.read().split('\n')

random.shuffle(persons)
random.shuffle(actions)

text = '''% CONSIDER A NOVEL
# Chapter 1
Consider '''
text += ', or '.join(referenced(p) for p in persons)
text += ' who is '
text += ', '.join(actions)
text += '.'

with open('novel.md', 'w') as f:
    f.write(text) 

subprocess.call('pandoc -o novel.pdf novel.md')
