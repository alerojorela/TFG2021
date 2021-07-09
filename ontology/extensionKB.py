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

# wordnet entailments. sólo para verbos
# entailment_tuples = [(synset, ent) for synset in wn.all_synsets(pos='v') for ent in synset.entailments()]
# print(entailment_tuples)

