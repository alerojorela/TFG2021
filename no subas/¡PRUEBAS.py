# -*- coding: utf-8 -*-
# by Alejandro Rojo Gualix 2021-06
import sys
import re
# import spacy
from nltk.corpus import wordnet as wn
# print('😱 not implemented')
from itertools import count

# import semantics
from utils import functions

from collections import Counter
from itertools import chain



from nltk.corpus import cess_esp as cess

# Read the corpus into a list,
# each entry in the list is one sentence.
# cess_sents = cess.tagged_sents()
# sent = cess_sents[0:50]
sentences = cess.sents()  # [0:100]
for sentence in sentences:
    if len(sentence) < 10:
        print(' '.join(sentence))

sys.exit(0)




print('\n************** MERONIMIA ************** ')
meronyms_tuples = []
for synset in wn.all_synsets(pos='n'):
    # .member_holonyms() .part_holonyms() .substance_holonyms()
    all_types_meronyms = synset.part_meronyms() + synset.substance_meronyms() + synset.member_holonyms()
    for meronym in all_types_meronyms:
        meronyms_tuples.append((synset, meronym))

print('\n************** MERONIMIA ************** ')
[print(_[0].name() + ' HAS ' + _[1].name()) for _ in meronyms_tuples[0:100]]




# https://www.howtobuildsoftware.com/index.php/how-do/4EO/python-nlp-wordnet-get-noun-from-verb-wordnet
def nounify(verb_word):
    set_of_related_nouns = set()
    for lemma in wn.lemmas(wn.morphy(verb_word, wn.VERB), pos="v"):
        for related_form in lemma.derivationally_related_forms():
            for synset in wn.synsets(related_form.name(), pos=wn.NOUN):
                # if wn.synset('person.n.01') in synset.closure(lambda s:s.hypernyms()):
                set_of_related_nouns.add(synset)
    return set_of_related_nouns


# verb_groups
print('*' * 150)
print('* ', 'verb_groups')
# unhashabble
# verb_groups = {synset.verb_groups() for synset in wn.all_synsets(pos='v')}
# print(verb_groups)

# FRAMES
for lemma in wn.synset('think.v.01').lemmas():
    print(lemma, lemma.frame_ids(), " | ".join(lemma.frame_strings()))  # Something think something Adjective/Noun | Somebody think somebody


# DERIVACIÓN
palabra = 'create'
derived = {synset for lemma in wn.lemmas(wn.morphy(palabra, wn.VERB), pos="v") for related_form in lemma.derivationally_related_forms() for synset in wn.synsets(related_form.name())}
print(derived)
derived = nounify(palabra)
print(derived)
# [print(_) for _ in derived]
lemmas = wn.lemmas('creation')
for lemma in lemmas:
    related_forms = lemma.derivationally_related_forms()
    print(related_forms)


# ADJETIVOS
aaaa = [synset for synset in wn.all_synsets(pos='a')]
# aaaa = Counter(chain(*[synset.root_hypernyms() for synset in wn.all_synsets(pos='a')]))
# comunes = aaaa.most_common(10)
# print(comunes)

lem=wordnet.synset('good.a.01').lemmas()[0]
lem.antonyms()  # [Lemma('bad.a.01.bad')]
# similar to (also for adjective satellites)
wordnet.synset('strong.a.01').similar_tos()  # [Synset('beardown.s.01'), Synset('beefed-up.s.01'), Synset('brawny.s.01'), Synset('bullnecked.s.01'), Synset('bullocky.s.01'), Synset('fortified.s.02'), Synset('hard.s.04'), Synset('industrial-strength.s.01'), Synset('ironlike.s.01'), Synset('knock-down.s.01'), Synset('noticeable.s.04'), Synset('reinforced.s.01'), Synset('robust.s.03'), Synset('stiff.s.02'), Synset('vehement.s.02'), Synset('virile.s.01'), Synset('well-knit.s.01')]
# pertainyms (can be nouns or other adjectives). Concepts(synsets) that pertain to the given synset
lem=wordnet.synset('technical.a.01').lemmas()[0]
lem.pertainyms()  # [Lemma('technique.n.01.technique')]
# attributes (relation to noun synsets)
wordnet.synset('strong.a.01').attributes()  # [Synset('strength.n.01')]

