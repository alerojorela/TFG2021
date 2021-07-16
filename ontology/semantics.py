# -*- coding: utf-8 -*-
# by Alejandro Rojo Gualix 2021-06

import nltk
from nltk.corpus import wordnet as wn
# MÍOS
import predicates.morphology as morphology
import predicates.graphs as graphs
import ontology.extensionKB as extensionKB

# principales categorías nominales consideradas
matter_syn = wn.synset('matter.n.03')
substance_syn = wn.synset('substance.n.01')
person_syn = wn.synset('person.n.01')
location_syn = wn.synset('location.n.01')


# synset deambiguation is difficult and not implemented
def get_term_features(term, debug_function=False):
    if isinstance(term, str):
        word = term.lower()
        is_location = None
        is_person = None
    else:
        word = term.properties['lemma']
        ent_type = term.ref_object.ent_type_
        if debug_function: print('\t\tent_type_ ', word, ent_type)
        is_location = ent_type == 'LOC'
        is_person = ent_type == 'PER'

    if is_location is None or not is_location:
        is_location = has_ancestor(word, location_syn)
    if is_person is None or not is_person:
        is_person = word in morphology.lemas_posesivos or has_ancestor(word, person_syn)
    is_matter = has_ancestor(word, matter_syn)
    is_substance = has_ancestor(word, substance_syn)

    result = {'is_location': is_location, 'is_person': is_person,
              'is_matter': is_matter, 'is_substance': is_substance}
    if debug_function: print('\t\t', word, result)
    return result


def has_ancestor(term, ancestor):
    if isinstance(term, nltk.corpus.reader.wordnet.Synset):
        # .hypernym_paths()[0] because returns a nested list [[s1, s2, ..., sN]]
        return ancestor in term.hypernym_paths()[0]
    else:
        word = str(term)
        return any([has_ancestor(syn, ancestor) for syn in wn.synsets(word, lang='spa')])


def is_synonym(syn1, syn2):
    if syn1 == syn2:
        return {'score': 0.9, 'relation': 'is_synonym', 'synsets': (syn1, syn2)}
    # return syn1 == syn2


def is_hypernym(syn1, syn2):
    if is_synonym(syn1, syn2):
        return
    # cuál es su hiperónimo común, siempre hay uno: en el caso más genérico es Synset('entity.n.01')
    lch = syn1.lowest_common_hypernyms(syn2)
    # cuanto más distante menos puntuación 1/distsancia
    # hyp2 = syn2.hypernym_paths()
    # print(lch)
    # otra cosa es que uno sea el hiperónimo común
    """
    casa edificio
    >>>>>>>>>>>>>>>1 {Synset('building.n.01'): 0, Synset('structure.n.01'): 1, Synset('artifact.n.01'): 2, Synset('whole.n.02'): 3, Synset('object.n.01'): 4, Synset('physical_entity.n.01'): 5, Synset('entity.n.01'): 6, Synset('*ROOT*'): 7}
    print('>>>>>>>>>>>>>>>2', syn2.path_similarity(syn1))
    print('>>>>>>>>>>>>>>>2', syn2.lch_similarity(syn1))
    print('>>>>>>>>>>>>>>>2', syn2.wup_similarity(syn1))
    >>>>>>>>>>>>>>>2 0.5
    >>>>>>>>>>>>>>>2 2.9444389791664407
    >>>>>>>>>>>>>>>2 0.9333333333333333
    """
    if syn1 in lch:  # syn1 es el hiperónimo
        return {'score': syn2.path_similarity(syn1), 'relation': 'is_hypernym', 'synsets': (syn1, syn2)}
    if syn2 in lch:  # syn2 es el hiperónimo
        return {'score': syn2.path_similarity(syn1), 'relation': 'is_hypernym', 'synsets': (syn1, syn2)}


def is_meronym(syn1, syn2):
    # [print(lemma_name) for meronym in syn1.part_meronyms() for lemma_name in meronym.lemma_names('spa') ]
    # print(syn1.part_meronyms(), syn2.part_meronyms())
    if syn2 in syn1.part_meronyms() or syn1 in syn2.part_meronyms() or syn2 in syn1.substance_meronyms() or syn1 in syn2.substance_meronyms():
        return  {'score': 0.5, 'relation': 'is_meronym', 'synsets': (syn1, syn2)}
    # return syn2 in syn1.part_meronyms() or syn1 in syn2.part_meronyms() or syn2 in syn1.substance_meronyms() or syn1 in syn2.substance_meronyms()



