# -*- coding: utf-8 -*-
# by Alejandro Rojo Gualix 2021-06
""" ¿QUÉ QUIERO EXTRAER?
    WORDNET
        herencia. hiper
        implicación. entailment >>>>>>>>>> MÁS
        HAS meronimia
        NO sinonimia
    MÁS
        más implicaciones
        qualia télico
        tipos semánticos +ANIMADO -> vive, respira, nace, crece, muere

    ANIMAL eats breathes CANmovearound

implicación
A(x) -> B(x)
meronimia
A(x) -> HAS(x,y)

"""
import sys
import json
from collections import Counter
from itertools import count, chain

import nltk
from nltk.corpus import wordnet as wn


# from predicates.graph import Graph
import graph
import ontology.conceptNet as conceptNet
import ontology.extensionKB as extensionKB
with open('ontology/WordNet2SUMO_mappings.json', 'r', encoding='UTF-8') as f:
    wn_sumo = json.load(f)
with open('ontology/tuples_SUMO.json', 'r', encoding='UTF-8') as f:
    sumo_tuples = json.load(f)


# TIPOS SEMÁNTICOS
""" .CLOSURE

OBJETO
    NATURAL
        roca
        SER_VIVO 
            PERSONA
            ANIMAL
    ARTEFACTO
EVENTO FENÓMENO
CONTABLE
LUGAR
	city	108226335, 108524735
	country	108168978
	mount	109359803, 109403734
2333 group%1:03:00:: 1 &%Collection SUMO
building

physical_entity.n.01
    process.n.06
    object.n.01
        artifact.n.01
        natural_object.n.01
        +living_thing.n.01
        +person.n.01
        +animal.n.01

"""
semantic_restrictions = {
    # 'entity': wn.synset('entity.n.01'),
    'process': wn.synset('process.n.06'),
    'object': wn.synset('object.n.01'),

    'artifact': wn.synset('artifact.n.01'),
    'natural_object': wn.synset('natural_object.n.01'),
    'living_thing': wn.synset('living_thing.n.01'),
    'person': wn.synset('person.n.01'),
    'animal': wn.synset('animal.n.01'),

    'location': wn.synset('location.n.01'),

    'matter': wn.synset('matter.n.03'),
    'substance': wn.synset('substance.n.01'),
}


def hypo(synset, max_level=None, level=0):
    """
    Obtiene los hipónimos
    :param synset:
    :param max_level:
    :param level:
    :return: set()
    """
    tuple_set = set()
    if max_level and level == max_level:
        return set()
    # print('\t' * level, syn.name())
    # print('\t' * level, synset)
    for hyponym in synset.hyponyms():
        tuple_set.add((hyponym, synset))
        tuple_set.update(hypo(hyponym, max_level, level + 1))
    return tuple_set


def get_verb_roots():
    root_hypernyms_of_verbs = Counter(chain(*[synset.root_hypernyms() for synset in wn.all_synsets(pos='v')]))
    print(root_hypernyms_of_verbs.most_common(10))
    return root_hypernyms_of_verbs.keys()  # This will return all root_hypernyms.



def format_implication(tuples):
    print(json.dumps(tuples, indent=2))
    return
    # assert len(tuples) == len(set(tuples))
    [print(_[0].name() + ' -> ' + _[1].name()) for _ in tuples[0:20]]


class SumoNode(str):
    def __init__(self, term):
        str.__init__(self)
        self.term = term


