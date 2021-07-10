from nltk.corpus import wordnet as wn

# lema en español → [synset1, …, synsetN]
wordnet_synset_expansion = {  # implementation or corrections
    'trueno': [wn.synset('thunder.n.02')],
    'roncar': [wn.synset('snore.v.01')],
}

# antecedent → consequent
# (antecedent, consequent)
wordnet_inference_edges = [
    (wn.synset('snore.v.01'), wn.synset('snore.n.01')),  # para implicar el ruido
    # (wn.synset('snore.v.01'), wn.synset('sleep.v.01')),

    (wn.synset('breathe.v.01'), wn.synset('live.v.04')),
    (wn.synset('living_thing.n.01'), wn.synset('live.v.04')),
    (wn.synset('living_thing.n.01'), wn.synset('be_born.v.01')),
    (wn.synset('living_thing.n.01'), wn.synset('die.v.01')),

    (wn.synset('person.n.01'), wn.synset('mammal.n.01')),

    # (wn.synset(''), wn.synset('')),
]

""" wordnet entailments. sólo para verbos
entailment_tuples = [(synset, ent) for synset in wn.all_synsets(pos='v') for ent in synset.entailments()]
print(entailment_tuples)
"""


"""
    [print(synset.name(), synset.lemma_names(), synset.definition()) for synset in wn.synsets('author')]
    [print(synset.name(), synset.lemma_names(), synset.definition()) for synset in wn.synsets('book')]
    writer.n.01 ['writer', 'author'] writes (books or stories or articles or the like) professionally (for pay)
    author.v.01 ['author'] be the author of
    book.n.01 ['book'] a written work or composition that has been published (printed on pages bound together)
    book.n.02 ['book', 'volume'] physical objects consisting of a number of pages bound together
"""
qualia = {
    'book.n.01': {
        'agentive': 'writer.n.01',
        'telic': 'read.n.01',
    },
}