def is_qualia(syn1, syn2):
    # [print(lemma_name) for meronym in syn1.part_meronyms() for lemma_name in meronym.lemma_names('spa') ]
    # print(syn1.part_meronyms(), syn2.part_meronyms())
    name1 = syn1.name()
    name2 = syn2.name()
    qualia = extensionKB.qualia
    if (name1 in qualia and (qualia[name1]['agentive'] == name2 or qualia[name1]['telic'] == name2)) or \
            (name2 in qualia and (qualia[name2]['agentive'] == name1 or qualia[name2]['telic'] == name1)):
        return {'score': 0.5, 'relation': 'is_qualia', 'synsets': (syn1, syn2)}
    # return (name1 in qualia and (qualia[name1]['agentive'] == name2 or qualia[name1]['telic'] == name2)) or (name2 in qualia and (qualia[name2]['agentive'] == name1 or qualia[name2]['telic'] == name1))
    # return (name1 in agentive_qualia and agentive_qualia[name1] == name2) or (name2 in agentive_qualia and agentive_qualia[name2] == name1) or (name1 in telic_qualia and telic_qualia[name1] == name2)or (name2 in telic_qualia and telic_qualia[name2] == name1)


# returns a list of tuples, each tuple (result, pair)
def process_combinations(list1, list2, function):
    output = []
    for item1 in list1:
        for item2 in list2:
            result = function(item1, item2)
            if result:  # filter None items
                result = ( result, (item1, item2) )  # etiqueta, este es el motivo por el que no basta con usar una list comprehension
                output.append(result)
    return output


# todo esto ELUDE LA DIFICULTAD DE LA DESAMBIGUACIÓN léxica
def process_combinations_synsets(word1, word2, function):
    synsets1 = wn.synsets(word1, lang='spa')
    synsets2 = wn.synsets(word2, lang='spa')
    return process_combinations(synsets1, synsets2, function)


# todo esto ELUDE LA DIFICULTAD DE LA DESAMBIGUACIÓN léxica
# escoge el que tenga mayor valor
# combina todos los predicados entre sí, y llama con las tuplas a esta función.
# Y este llama para combinar todos los synsets posibles
def find_semantic_relation(word1, word2):
    # print(word1, word2)
    if word1 == word2:
        return {'score': 1, 'relation': 'identity'}
    else:  # different form
        synsets1 = wn.synsets(word1, lang='spa')
        synsets2 = wn.synsets(word2, lang='spa')
        candidates = []
        candidates.extend(process_combinations(synsets1, synsets2, is_synonym))
        candidates.extend(process_combinations(synsets1, synsets2, is_hypernym))
        candidates.extend(process_combinations(synsets1, synsets2, is_meronym))
        candidates.extend(process_combinations(synsets1, synsets2, is_qualia))

        candidates = [_[0] for _ in candidates if _]  # remove None items and strip combination tuple

        if len(candidates) == 1:
            return candidates[0]
        elif len(candidates) > 1:
            maximum = max([_['score'] for _ in candidates])
            return [_ for _ in candidates if _['score'] == maximum][0]


#region "desambigüación de 'de'"
""" funciones de DE
    es muy difícil determinar el antecedente, que no ha de ser inmediato
    se requiere ontología

    tipos de relaciones que establece DE(arg1, arg2)
        merónimos
            material
            parte
        entidades o no
            lugar
            persona
                posesión
        qualias o argumentos

    ejemplo "La tapa de latón de la caja de agujas de coser de mi tía de Toledo"
        ESTAR_HECHO_DE < tapa latón >
        TENER < tapa caja >
        POSEER < tía ¿caja/tapa? >
        TENER < mi tía >
        EN/ORIGEN < tía Toledo >
        qualias o argumentos:
            SERVIR_PARA < agujas coser >
            CONTENER < caja agujas >

    OTRAS
        más los complementos oblicuos surgidos de la nominalización de los complementos de una suboración
            la ruptura DE las relaciones
            CONTENER < caja agujas >    <<<<<<< PREDICADO NOMINAL caja(continente, contenido)
        adjetivo enfatizado? "El imbécil/cerdo de Arnaldo" El cerdo Arnaldo
        determinantes, restricción de conjunto previo
            "uno de esos barrios ricos"

    ¿diferencias entre POSEER Y TENER?
        TENER +-animado +-alienable
            POSEER +-animado +alienable
                * poseo un ojo
                poseo un coche
                el edificio posee un sistema antincendios
"""