class InferencesGraph(graph.Graph):
    def __init__(self, facts, max_level=None):
        graph.Graph.__init__(self)
        for fact in facts:
            self.create_node(fact, {'label': fact.name(), 'fontcolor': "violetred1"})
            # self.nodes[fact] = {}
            all_types_meronyms = fact.part_meronyms() + fact.substance_meronyms() + fact.member_holonyms()
            for meronym in all_types_meronyms[0:3]:
                self.add_node(fact, meronym, {'label': meronym.name(), 'fontcolor': "violetred1"}, 'parte')

        self.inference_loop(facts, max_level=max_level)

        # es importante que estoy vaya después de traverse_implications() para que se puedan analizar las relaciones de estos nodos
        for fact in facts:
            for semantic_restriction in semantic_restrictions.values():
                if semantic_restriction in set([hyp for hyp in fact.closure(lambda s: s.hypernyms())]):
                    self.add_node(fact,
                                  semantic_restriction, {'label': semantic_restriction.name(), 'fontcolor': "violetred1"},
                                  'rasgo', {'color': "red"})

    def add_node(self, node, new_node, node_properties, edge_label, edge_properties={'color': 'gray'}):
        add = new_node not in self.nodes
        if add:
            self.create_node(new_node, node_properties)
        self.add_edge(node, new_node, edge_label, edge_properties)
        return add

    def process(self, fact):
        pass

    def inference_loop(self, process_facts, max_level=None, level=0):
        if max_level and level == max_level:
            return

        # objetivo: no volver a procesar nodos ya procesados
        new_nodes = set()
        for fact in process_facts:
            # WORDNET sus datos se reconocen porque son de tipo Synset
            if isinstance(fact, nltk.corpus.reader.wordnet.Synset):
                for target in fact.hypernyms():
                    if self.add_node(fact, target, {'label': target.name(), 'fontcolor': "violetred1"}, 'es-un'):
                        new_nodes.add(target)  # avoid circularity

                # adjetives
                # strong.a.01 -> strength.n.01
                if fact.pos() == 'a':
                    for target in fact.attributes():
                        if self.add_node(fact, target, {'label': target.name(), 'fontcolor': "violetred1"}, 'attr'):
                            new_nodes.add(target)  # avoid circularity

                # verbs
                # implicación / entailment
                if fact.pos() == 'v':
                    for target in fact.entailments():
                        if self.add_node(fact,
                                         target, {'label': target.name(), 'fontcolor': "violetred1"},
                                         '→', {'color': "red"}):
                            new_nodes.add(target)  # avoid circularity

                # wordnet extension
                for antecedent, consequent in extensionKB.wordnet_inference_edges:
                    if fact == antecedent:
                        target = consequent
                        node_properties = {'label': target.name(), 'fontcolor': "violetred1", 'style': "filled", 'fillcolor': "bisque"}
                        if self.add_node(fact,
                                         target, node_properties,
                                         '→', {'color': "red"}):
                            new_nodes.add(target)  # avoid circularity

                # conceptNet
                # artifact use for
                if semantic_restrictions['artifact'] in set([hyp for hyp in fact.closure(lambda s: s.hypernyms())]):
                    print('\t', fact.name(), '->', fact.lemmas()[0].name(), fact.lemmas())
                    target = conceptNet.query(fact.lemmas()[0].name(), 'UsedFor')
                    if target and self.add_node(fact, target, {'label': target, 'fontcolor': "red"}, 'usado para'):
                            new_nodes.add(target)  # avoid circularity
                    target = conceptNet.query(fact.lemmas()[0].name(), 'CreatedBy')
                    if target and self.add_node(fact, target, {'label': target, 'fontcolor': "red"}, 'creado por'):
                            new_nodes.add(target)  # avoid circularity

                # localización
                target = conceptNet.query(fact.lemmas()[0].name(), 'AtLocation')
                if target and self.add_node(fact, target, {'label': target, 'fontcolor': "red"}, 'en'):
                        new_nodes.add(target)  # avoid circularity


                # connect with sumo
                name = fact.name()
                if name in wn_sumo:
                    print('>', name, wn_sumo[name])
                    target = wn_sumo[name][0]
                    target = SumoNode(wn_sumo[name][0])
                    # si no se hallan consecuentes ¿para qué añadirlo?
                    found = False
                    for antecedent, consequent in sumo_tuples:
                        if target == antecedent:
                            found = True
                            break
                    if not found:
                        continue
                    if self.add_node(fact, target, {'label': target, 'fontcolor': "blue"}, ''):
                        new_nodes.add(target)  # avoid circularity

            # elif isinstance(fact, str):  # SUMO sus datos son de tipo str
            elif isinstance(fact, SumoNode):  # SUMO sus datos son de tipo str
                name = fact
                for antecedent, consequent in sumo_tuples:
                    if name == antecedent:
                        if name in consequent:
                            if len(consequent) == 2:
                                continue
                            idx = consequent.index(name)
                            if idx == 1:
                                idx += 1
                            elif idx > 1:
                                idx -= 1
                            else:
                                continue
                            target = consequent[idx]
                            target = SumoNode(consequent[idx])
                        else:
                            target = consequent[1]
                            target = SumoNode(consequent[1])
                        print('>>>', name, consequent)
                        if self.add_node(fact, target, {'label': target, 'fontcolor': "blue"}, consequent[0]):
                            new_nodes.add(target)  # avoid circularity

        if new_nodes:  # recursion until nothing changes
            self.inference_loop(new_nodes, max_level, level + 1)



if __name__ == "__main__":
    # ss = wn.synset('car.n.01')
    # for lemma in ss.lemmas():
    #     print(lemma.name())
    # sys.exit(0)
    # facts = wn.synsets('cerveza', lang='spa')[0:1]
    # print(facts)

    # predicados de valencia 1
    facts = {wn.synset('snore.v.01'), wn.synset('car.n.01'), wn.synset("thunder.n.02"), wn.synset('rock.n.01'), wn.synset('deer.n.01')}
    ig = InferencesGraph(facts)
    ig.visualize()

    # subgraphs = [list(ig.nodes.keys())[:4], list(ig.nodes.keys())[4:10]]
    # formatted = ig.dot_graph_subgraph_format(subgraphs)
    # ig.visualize_string(formatted)


""" WN -> SUMO ¿¿??
natural_object.n.01 ['Artifact']
electrical_discharge.n.01 ['Radiating']
physical_phenomenon.n.01 ['IntentionalProcess']

> car.n.01 ['Automobile']
> motor_vehicle.n.01 ['Automobile']
> whole.n.02 ['CorpuscularObject']
event.n.01 ['Process']
"""