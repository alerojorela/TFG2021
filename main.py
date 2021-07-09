# -*- coding: utf-8 -*-
# by Alejandro Rojo Gualix 2021-06
__author__ = 'Alejandro Rojo Gualix'
# assert días_para_entrega > 10, "😱"

""" FROM TERMINAL
python3 main.py -s
python3 main.py -nc -s
python3 main.py -t 'Compré un coche en Segovia.'
python3 main.py -t 'En la colina había una casa de piedra. La casa era grande.'
"""
import sys

# MÍOS
import evaluacion  # samples for testing
import graph
import predicates.graphs as graphs
from predicates import patterns, ancora_patterns

import predicates
import ontology


def prueba_spacy(text):
    complexity = 1
    if complexity == 0:
        nlp = spacy.load("es_core_news_sm")
    elif complexity == 1:  # más pesado:
        nlp = spacy.load("es_dep_news_trf")
    elif complexity == 2:
        nlp = spacy.load("es_core_news_lg")

    doc = nlp(text)
    explacy.print_parse_info(nlp, text)
    sys.exit(0)


def run(text, coreference=True, inference=True):
    # sg = graphs.SemanticGraph(text, pattern_source)
    # sg = graphs.SemanticGraph(text, pattern_source, coreference=True, inference=False, debug=False)
    sg = graphs.SemanticGraph(text, pattern_source, coreference=coreference, debug=False)

    if inference:
        # -------------------------------------------------------------------------------------------------
        # [8] se vincula la información explícita del microtexto con la derivada de la base de conocimiento
        monovalent_predicate_tokens = [_ for _ in sg.predicate_tokens
                                       if sg.get_predicate_info(_)['valency'] == 1]
        # -------------------------------------------------------------------------------------------------
        # [7] se vincula la información explícita del microtexto con la derivada de la base de conocimiento
        print('\n', '*' * 100)
        # token: synset
        monovalent_predicate_tokens_tuples = {_: _.properties['synset'] for _ in monovalent_predicate_tokens
                                              if 'synset' in _.properties}

        from ontology import inference

        # import ontology  # module 'ontology' has no attribute 'inference'
        ig = inference.InferencesGraph(monovalent_predicate_tokens_tuples.values())
        # ig.visualize()
        # se vincula la información explícita del microtexto con la derivada de la base de conocimiento
        merged = graph.Graph()
        merged.merge_graphs([sg, ig])

        # conexiones
        for key, value in monovalent_predicate_tokens_tuples.items():
            merged.add_edge(key, value, '', {})

        # distinción entre el grupo inicial y el inferido
        subgraph = False
        if subgraph:
            subgraphs = [sg.nodes.keys()]
            formatted = merged.dot_graph_subgraph_format(subgraphs)
            merged.visualize_string(formatted)
        else:
            for node in sg.nodes.keys():
                sg.update_node_properties(node, {'style': "filled", 'fillcolor': "lightsteelblue1"})
                # sg.update_node_properties(node, {'style': "filled", 'fillcolor': "khaki"})
            merged.visualize()


pattern_source = patterns.patterns['es']
# VERBS section
ancora_patterns.patterns['es'][0]['ALTERNATIVES'].append(patterns.patterns['es'].pop())
# my patterns and Ancora patterns
pattern_source = patterns.patterns['es'] + ancora_patterns.patterns['es']


