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