# ADVERBIOS
# lem.antonyms()
# lem.pertainyms()

# how specific a certain word is, by analyzing it’s depth in a hierarchy
wn.synset('entity.n.01').min_depth()




sys.exit(0)


def hyp_recursive(synset, level = 0):
    ancestors = synset.hypernyms()
    for hyp in ancestors:
        ancestors.extend(hyp_recursive(hyp, level + 1))
    return ancestors

def hyp_recursive2(synset, level = 0):
    hyps = synset.hypernyms()
    ancestors = synset.hypernyms()
    if len(hyps) > 1:
        [print('\t' * level, hyp.lemma_names(), hyp.definition()) for hyp in hyps]
        raise ValueError('más de un hiperónimo')

    for hyp in hyps:
        ancestors.extend(hyp_recursive(hyp, level + 1))
        
    return ancestors

tests = [
    ('coche', 'automóvil'),
    ('animal', 'rata'),
    ('casa', 'edificio'),
    ('edificio', 'casa'),
    ('casa', 'comedor'),
    ('casa', 'puerta'),
    ('casa', 'ventana'),
    ('habitación', 'puerta'),
    ('habitación', 'ventana'),
    ('coche', 'ventana'),
    ('lectura', 'libro'),
    ('escritor', 'libro'),
]
[print(word1, word2, '\t', semantics.find_semantic_relation(word1, word2)) for word1, word2 in tests]



pat = r'(?:ción|mi?ento|aj[eo]|encia|ura|zón|dora?|der[ao])$'
regex = re.compile(pat)
print(regex, type(regex))
if isinstance(regex, re.Pattern):
    print('wiiiii')
print(regex.search('contención'))

sys.exit(0)


def f(arg):
    print('¡f!' + arg)

d = {'a': f, 'b': 2}

d['a'](' yepppa')

if callable(f):
    print('<<<<<<<<<<<<<<<<<<<<<<<<')

sys.exit(0)

format_pattern_regex = r'\d+'
# patterns like '0 < 3 1 >'
def format_pattern(pattern: str, values: list):
    output = ''
    last_pos = 0
    for match in re.finditer(format_pattern_regex, pattern):
        index = int(match.group())
        replacement = values[index] if (index < len(values) and values[index] is not None) else ''
        output += pattern[last_pos:match.start()] + replacement
        last_pos = match.end()
    output += pattern[last_pos:]
    print(output)


pattern = '0 < 3 1 >'
format_pattern(pattern, ['a', 'b', 'c'])

sys.exit(0)


def ab(num):
    if num % 3:
        return 0
    else:
        return None

print([ab(num) for num in range(0, 10)])

sys.exit(0)

strawberry = [] * 10
print(strawberry)
aList = [123, 'xyz', 'zara', 'abc']
aList.insert(13, 2009)
aList[14:15] = 'asdfs'
# aList[14] = 'asdfs'
print(aList)

pasiva = { 'name': 'pasiva', 'dep': 'aux', 'lemma': 'ser', 'predicate': '{0} < {3} {1} >',
    'pattern': {  # La casa fue arruinada por el fuego
        'pos': ['VERB'], 'pattern': [
            { 'dep': ['nsubj', 'iobj'] }, # puede tener muchos complementos "el libro fue regalado a Juan por Marta"
            { 'dep': 'aux', 'lemma': 'ser' },
            { 'pattern': [
                { 'dep': 'case', 'lemma': 'por' }
            ]
            }
        ]
    }
}     

def print_dict(obj):
    for key, value in obj.items():
        if key != 'pattern' and key != 'predicate':
            print(f'{key}: {value}', end='\t')


print_dict(pasiva)

sys.exit(0)

import re

s = re.search(r'do$', 'imprimido')
print(s is not None)

ds = re.sub(r'do$', 'r', 'imprimido')
print(ds)

predicate = r'< {0} {1} > {2} '
predicate = r'{2} < {0} {1} >'
arr = ['supermercado', 'esquina', 'de']
print(predicate.format(*arr))


# from __future__ import print_function
from nltk.featstruct import FeatStruct
from nltk.sem.logic import Variable, VariableExpression, Expression

 
fs1 = FeatStruct(pasiva)
print(fs1)

fs1 = FeatStruct(number='singular', person=3)
print(fs1)