# Para ejecutar desde la consola
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Extrae los predicados de una oración o texto.')
    # INPUT
    """ DISPLAY FORMAT
        latex
        dot
        dotweb
    """
    # parser.add_argument('--dot', action='store_true', help='devuelve grafos en formato dot (graphviz)')
    # parser.add_argument('--dotweb', action='store_true',
    #                     help='Visualiza los grafos en la página https://dreampuf.github.io/GraphvizOnline/')
    """ DISPLAY INFO
        spacy and output [always]
        pattern
        predicate
    """
    # positional
    parser.add_argument('-t', '--text', nargs=1, metavar='text', type=str, help='oración o texto a procesar')
    # optional
    # parser.add_argument('-e', '--evaluation', action='store_true', help='')
    parser.add_argument('-s', '--samples', action='store_true', help='')
    parser.add_argument('-nc', '--no-coreference', action='store_false', help='no analiza la correferencia')
    parser.add_argument('-ni', '--no-inference', action='store_false', help='no realiza inferencias')
    # Namespace(no_inference=False, no_coreference=False, samples=False, text='papar itrip')

    args = parser.parse_args()
    # print(args)

    if args.samples:
        text = 'En la colina había una casa de piedra. La casa era grande.'
        text = 'El trueno resonó en el valle.'
    elif args.text:
        text = args.text[0]
    else:
        parser.error("One argument is required!")
        sys.exit(1)

    run(text, coreference=args.no_coreference, inference=args.no_inference)
    sys.exit(0)



""" spacy.tokens.Token
    [SÍ] i	The index of the token within the parent document. 
        doc[i] 
        16)abismo < 13)saturno >  <22)hollar> 	patrón[N N COP]
        TENER-cuyo < 16)abismo 18)fondo >  <13)saturno 22)hollar> 	patrón[TENER-cuyo]

    [NO] idx	The character offset of the token within the parent document.
    int
    lex_id	Sequential ID of the token’s lexical type, used to index into tables, e.g. for word vectors. 
        TENER-cuyo < 1|18446744073709551615|vecina 3|18446744073709551615|casa >  <4|18446744073709551615|arder> 

    [SÍ] _	User space for adding custom attribute extensions. 

    [NO] tag_	Fine-grained part-of-speech. 
        16|NOUN|abismo < 13|PROPN|saturno >  <22|VERB|hollar> 	patrón[N N COP]
        TENER-cuyo < 16|NOUN|abismo 18|NOUN|fondo >  <13|PROPN|saturno 22|VERB|hollar> 	patrón[TENER-cuyo]

    is_oov	Is the token out-of-vocabulary (i.e. does it not have a word vector)? 
    like_num	Does the token represent a number? e.g. “10.9”, “10”, “ten”, etc. 

    ENT
        ent_type	Named entity type.
        int
        ent_type_	Named entity type.
        str
        ent_iob	IOB code of named entity tag. 3 means the token begins an entity, 2 means it is outside an entity, 1 means it is inside an entity, and 0 means no entity tag is set.
        int
        ent_iob_	IOB code of named entity tag. “B” means the token begins an entity, “I” means it is inside an entity, “O” means it is outside an entity, and "" means no entity tag is set.
        str
        ent_kb_id 	Knowledge base ID that refers to the named entity this token is a part of, if any.
        int
        ent_kb_id_ 	Knowledge base ID that refers to the named entity this token is a part of, if any.
        str
        ent_id	ID of the entity the token is an instance of, if any. Currently not used, but potentially for coreference resolution.
        int
        ent_id_	ID of the entity the token is an instance of, if any. Currently not used, but potentially for coreference resolution.
        str

    lex v3.0 The underlying lexeme. 
        Lexeme.vector 
            ValueError: [E010] Word vectors set to length 0. This may be because you don't have a model installed or loaded, or because your model doesn't include word vectors. For more info, see the docs:
            https://spacy.io/usage/models

    tensor 	The tokens’s slice of the parent Doc’s tensor. 

"""


""" 
    Universal POS tags  https://universaldependencies.org/u/pos/all.html
    Open class words
    VERB
    ADV
    ADJ
    NOUN
    PROPN
    INTJ

    Closed class words
    ADP
    PRON
    AUX
    DET
    NUM
    PART: particle [en] ‘s [ja] か / ka
    CCONJ
    SCONJ

    Other
    PUNCT
    SYM: symbol $, %, §, © +, −, ×, 
    X

    token.dep_  https://universaldependencies.org/u/dep/all.html
"""