def precisa_de(predicate):
    """
    evaluaciones sobre segundo término
        la casa de Segovia
        la casa de Juana
        la casa de piedra

    evaluaciones conjuntas
        la puerta de la casa
    CON
        vecino con coche
        casa con jardín
    """
    debug_function = True
    if debug_function: print('\tDESAMBIGUANDO "DE"')

    word1 = str(predicate.arguments[0])
    word2 = str(predicate.arguments[1])

    meronyms = [meronym for syn in wn.synsets(word2, lang='spa') for meronym in syn.part_meronyms()]
    if debug_function: print('\t\tmeronyms', word2, meronyms)
    is_part = any([syn in meronyms for syn in wn.synsets(word1, lang='spa')])

    reverse_arguments = False
    features = get_term_features(predicate.arguments[1], debug_function)  # segundo argumento
    if features['is_location']:
        label = 'DE->EN'
    elif features['is_person']:
        reverse_arguments = True
        label = 'DE->POSEER'
    elif features['is_substance']:  # is_matter juego de mesa
        label = 'DE->HECHO_DE'
    elif is_part:
        reverse_arguments = True
        label = 'DE->TENER'
    else:
        label = 'DE'

    if predicate.functor is None:
        # properties['lemma'].upper()
        current_token_position = predicate.arguments[0].properties['text_index']
        properties = {'lemma': 'de', 'text': 'de', 'old_lemma': 'de', 'pos': 'ADP', 'text_index': current_token_position}
        predicate.functor = graphs.MyNode(label, properties)
    elif predicate.functor.label == 'con':
        predicate.functor.label = 'CON->TENER'  # [0] debe ser persona
        reverse_arguments = False
    elif predicate.functor.label == 'sin':
        predicate.functor.label = 'SIN->TENER'  # [0] debe ser persona
        reverse_arguments = False
    else:
        predicate.functor.label = label

    if reverse_arguments:
        predicate.arguments = predicate.arguments[::-1]  # invierte los argumentos


if __name__ == "__main__":
    desambigua_de('supermercado', 'esquina')
    desambigua_de('supermercado', 'pueblo')
    desambigua_de('pata', 'mesa')
    desambigua_de('tapa', 'caja')
    desambigua_de('vasija', 'barro')
    sys.exit(0)

    test_words = 'tío, vecino, ingeniero, presidente, padre, chica, pantalón, pollo, dios, hormiga, lagartija'
    for word in test_words.split(', '):
        # if debug: print(word, [syn.hypernym_paths()[0] for syn in wn.synsets(word, lang='spa')])
        is_person = [person_syn in syn.hypernym_paths()[0] for syn in wn.synsets(word, lang='spa')]
        if debug: print(word, any(is_person))

    # tests
    # [v] tío True
    # [v] vecino True
    # [v] ingeniero True
    # [v] presidente True
    # [v] padre True
    # [v] chica True
    # [v] pantalón False
    # [ ] pollo True
    # [ ] dios True
    # [v] hormiga False
    # [v] lagartija False

    # tests
    test_words = 'latón, zinc, vidrio, papel, mesa, roble, música, letra, aire, oxígeno, dios'
    for word in test_words.split(', '):
        # if debug: print(word, [syn.hypernym_paths()[0] for syn in wn.synsets(word, lang='spa')])
        is_substance = [substance_syn in syn.hypernym_paths()[0] for syn in wn.synsets(word, lang='spa')]
        is_matter = [matter_syn in syn.hypernym_paths()[0] for syn in wn.synsets(word, lang='spa')]
        if debug: print(word, any(is_substance_syn), any(is_matter_syn))

    # aire Synset('matter.n.03'), Synset('substance.n.01')
    # aire Synset('matter.n.03'), Synset('fluid.n.02')
    # mesa Synset('matter.n.03'), Synset('substance.n.07'), Synset('food.n.01')
    # vidrio [[Synset('entity.n.01'), Synset('physical_entity.n.01'), Synset('matter.n.03'), Synset('solid.n.01'), Synset('glass.n.01')]]
    # papel [Synset('entity.n.01'), Synset('physical_entity.n.01'), Synset('matter.n.03'), Synset('substance.n.01'), Synset('material.n.01'), Synset('paper.n.01')]]

    # [v] latón True True
    # [v] zinc False False
    # [ ] vidrio False True
    # [v] papel True True
    # [ ] mesa False True
    # [v] roble False False
    # [v] música False False
    # [v] letra False False
    # [v] aire True True
    # [v] oxígeno True True
    # [v] dios False False



#endregion