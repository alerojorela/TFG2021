# -*- coding: utf-8 -*-
# by Alejandro Rojo Gualix 2021-06
__author__ = 'Alejandro Rojo Gualix'


import sys
from itertools import count
import json
import re
import spacy
# dependency visualizer
# from spacy import displacy
# wget https://raw.githubusercontent.com/tylerneylon/explacy/master/explacy.py
import utils.explacy


# MÍOS
import graph  # basic graph
import utils.functions as functions
import predicates
import predicates.morphology as morphology
import predicates.semantics as semantics
import ontology.extensionKB


# Preparado para presentación de colores en consola. Basado en:
# https://stackoverflow.com/questions/27265322/how-to-print-to-console-in-color
fg = {'black': '\033[30m', 'red': '\033[31m', 'green': '\033[32m', 'orange': '\033[33m', 
    'blue': '\033[34m', 'magenta': '\033[35m', 'cyan': '\033[36m', 'white': '\033[37m'}
bg = {'black': '\033[40m', 'red': '\033[41m', 'green': '\033[42m', 'orange': '\033[43m',
    'blue': '\033[44m', 'magenta': '\033[45m', 'cyan': '\033[46m', 'white': '\033[47m'}

# properties
property_keys = ['text', 'old_lemma', 'pos', 'lemma']  # lemma
# print_dict_exclude = morphology.recursive_keys + morphology.function_keys
print_dict_exclude = ['CHILDREN', '¬CHILDREN', 'OPTIONAL_CHILDREN', 'ALTERNATIVES', 'fNOTFOUND', 'fRENAME', 'fPOSTPROC']

def print_debug_dict(obj):
    output = ''
    for key, value in obj.items():
        if key not in print_dict_exclude:
            output += f"{fg['green']}✔{fg['white']} {key}: {value}  "
    return output


def verify(value, pattern):
    # print(f"verify( {value} == {pattern} )")
    if isinstance(pattern, re.Pattern):  # regular expression created with re.compile(pattern)
        if pattern.search(value) is not None: return True
    elif isinstance(pattern, dict):  # dictionary
        if value in pattern: return True
    elif isinstance(pattern, list):  # list
        if value in pattern: return True
    else:
        if value == pattern: return True
    return False


def format(key, pattern):
    if key in pattern:
        if isinstance(pattern[key], re.Pattern):
            return pattern[key].pattern
        elif isinstance(pattern[key], list):
            return ' / '.join(pattern[key])
        else:
            return pattern[key]
    else:
        return ''




# Wraper que me permite crear mis propios Token
# permite comparación entre subgrafos


#region "Match and transformation graphs"


class MyEdge(graph.Edge):
    def __init__(self, start, end, label='', properties={}):
        graph.Edge.__init__(self, start, end, label='', properties={})


"""
spacy.tokens.Token
(None, str)  creados TENER mi casa
(spacy.tokens.Token, str)   renombrados como en->ESTAR
"""
class MyNode(graph.Node):
    def __init__(self, label, properties, ref_object=None):
        graph.Node.__init__(self, label, properties, ref_object)

    # coincidencia de un token y un patrón
    def match_properties(self, patterns, restricted_keys=property_keys, debug_function=False):
        # restricted_keys ∩ patterns.keys
        # pattern_properties = { key:patterns[key] for key in patterns.keys() if key in restricted_keys}  
        for key, pattern in patterns.items():
            if not restricted_keys or key in restricted_keys:  # filter keys for comparison
                if key not in self.properties or not verify(self.properties[key], pattern):
                    if debug_function: print('\t' * 3 + fg['red'] + 'x' + fg['white'], 'PROPERTY', f'{key}: {pattern}')
                    return False
                if debug_function: print('\t' * 3 + fg['green'] + '✔' + fg['white'], 'PROPERTY', f'{key}: {pattern}')
        return True



class MyGraph(graph.Graph):
    def __init__(self, nodes=None, nodes_attr=None):
        graph.Graph.__init__(self, nodes, nodes_attr)

    """ coincidencia de un token y un patrón
    el patrón habrá de tener esta forma
    """
    def match(self, token, pattern, restricted_keys=property_keys, debug_function=False):
        # nodes
        if debug_function: print('\t' * 3 + 'MATCH?', token.properties, '\t', {key:pattern[key] for key in pattern.keys() if key in restricted_keys})
        if not token.match_properties(pattern, restricted_keys, debug_function):
            if debug_function: print('\t' * 3 + fg['red'] + 'x' + fg['white'], 'MATCH')
            return False

        # edges
        if 'dep' in pattern:
            parent_edges = self.search_edges(end=token)
            if parent_edges:
                label = parent_edges[0].label
                if not verify(label, pattern['dep']):
                    if debug_function: print('\t' * 3 + fg['red'] + 'x' + fg['white'], 'EDGE', (label, pattern['dep']) )
                    return False
                if debug_function: print('\t' * 3 + fg['green'] + '✔' + fg['white'], 'EDGE', (label, pattern['dep']) )

        if 'boolean_function' in pattern:  # función de comprobación ulterior para precisar
            return pattern['boolean_function'](self)
        # black_list white_list exclude include
        return True

    """
    coincidencia de un árbol de tokens con un árbol de patrones
    función recursiva
    """
    # shared function
    def recursive_match(self, token, pattern, parent_token=None, dict_key='#', debug_function=False, level=0):
        indent = (' ' * level + '█').ljust(5)
        lj = 12

        """
        en esta función recursiva hacen falta dos movimientos:
            uno descendente de la raíz a las hojas, cuyo objetivo es recorrer una estructura
                recursive_match(...child_token...)
            otro ascendente, de vuelta desde las hojas a la raíz (la primera llamada a la función recursive_match)
            es necesario que cada hoja (terminal) exitosa se propague de vuelta
            para que el nudo superior tome una decisión sobre la validez de todas sus ramas
                return recursive_feedback
        este valor de retorno recursive_feedback es un diccionario {}
        con los argumentos escogidos y la ruta que se ha seguido hasta entonces
        """
        recursive_feedback = {'sel_arguments': [], 'trace': [], 'ppf': []}
        new_arguments = []

        # *************************************************************************************************
        # CONDICIONES NECESARIAS
        # A análisis del elemento individual
        if not self.match(token, pattern, debug_function=debug_function):
            return None  # [exit 1]

        if debug_function: 
            forks = [key for key in pattern.keys() if key in ['CHILDREN', 'ALTERNATIVES', 'OPTIONAL_CHILDREN']]
            print(indent, '↓  ', str(token).ljust(lj),
                ("'" + pattern['NAME'] + "'") if 'NAME' in pattern else '',
                ' & '.join(forks) )

        def match_children(pattern2, optional=False, negation=False):
            # para comprender bien esto visualiza una tabla:
            # 1) los encabezados de las filas son los patrones, los de las columnas son los hijos de token
            # 2) se va rellenando esa tabla por filas con True o False

            # condiciones
            # NO puede haber un patrón sin elementos coincidentes
            # SÍ puede haber un elemento que no verifique ningún patrón

            matrix = []
            for child_pat in pattern2:
                matched_children = [self.recursive_match(child, child_pat, token, dict_key, debug_function, level + 1)
                                    for child in self.children(token)]
                matrix.append(matched_children)
                alguno = [item for item in matched_children if item]  # remove None or False items
                if not alguno:
                    # 1) si no tiene hijos token, matched_children = []
                    # 2) si ninguno verifica el patrón
                    if debug_function: print(indent, ' x ', str(token).ljust(lj), 'matched_children CHILDREN', matched_children)
                    if 'fNOTFOUND' in child_pat and callable(child_pat['fNOTFOUND']):  # optional_not_found
                        # print('fNOTFOUND', token)
                        # OPTIONAL puede ser bool o una función. La función es llamada si no se halla ningún elemento que verifique el patrón
                        properties = child_pat['fNOTFOUND'](self, token)  # call function defined in key value
                        if properties:
                            # force string argument
                            properties['text_index'] = token.properties['text_index']  # same as current token position
                            index = child_pat[dict_key]
                            new_argument = (index, MyNode(properties['text'], properties))
                            alguno = [new_argument]
                            new_arguments.append(new_argument)
                # EXITO: XOR        FRACASO: mismo valor
                if not optional and bool(alguno) == negation:
                    return False

            if functions.is_bijection_matrix(matrix):
                valid_matrix = matrix
            else:
                print('\n', 'is_bijection_matrix == False')
                print('\t', token.label, [_.label for _ in self.children(token)])
                print('\t', functions.matrix2_to_bool(matrix))
                alternatives = functions.force_bijection_matrix(matrix)
                if not alternatives:
                    if debug_function: print(indent, ' x ', str(token).ljust(lj), 'NON-BIJECTIVE Matrix: 1 token for each pattern',
                                             matched_children)
                    return False
                else:
                    for alternative in alternatives:
                        al_bool = functions.matrix2_to_bool(alternative)
                        for index, child_pat in enumerate(pattern2):
                            print('>>', al_bool[index], child_pat)
                    valid_matrix = alternatives[0]

            validos = [item for i_pattern in valid_matrix for item in i_pattern if item]
            for item in validos:
                recursive_feedback['sel_arguments'].extend(item['sel_arguments'])
                recursive_feedback['trace'].extend(item['trace'])
                recursive_feedback['ppf'].extend(item['ppf'])

            return True

        def match_childrenOBSOLETO(pattern2, optional=False, negation=False):
            for child_pat in pattern2:  # por cada patrón child_pat, recorre todos los hijos del token, escogiendo aquellos que lo verifican
                matched_children = [self.recursive_match(child, child_pat, token, dict_key, debug_function, level + 1)
                                    for child in self.children(token)]
                matched_children = [item for item in matched_children if item]  # remove None or False items

                found = False
                if matched_children:
                    if negation:
                        return False
                    else:
                        found = True
                        if debug_function: print(indent, ' ↑ ', str(token).ljust(lj), 'matched_children CHILDREN',
                                                 matched_children)
                        # FUSIÓN, incorpora los resultados de la recursión inferior
                        for item in matched_children:
                            recursive_feedback['sel_arguments'].extend(item['sel_arguments'])
                            recursive_feedback['trace'].extend(item['trace'])
                            recursive_feedback['ppf'].extend(item['ppf'])
                else:
                    # 1) si no tiene hijos token, matched_children = []
                    # 2) si ninguno verifica el patrón
                    if debug_function: print(indent, ' x ', str(token).ljust(lj), 'matched_children CHILDREN',
                                             matched_children)
                    if 'fNOTFOUND' in child_pat and callable(child_pat['fNOTFOUND']):  # optional_not_found
                        # OPTIONAL puede ser bool o una función. La función es llamada si no se halla ningún elemento que verifique el patrón
                        # print('fNOTFOUND', token)
                        properties = child_pat['fNOTFOUND'](self, token)  # call function defined in key value
                        if properties:
                            if negation:
                                return False
                            else:
                                found = True
                                # force string argument
                                properties['text_index'] = token.properties[
                                    'text_index']  # same as current token position
                                index = child_pat[dict_key]
                                new_argument = (index, MyNode(properties['text'], properties))
                                new_arguments.append(new_argument)

                if negation and found: return False
                if not optional and not negation and not found: return False
            return True

        # B1 parte recursiva que puede abortar la función
        # children pattern
        if '¬CHILDREN' in pattern and not match_children(pattern['¬CHILDREN'], optional=False, negation=True):
            return None  # [exit 2] forbidden children matched. report that this branch failed to parent function.

        if 'CHILDREN' in pattern and not match_children(pattern['CHILDREN'], optional=False):
            return None  # [exit 3] no compulsory children matched. report that this branch failed to parent function.

        # B2 Al menos debe haber una alternativa que se cumpla; se escogerá la primera
        if 'ALTERNATIVES' in pattern and pattern['ALTERNATIVES']:
            matched = False
            for option in pattern['ALTERNATIVES']:
                # if debug_function: print(indent, '⑃')
                # NOTA: 'ALTERNATIVES' se halla al mismo nivel que el token y no al de sus hijos
                matched = self.recursive_match(token, option, parent_token, dict_key, debug_function, level + 1)
                if matched:
                    break  # iteramos sobre las alternativas y si una se verifica no continuamos
            if matched:
                if debug_function: print(indent, ' ✔ ', str(token).ljust(lj), 'matched ALTERNATIVES', matched)
                # FUSIÓN
                recursive_feedback['sel_arguments'].extend(matched['sel_arguments'])
                recursive_feedback['trace'].extend(matched['trace'])
                recursive_feedback['ppf'].extend(matched['ppf'])
            else:
                if debug_function: print(indent, ' x ', str(token).ljust(lj), 'matched ALTERNATIVES', matched)
                return None  # [exit 4] ninguna alternativa se verificó

        # *************************************************************************************************
        # OPCIONAL
        # C parte recursiva que no aborta la función
        # Esta opción va al final pues no es condición necesaria como las anteriores
        if 'OPTIONAL_CHILDREN' in pattern:  # children pattern
            match_children(pattern['OPTIONAL_CHILDREN'], optional=True)

        # D si hemos llegado aquí quiere decir ninguna rama ha sido abortada, por tanto
        # existe una rama válida por debajo y hasta la bifurcación superior, también se verificó el token arriba
        if debug_function: print(indent, ' ✔ ', str(token).ljust(lj), print_debug_dict(pattern))
        # trace alternatives
        if 'NAME' in pattern:  # prefija
            if debug_function: print(indent, ' ⑂', ' ' * (lj + 2), 'NAME', pattern['NAME'])
            recursive_feedback['trace'].insert(0, pattern['NAME'])
        # post processing function
        if 'fPOSTPROC' in pattern:  # al ubicarse la asignación aquí el valor de 'ppf' es el del elemento más profundo, más específico
            recursive_feedback['ppf'].insert(0, pattern['fPOSTPROC'])
        # función ulterior para renombrar la etiqueta
        if 'fRENAME' in pattern:
            if callable(pattern['fRENAME']):
                token.label = pattern['fRENAME'](token)
            elif isinstance(pattern['fRENAME'], str):
                token.label = pattern['fRENAME']

        # Selected arguments
        if dict_key in pattern:  # promote to argument
            index = pattern[dict_key]
            new_argument = (index, token)
            recursive_feedback['sel_arguments'].append(new_argument)
            if debug_function: print(indent, '  #', token)
        # Created arguments
        if new_arguments:
            for new_argument in new_arguments:
                self.add_edge(token, new_argument[1], 'INSERTADO')
                recursive_feedback['sel_arguments'].append(new_argument)
                if debug_function: print(indent, '  # Token insertado -> ', new_argument[1].properties)
                # if debug_function: print(indent, '  #', properties, 'recursive_feedback', recursive_feedback)

        # trazado
        self.update_node_properties(token, {'fontcolor': 'red'})
        # if parent_token is not None and parent_token is not token:  # edge
        #     edge = graph.search_edges(start=parent_token, end=token)[0]
        #     graph.update_edge_properties(edge, {'color': 'red', 'fontcolor': 'red'})

        return recursive_feedback


class PredicateGraph(MyGraph):
    """ returns a tree graph were tagged nodes with
    0 as functor
    1..n as its children

    digraph G {
        node [shape="plaintext"];
        edge [color="gray80"];
        
        
        0 [fontcolor="red", shape="invhouse", fontsize="18", label="0"];
        1 [fontcolor="black", shape="box", fontsize="18", label="1"];
        2 [fontcolor="black", fontsize="18", label="..."];
        3 [fontcolor="black", shape="box", fontsize="18", label="N"];
        
        0 -> 1 [label="1"];
        0 -> 2 [label=""];
        0 -> 3 [label="N"];
    }
    """
    def __init__(self, graph, token, pattern, dict_key='#', debug_function=False):
        MyGraph.__init__(self)
        # self.text = ''

        self.success = False

        # post procesamiento
        results = graph.recursive_match(token, pattern, dict_key=dict_key, debug_function=debug_function)
        if results:
            # print('\t' * (level), f"{fg['blue']}{results}{fg['white']}")

            """ convierte a diccionario las tuplas (key, value)
            Si dos complementos compiten por un mismo rol argumental escogemos el primero y relegamos los demás.
            se escoge el primero que suele ser el argumento

            en caso de coordinación tendría sentido mantener la lista
                esto funciona por ejemplo para "Yo introduje los garbanzos en el tarro en la cocina"
                    "en el tarro" es un argumento pero "en la cocina" es un complemento de lugar
            [(2, proyecto), (3, Marta), (1, 'yo'), (0, hablé)] ----> ['yo', proyecto, Marta]         
            [(1, 'yo'), (2, garbanzos), (3, tarro), (3, cocina)] ----> 
            """
            # dct = {item[0]: item[1] for item in results['sel_arguments']}  # esta opción sobreescribe la key con el último elemento
            dct = {}
            for key, value in results['sel_arguments']:
                if not key in dct:  # solo admite el primero
                    dct[key] = value
            results['sel_arguments'] = dct

            # convierte a lista de valores conservando sus posiciones
            keys = dct.keys()
            arr = [None] * (max(keys) + 1)
            for key in keys:
                arr[key] = dct[key]

            self.pattern = pattern
            self.pattern_trace = results['trace']

            self.functor = arr[0]
            self.arguments = arr[1:]  # argumentos etiquetados
            self.adjuncts = []
            # NO HECHOS: negación subjuntivo futuro
            # verificar si hay negación, iteramos sobre los complementos
            # negation_pattern = {'dep': 'advmod', 'lemma': 'no' }  # <<<<<<<< ninguno en sujeto etc... nunca adv
            # self.negation = [child for child in graph.children(token) if graph.match(child, negation_pattern)]
            negation_patterns = [
                {'dep': 'advmod', 'lemma': 'no'},
                {'dep': 'advmod', 'lemma': 'nunca'},
                {'dep': 'nsubj', 'lemma': 'ninguno'},
                {'pos': ['NOUN', 'PROPN', 'PRON'], 'CHILDREN': [
                     {'old_lemma': 'ninguno'},  # "Saturno era un abismo cuyo fondo ninguna sonda había hollado aún."
                ]},
                {'dep': 'nsubj', 'lemma': 'nadie'},
            ]
            self.negation = [child for child in graph.children(token) for negation_pattern in negation_patterns if graph.recursive_match(child, negation_pattern)]

            if 'ppf' in results and results['ppf']:  # PPF 'fPOSTPROC' función de comprobación ulterior para precisar
                if debug_function: print('*\tfPOSTPROC()')
                results['ppf'][0](self)

            """ CAMBIOS EN LAS ARISTAS
            todo functor pasa a raíz -> se eliminan todos los edge (?, functor)
            todos los argumentos deben depender de él -> se crea un edge
            """
            self.nodes[self.functor] = {}
            # self.create_node(self.functor)

            # remove_edges = self.search_edges(end=self.functor)
            for index, argument in enumerate(self.arguments):
                self.nodes[argument] = {}
                # if argument is not None and not self.search_edges(start=self.functor, end=argument):
                self.add_edge(self.functor, argument, str(index), {})

            self.success = True

    def print(self, level=0):
        if not self.success: return None
        # print('\t' * level, f"{fg['blue']}{predicate}{fg['white']}")
        prep = [
            ('¬' if self.negation else ''),
            self.functor,
            ' '.join([str(_) for _ in self.arguments]),
            ' '.join([str(_) for _ in self.adjuncts]),
            # ' '.join([str(_) for _ in functions.flatten(self.arguments)]),
            # ' '.join( [str(_) for _ in functions.flatten(self.adjuncts)] ),
            '/'.join(self.pattern_trace),
        ]

        print('\t' * level,
            f"{fg['orange']}{prep[0]}{prep[1]} < {prep[2]} > ",
            f"<{prep[3]}>" if prep[3] != '' else '',
            f"{fg['white']}\tpatrón[{fg['orange']}{prep[4]}{fg['white']}]")
        # return prep

#endregion



"""
SPACY ->
PATTERN ->
"""
#region "conversion to graphs"


class SpacyGraph(MyGraph):
    def __init__(self, doc):
        # without merging items
        # list_tokens = [SpacyToken(token) for token in doc]
        # MyGraph.__init__(self, my_tokens)
        # [self.add_edge(list_tokens[token.i], list_tokens[child.i], child.dep_) for token in doc for child in token.children]

        # merging items
        # deben mantener cada uno su índice en la lista
        indexed_tokens = []
        for token in doc:
            if token.dep_ == 'flat':
                indexed_tokens.append(None)
            else:
                # merge tokens
                # Gómez        flat     Gómez        PROPN
                new_token = SpacyToken(token)
                for child in token.children:
                    if child.dep_ == 'flat':
                        new_token.label += '_' + child.text
                        new_token.merged.append(child)
                indexed_tokens.append(new_token)

        valid_tokens = [_ for _ in indexed_tokens if _ is not None]
        MyGraph.__init__(self, valid_tokens)
        # print('my_tokens', my_tokens)
        [self.add_edge(indexed_tokens[token.i], indexed_tokens[child.i], child.dep_) for token in doc for child in token.children
            if indexed_tokens[token.i] is not None and indexed_tokens[child.i] is not None]


class SpacyToken(MyNode):
    def __init__(self, token):
        properties = {'text': token.text, 'old_lemma': token.lemma_, 'pos': token.pos_, 'text_index': token.i}
        MyNode.__init__(self, token.lemma_, properties, token)
        self.merged = []
        """
        Como puede observarse en los PRON el lema elimina EL NÚMERO
        LABEL  va a ser siempre yo tú él
        
        Dep tree Token    Dep type Lemma   Part of Sp
        ──────── ──────── ──────── ─────── ──────────
            ┌──► Vosotros nsubj    tú      PRON
            │┌─► nos      obj      yo      PRON
            ┌──► Yo       nsubj    yo      PRON
            │┌─► me       obj      yo      PRON
             ┌─► Mi       det      mi      DET
          └──┼── mía      ROOT     mío     PRON
         └┴──┼── suya     ROOT     suyo    DET
        ││  │┌─► vuestra  det      vuestro DET
             ┌─► Nuestra  det      nuestro DET        
        """

        """ 2 situaciones con la flexión
           ┌─►   Mi    det      mi    DET       
        ┌─►└──   casa  nsubj    casa  NOUN      
        │  ┌─►   está  cop      estar AUX       
        └──┴──   nueva ROOT     nuevo ADJ       

        Dep tree Token     Dep type Lemma     Part of Sp
        ──────── ───────── ──────── ───────── ──────────
            ┌─►  La        det      el        DET       
         ┌─►└──  bicicleta nsubj    bicicleta NOUN      
        ┌┴─────  está      ROOT     estar     VERB      
        │  ┌──►  en        case     en        ADP       
        │  │┌─►  la        det      el        DET       
        └─►└┴──  pared     obl      pared     NOUN 
        """
        # if self.match_properties({'pos': 'AUX'}):
        #     self.properties['pos'] = 'FLEX'
        #     self.properties['lemma'] = self.properties['old_lemma']
        # 'haber',
        if self.match_properties({'old_lemma': ['estar', 'ser']}):
            self.properties['pos'] = 'AUX'
            self.properties['lemma'] = self.properties['old_lemma']
            self.label = self.properties['lemma']

        elif self.match_properties( {'pos': 'PROPN'} ):
            self.properties['lemma'] = self.properties['text']
            self.label = self.properties['lemma']
        elif self.match_properties( {'pos': ['PRON', 'DET']} ):
            """ EN DET y PRON se evita la lematización de SPACY 
            no aceptes el lema, usa self.properties['text'].lower()
            se evita la lematización ya que convierte  nosotros->yo, ella->él
            # POSTPROCESAMIENTO tras correferencia
            el caso particularísimo de los posesivos
            que SPACY lematiza a su manera, y es normal ya que codifican información del poseedor y poseído
             y NOUN ¿por qué? 'pos': ['PRON', 'DET', 'NOUN']
                  ┌─► La           det      el           DET       
               ┌─►└── mía          nsubj    mía          NOUN      
               │  ┌─► es           cop      ser          AUX       
               └──┼── chalet       ROOT     chalet       NOUN      
                  └─► .            punct    .            PUNCT   
            """
            det_data = morphology.get_determiner_lemma(self.properties['text'].lower(), self.properties['pos'])
            if det_data:
                self.properties['lemma'] = det_data['lemma']
                self.label = self.properties['lemma']
                self.properties['DET'] = det_data

        else:
            self.properties['lemma'] = self.properties['old_lemma']
            self.label = self.properties['lemma']


class PatternGraph(MyGraph):
    def __init__(self, pattern, pattern_trace=[]):
        # si pattern_trace=[] no filtrará las alternativas y las recorrerá todas
        def format_recursive(pattern, pattern_trace, parent=None, edge_type=None):
            data = [format('text', pattern), format('lemma', pattern), format('pos', pattern)]
            # remove None members and convert re.Pattern to string
            data = [_ for _ in data if _]
            # data = [_.pattern if isinstance(_, re.Pattern) else _ for _ in data if _]
            if '#' in pattern:  # etiqueta #
                # d = f"< <font POINT-SIZE='18' color='red'><b>[{pattern['#']}]</b></font><br/>the >"
                # tp[0] = f"[{pattern['#']}]\\n{'|'.join(text)}"
                label = f"< <font POINT-SIZE='18' color='red'><b>[{pattern['#']}]</b></font><br/>{'<br/>'.join(data)} >"
            else:
                label = '\n'.join(data)

            properties = { _:pattern[_] for _ in pattern.keys() if _ in property_keys}  # copy selected properties
            token = MyNode(label, properties, pattern)
            node_properties = {'label': label}
            self.create_node(token, node_properties)

            if not parent is None:  # create edge
                # con edge_type podemos crear una etiqueta 'label' o bien cambiar la forma de este nodo hijo
                edge_label = pattern['dep'] if 'dep' in pattern else ''
                edge_properties = {}

                if edge_type == '¬CHILDREN':
                    edge_properties = {'label': '¬' + edge_label}
                    node_properties.update( {'fontcolor': 'purple'} )
                elif edge_type == 'OPTIONAL_CHILDREN':
                    node_properties.update( {'style': 'dotted'} )
                elif edge_type == 'ALTERNATIVES':
                    node_properties.update( {'shape': 'invtriangle'} )
                #funciones

                self.add_edge(parent, token, edge_label, edge_properties)

            # self.update_node_properties(token, node_properties )

            for key in pattern.keys():  # { } pattern 
                if key in morphology.recursive_keys:
                    for pattern_child in pattern[key]:  # [ ] pattern_child 
                        if pattern_trace and key == 'ALTERNATIVES':  # branch just traced path restrictions
                            # print(pattern_trace, '\t', pattern_child['NAME'])
                            if pattern_child['NAME'] == pattern_trace[0]:
                                format_recursive(pattern_child, pattern_trace[1:], parent=token, edge_type=key)
                        else:
                            format_recursive(pattern_child, pattern_trace, parent=token, edge_type=key)

        MyGraph.__init__(self)
        if pattern_trace:
            # print(pattern_trace, '\t', pattern['NAME'])
            if pattern['NAME'] != pattern_trace[0]: return
            format_recursive(pattern, pattern_trace[1:])
        else:
            format_recursive(pattern, pattern_trace)



#endregion



#region "LO IMPORTANTE"
# ----------------------------------------

import time
start_time = time.time()
weight = 2
if weight == 0:
    nlp = spacy.load("es_core_news_sm")
elif weight == 1:  # sec
    nlp = spacy.load("es_core_news_lg")
    """" no reconoció
     introducir
     'La casa inadecuada para vivir',
    '✅Pepe ronca en el sofá que compramos'
    """
elif weight == 2:  # más pesado: 7.72 sec
    nlp = spacy.load("es_dep_news_trf")
    """ no reconoce entidades, aunque el anterior es bastante torpe 
    """
execution_time = (time.time() - start_time)
print(f'Spacy loading took {str(execution_time)} seconds\n')
# print(f'spacy loading and text processing took {str(execution_time)} seconds')


class SemanticGraph(MyGraph):

    def search_predicates(self, graph, token, sentence, debug_function=False, level=0):
        indent = '\t' * level
        predicates = []
        # functions.debug_dir(token, '\t' * (level + 1))

        for pattern in self.pattern_source:
            predicate = PredicateGraph(graph, token, pattern, dict_key='#', debug_function=debug_function)
            if predicate.success:
                predicate.sentence = sentence
                predicates.append(predicate)
                if debug_function: print(indent, str(token),
                                         f"{fg['green']}[✔ MATCHED] {pattern['NAME']} {fg['white']}")
            else:
                if debug_function: print(indent, str(token), f"{fg['red']}[☠ ABORTED] {pattern['NAME']} {fg['white']}")

        # RECURSION: check for categories in SUBCAToptegorizing_pos
        for child in graph.children(token):
            if child.match_properties(self.SUBCAToptegorizing_pos):
                # if debug_function: print(indent + f"{token}->{child}")
                predicates.extend(self.search_predicates(graph, child, sentence, debug_function, level + 1))

        return predicates

    def __init__(self, text, pattern_source, coreference=True, debug=False):
        MyGraph.__init__(self)
        self.pattern_source = pattern_source
        self.text = text
        self.SUBCAToptegorizing_pos = {'pos': ['VERB', 'ADV', 'ADJ', 'NOUN', 'PROPN']}
        self.pos_predicate_pattern = {'pos': ['VERB', 'ADV', 'ADJ', 'NOUN', 'ADP']}  # ADV "estaba delante de mis ojos"



        # --------------------------------
        # [1-4] Se crea el grafo semántico
        print('\n', '*' * 100)
        print(text, '\n')
        self.base_graph(text)


        # ----------------------------------------------------------------
        # [5] Desambiguación: asocia a synsets
        self.deambiguation()

        # -----------------------------------------------------
        # [6] Categoriza y se prepara visualmente para graphviz
        print('\n', '*' * 100)

        # 4 nociones que se corresponden con 3 propiedades visuales <<<<<<<<<<
        self.predicate_tokens = []
        self.flex_tokens = []
        self.determiner_tokens = []  # nombres propios y determinantes
        self.entity_tokens = []  # nombres propios y los determinantes que no sean anáfora (que no sean origen de una arista)

        name_tokens = []
        indefinite_tokens = []
        definite_tokens = []
        for node in self.nodes.keys():
            arity = len(self.search_edges(start=node))  # valencia, <<<<<<< PERO quita AUX y otros
            # HABER + DP
            # print(arity, node, node.properties)
            if node.match_properties({'pos': 'FLEX'}):
                self.flex_tokens.append(node)
            elif node.match_properties(morphology.sintagma_determinante):
                self.determiner_tokens.append(node)
                if node.match_properties(morphology.indefinido):
                    indefinite_tokens.append(node)
                elif node.match_properties(morphology.definido):
                    definite_tokens.append(node)
                elif node.match_properties({'pos': ['PROPN']}):
                    name_tokens.append(node)
            elif node.match_properties(self.pos_predicate_pattern):
                self.predicate_tokens.append(node)

        sorted_tokens = [(_.properties['text_index'], self.label(_)) for _ in self.nodes]
        sorted_tokens = sorted(sorted_tokens, key=lambda x: x[0])
        print('sorted_tokens', '\t', sorted_tokens)
        print(' predicates', '\t', self.label(self.predicate_tokens))
        # print(' arguments', '\t', self.label(argument_tokens))
        print(' determiner_tokens', '\t', self.label(self.determiner_tokens))
        print('     indefinite_tokens', '\t', self.label(indefinite_tokens))
        print('     definite_tokens', '\t', self.label(definite_tokens))
        print('     name_tokens', '\t', self.label(name_tokens))

        self.format_graph()

        if not coreference:
            self.visualize()
            return

        # -------------------------------------------------------------------------
        # [6] Resolución de la referencia: enumeración de referentes, correferencia
        print('\n', '*' * 100)
        self.coreference()
        self.visualize()
        print('     entity_tokens', '\t', self.label(self.entity_tokens))

        # ----------------------------------------------------------------
        # SIMPLIFICA, pero no atiende a conjuntos no unitarios
        # [7] Unifica los elementos referenciales y enumera los referentes
        print('\n', '*' * 100)
        self.collapse()
        self.visualize()

    def get_predicate_info(self, predicate):
        argument_nodes = [_ for _ in self.search_nodes(start=predicate) if _ in self.entity_tokens]
        # AUX u otro
        event_nodes = [_ for _ in self.search_nodes(start=predicate) if _.match_properties({'pos': ['AUX', 'FLEX']})]
        if event_nodes:
            event_node = event_nodes[0]
        else:
            event_node = None
        # return {
        #     'predicate': self.label(predicate),
        #     'event': self.label(event_node),
        #     'arguments': self.label(argument_nodes),
        #     'valency': len(argument_nodes),
        # }
        return {
            'predicate': predicate,
            'event': event_node,
            'arguments': argument_nodes,
            'valency': len(argument_nodes),
        }

    def base_graph(self, text):
        # visualiza_pasos = True
        # visualiza_pasos = False

        # ----------------------------------------------------
        # [1] adaptación del grafo de Spacy a la clase MyGraph
        doc = nlp(text)
        # displacy.serve(doc, style="dep")
        print('Dependency analysis tree')
        utils.explacy.print_parse_info(nlp, text)
        graph_doc = SpacyGraph(doc)

        # check properties
        print('\n', '*' * 100)
        compulsory_attributes = ['lemma', 'text', 'old_lemma', 'pos', 'text_index']
        for node in graph_doc.nodes:
            if not all([attribute in node.properties for attribute in compulsory_attributes]):
                functions.show_error('ERROR', 'faltan algunos o todos los atributos obligatorios de: ' + node.label)
                print(node.properties)
            elif node.properties['lemma'] != node.properties['old_lemma']:
                print('lematización distinta:', node.properties['lemma'], '\t'*3, node.properties)

        # if visualiza_pasos: graph_doc.visualize()

        # ------------------------------
        # [2] segmentación de la flexión

        def get_flex_tag(flex, lemma):
            # dos modos de presentación
            #   a) PROG.PRS.IND
            #   b) está...ndo
            # (^[^ ]+)(?: .+(n?do))+$
            # remove_regex = re.compile(r'(' + lemma + r'estan?|sie?)[aeiou]?')
            # print(remove_regex.sub('', ))
            """
            (compr|vivi|esta?|sie?)[aeiou]?
                he comprado
                estoy comprando
                he estado comprando

                he vivido
                estoy viviendo

                compraba

                he ...ado
                estoy ...ando
                he ...do ...ando

                he ...do
                estoy ...endo

                ...aba
            """
            TAM_values = [value for key, value in flex.items() if key in ['aspect', 'tense', 'mood']]
            # tag = '.'.join(TAM_values)

            return TAM_values


        # [2a] segmentación en los morfemas persona y TAM:
        #       TAM, 3 posibilidades
        #           verbo sin AUX
        #           AUX + verbo
        #           AUX sin verbo
        #       donde AUX: haber estar ser
        verb_nodes = [node for node in graph_doc.nodes if node.match_properties({'pos': 'VERB'})]
        for node in verb_nodes:
            aux_node = None
            for child in graph_doc.children(node):
                if child.match_properties({'pos': ['AUX']}):
                    aux_node = child
                    break
            if aux_node:  # funde la información TAM y la transfiere a FLEX
                # ¡puede haber varios flex! "he estado viendo" ...
                flex = morphology.get_analytical_flex_info(aux_node.properties, node.properties)
                if flex:  # si ha hallado algo y el primer elemento no es infinitivo
                    flex_TAM = get_flex_tag(flex, node.properties['lemma'])
                    label = '\n'.join(flex_TAM)
                    text = '.'.join(flex_TAM) 
                    print('segmentación FLEX:', aux_node.properties['text'], node.properties['text'], '->', text)

                    aux_node.properties.update({'FLEX': flex_TAM})
                    aux_node.label = label
            else:  # crea un elemento FLEX
                flex = morphology.get_flex_info(node.properties['text'], node.properties['lemma'])
                if flex and flex[0]:  # si ha hallado algo y el primer elemento no es infinitivo
                    flex = flex[0]
                    flex_TAM = get_flex_tag(flex, node.properties['lemma'])
                    label = '\n'.join(flex_TAM)
                    text = '.'.join(flex_TAM) 
                    print('segmentación FLEX:', node.properties['text'], '->', text)

                    new_node = MyNode(label,
                                         {'lemma': text, 'text': text,
                                          'pos': 'FLEX', 'FLEX': flex,
                                          'text_index': node.properties['text_index']})
                    # posteriormente se cambiará el sentido del argumento eventivo, que es externo
                    # el no hacerlo ahora permite que sea accedido por los patrones
                    new_node.label = label
                    graph_doc.create_node(new_node, {})
                    graph_doc.add_edge(node, new_node, '', {})

            has_explicit_subject = [child for child in graph_doc.children(node) if graph_doc.match(child, {'dep': 'nsubj'})]
            # has_explicit_subject = [child for child in graph_doc.children(node) if child.match_properties({'dep': 'nsubj'})]
            # has_explicit_subject = [child for child in node.children if child._dep == 'nsubj']
            if not has_explicit_subject:
                if flex and 'person' in flex:
                    properties = morphology.get_person_properties(flex['person'])
                    properties.update({'text_index': node.properties['text_index']})
                    new_node = MyNode(properties['lemma'], properties)
                    graph_doc.create_node(new_node, {})
                    graph_doc.add_edge(node, new_node, 'nsubj', {})
                    print('segmentación FLEX:', node.properties['text'], '->', text)

        if visualiza_pasos: graph_doc.visualize()

        # --------------------------------
        # [3] Extracción de los predicados
        def print_predicates(predicates, level=0):
            previous_sentence = ''
            for predicate in predicates:
                if predicate.sentence != previous_sentence:
                    previous_sentence = predicate.sentence  # update current
                    print('\n' + fg['green'] + '"' + predicate.sentence + '"' + fg['white'])
                predicate.print(level)

        roots = graph_doc.root_nodes()
        # print('roots', roots, roots[0])
        predicates = [predicate for root in roots for predicate in
                      self.search_predicates(graph_doc, root, root.ref_object.sent.text)]  # , debug_function=debug)]
        print_predicates(predicates)

        # -------------------------------------------------------------------
        # [4a] Fusión de los predicados e incorporación de los nodos restantes
        self.merge_graphs(predicates, erase=True)
        self.reset_nodes_properties()
        self.reset_edges_properties()

        if visualiza_pasos: self.visualize()

        # AUX y FLEX se incorporan con todas sus aristas
        for node in graph_doc.nodes:
            if node.match_properties({'pos': 'AUX'}):  # AUX, ej.: haber estar ser
                if 'FLEX' not in node.properties:
                    flex = morphology.get_flex_info(node.properties['text'], node.properties['lemma'])[0]
                    flex_TAM = get_flex_tag(flex, node.properties['lemma'])
                    label = '\n'.join(flex_TAM)
                    text = '.'.join(flex_TAM) 
                    print('FLEX:', node.properties['text'], '->', text)

                    node.properties['FLEX'] = flex
                    node.label = label
                # found_edges = self.search_edges(end=node)
                # if not found_edges:
                parent = graph_doc.head(node)
                if parent:  # maldito SPACY que considera 'estar' un verbo y una raíz de la oración
                    if node not in self.nodes:
                        self.nodes[node] = {}
                    # self.edges[parent_edge] = {}
                    self.add_edge(graph_doc.head(node), node, '', {})

            if node.match_properties({'pos': ['AUX', 'FLEX']}):
                if node not in self.nodes:
                    self.nodes[node] = {}
                # copia todas las aristas
                for start_edge in graph_doc.search_edges(end=node):
                    found_edges = self.search_edges(start=start_edge, end=node)
                    for e in found_edges:
                        e.label = ''
                    if not found_edges:
                        self.add_edge(start_edge.start, node, '', {})
                node.properties['pos'] = 'FLEX'

        if visualiza_pasos: self.visualize()


        # vincular a eventos los adjuntos: adverbios, EN, predicados secundarios
        # -----------------------------------------------------------------------------
        # [4b] Se añaden los nodos y aristas restantes (adjuntos, determinantes, etc...)
        # ¡Se promueven los determinantes a argumentos de todos los predicados!
        add_nodes = graph_doc.complement(self.nodes)
        # print(add_nodes)
        for node in add_nodes:
            # cuidado con distinguir propiedades del objeto Token y del diccionario Nodes
            # filter only end edges
            if node.match_properties(morphology.sintagma_determinante):
                self.nodes[node] = {}
                for parent_edge in graph_doc.search_edges(end=node):
                    self.edges[parent_edge] = {}
                    parent_edge.label = 0  # 'Det' -> 0
                    # transformación: promueve el determinante a argumento de todos los predicados
                    # para ello:  sustituye al padre por él (nietos) para que los abuelos vinculen al determinante
                    # "los abuelos se encargan del nieto"
                    for grandparent_edge in self.search_edges(end=parent_edge.start):
                        grandparent_edge.end = node  # keep label and everything else
            elif not node.properties['lemma'] == '.':  # and not graph_doc.match(node, {'dep': 'case'}, debug_function=True):
                self.nodes[node] = {}
                for parent_edge in graph_doc.search_edges(end=node):
                    self.edges[parent_edge] = {}

        # ORDEN: DESPUÉS DE LA PROMOCIÓN DE DET. Para evitar que se vuelvan hijos de FLEX
        # FLEX debe dominar al predicado por ser una instrucción sobre este
        # hasta ahora AUX eran FLEX explícitas y FLEX nodos creados
        # todos los AUX pasan a ser recategorizados como FLEX
        # return
        not_reverse_list = ['cuando', 'mientras', 'antes', 'después', 'donde']
        for node in self.nodes:
            if node.match_properties({'pos': ['AUX', 'FLEX']}):
                for edge in self.search_edges(end=node):
                    # self.add_edge(node, graph_doc.head(node), '', {})
                    if edge.start.properties['lemma'] not in not_reverse_list:
                        parent = edge.start
                        if edge.start.match_properties({'pos': ['PROPN', 'DET', 'PRON']}):
                            if self.head(parent):
                                # "La ingeniera es Itsaso"
                                edge.start = self.head(parent)
                        self.reverse_edge(edge)

        if visualiza_pasos: self.visualize()




    def deambiguation(self):
        # A IMPLEMENTAR, es uno de las tareas más complejas
        from nltk.corpus import wordnet as wn
        """
        Synset('calculus.n.01')
        If you only need to know what the most frequent word is, you can do wn.synsets(word)[0]
        since WordNet generally ranks them from most frequent to least frequent.
        (source: Daniel Jurafsky's Speech and Language Processing 2nd edition)
        """
        omit = ['de']

        # implement Deambiguation
        # Assign first synset
        for node in self.nodes.keys():
            if node.match_properties(self.pos_predicate_pattern):
                lemma = node.properties['lemma'].lower()
                if 'synset' not in node.properties and lemma not in omit:
                    if lemma in ontology.extensionKB.wordnet_synset_expansion:
                        synsets = ontology.extensionKB.wordnet_synset_expansion[lemma]
                    else:
                        synsets = wn.synsets(lemma, lang='spa')
                    if synsets:
                        node.properties['synset'] = synsets[0]

    def coreference(self):
        """
        no todos los predicados tienen el mismo peso. El nombre más que las propiedades
        El nombre es más específico respecto a ciertos rasgos del objeto, como forma, función, etc...

        va hacia atrás intentando hallar la mayor correspondencia
            "había una casa grande y otra casa pequeña. La casa grande"
                "La casa grande" debe ser maximalista. Ignora casa (pequeña) y sigue hacia atrás hasta casa grande
        El género puede extraerse del adjetivo, no del verbo
            compré un jarrón y una planta. es muy bonita. ->ella

        ALGORITMO:
            posesivos
                el español da preferencia a presentar la referencia mediante la posesión si la hubiera
                se desdoblan, codifican un predicado de posesión TENER<yo casa>
                EL POSESIVO en sí, se utiliza como determinante ignorando su poseedor
                si es de 1ª o 2ª personas debe existir en el antecedente tal determinante
                si no, da igual
            sucesión de determinantes
            indefinido     SIN ANTECEDENTE
            definido    buscan ANTECEDENTE
                ANTECEDENTE INMEDIATO
                    relativos
                ANTECEDENTE IDÉNTICO
                    formas personales         yo tu nosotros vosotros
                    x no resuelve ciertos casos con plurales. Vi a Marta. Somos pareja ¿sabes? Nosotros (X Y)
                ANTECEDENTE (con puntuaciones)
                    según género
                        sin complemento SN (determinante sin ninguna restricción predicativa)
                    según predicados
                        la casa es grande. el  fue construido
                        con complemento SN
        """

        def ultra_lemma(token):
            # return token.properties['DET']['ultralemma'] if 'ultralemma' in token.properties['DET'] else token.properties['DET']['lemma']
            if 'ultralemma' in token.properties['DET']:
                return token.properties['DET']['ultralemma']
            else:
                return token.properties['DET']['lemma']

        iterator = count(start=0, step=1)

        # son necesarios todos los determinates para hallar el antecedente
        # determiner_tokens = [_ for _ in self.nodes if                              _.match_properties(morphology.determinante)]  # indefinite_tokens + definite_tokens
        # los ordena por posición
        determiners_tuple = sorted([(_.properties['text_index'], _) for _ in self.determiner_tokens],
                                   key=lambda x: x[0])
        determiners_sorted = [_[1] for _ in determiners_tuple]
        for anaphora_index, (position, anaphor) in enumerate(determiners_tuple):
            print(position, anaphor.properties['text'].lower())
            max_distance = 0
            selected_antecedent = None
            selected_label = ''

            if anaphor.match_properties(morphology.definido):  # condición necesaria, no suficiente
                # escoge los potenciales antecedentes y los ordena para que el primero que se procese sea el más próximo
                potenciales_antecedentes = determiners_sorted[0: anaphora_index][::-1]
                # si es un determinante definido y hay potenciales antecedentes se verifican
                if potenciales_antecedentes:  # 4)
                    anaphor_lemma = anaphor.properties['lemma']
                    # anaphor_lemma = get_lemma(anaphor)

                    """ QUE, CUYO... no deberían considerarse antecedentes válidos
                        14 el
                             CON ANTECEDENTE:       9 que
                             CON ANTECEDENTE:       5 uno
                                 1 [{'score': 1, 'relation': 'identity'}]
                             CON ANTECEDENTE:       1 el
                             14 -> uno 	 identity                
                    """
                    # lemas_relativos = ['cuyo', 'cual', 'quien', 'cuanto', 'donde', 'que']
                    if anaphor_lemma in morphology.lemas_relativos:
                        print('\t', 'lemas_relativos')
                        if anaphora_index > 0:
                            selected_antecedent = determiners_sorted[anaphora_index - 1]

                    # morphology.determinante_sin_complemento
                    # lemas_personales = ['yo', 'tu', 'nosotros', 'vosotros', 'me', 'te', 'nos', 'os']
                    elif anaphor_lemma in morphology.lemas_personales:
                        print('\t', 'lemas_personales')
                        for antecedent_index, antecedent in enumerate(potenciales_antecedentes):
                            if antecedent.properties['lemma'] in morphology.lemas_personales:
                                print('\t' * 1, 'CON ANTECEDENTE:      ', antecedent.properties['text_index'],
                                      antecedent.properties['text'])
                                if ultra_lemma(antecedent) == ultra_lemma(anaphor):  # check for identity
                                    selected_antecedent = antecedent
                                    break

                    # definido sin complemento -> coteja género y número
                    elif anaphor.match_properties(morphology.determinante_sin_complemento):
                        print('\t', 'determinante_sin_complemento')
                        # 'él': {'gen': 'masc', 'num': 'sing'},
                        scores = []
                        anaphor_features = anaphor.properties['DET']
                        for antecedent_index, antecedent in enumerate(potenciales_antecedentes):
                            if not (antecedent.properties['lemma'] in morphology.lemas_personales \
                                    or antecedent.properties['lemma'] in morphology.lemas_relativos):  # Filter out
                                print('\t' * 1, 'CON ANTECEDENTE:      ', antecedent.properties['text_index'],
                                      antecedent.properties['text'])
                                antecedent_features = antecedent.properties['DET']

                                selected_features = []
                                if 'num' in anaphor_features and 'num' in antecedent_features:
                                    if anaphor_features['num'] != antecedent_features['num']:
                                        continue
                                    else:
                                        selected_features.append('num:' + anaphor_features['num'])
                                if 'gen' in anaphor_features and 'gen' in antecedent_features:
                                    if anaphor_features['gen'] != antecedent_features['gen']:
                                        continue
                                    else:
                                        selected_features.append('gen:' + anaphor_features['gen'])

                                # factor distancia
                                distance = anaphor.properties['text_index'] - antecedent.properties['text_index']
                                score = len(selected_features) / distance * 10
                                print('\t' * 2, score)
                                scores.append((score, antecedent, selected_features))

                            if scores:
                                # se ordena de mayor a menor puntuación
                                sorted_scores = sorted(scores, key=lambda x: -x[0])
                                selected = sorted_scores[0]
                                selected_antecedent = selected[1]
                                selected_label = '+'.join(selected[2])

                    else:  # definido con complemento -> coteja predicados
                        print('\t', 'else')
                        scores = []
                        # anaphor_predicates = self.search_nodes(end=anaphor)
                        # predicados monovalentes
                        anaphor_predicates = [node for node in self.search_nodes(end=anaphor)
                                              if node.match_properties({'pos': ['ADJ', 'NOUN']})]
                        anaphor_predicates = self.label(anaphor_predicates)
                        for antecedent_index, antecedent in enumerate(potenciales_antecedentes):
                            if not (antecedent.properties['lemma'] in morphology.lemas_personales \
                                    or antecedent.properties['lemma'] in morphology.lemas_relativos):  # Filter out
                                print('\t' * 1, 'CON ANTECEDENTE:      ', antecedent.properties['text_index'],
                                      antecedent.properties['text'])

                                # se puede considerar como u predicado obligatorio
                                if anaphor_lemma in ['su', 'suyo']:  # morphology.lemas_posesivos:
                                    # crea una nueva referencia
                                    # porque el poseedor puede correferenciarse
                                    continue
                                if anaphor_lemma in ['mi', 'tu', 'nuestro', 'vuestro', 'mío',
                                                     'tuyo']:  # morphology.lemas_posesivos:
                                    # if ultra_lemma(antecedent) != ultra_lemma(anaphor):
                                    if antecedent.properties['lemma'] != anaphor_lemma:
                                        continue
                                # antecedent_predicates = self.search_nodes(end=antecedent)
                                antecedent_predicates = [node for node in self.search_nodes(end=antecedent)
                                                      if node.match_properties({'pos': ['ADJ', 'NOUN']})]
                                antecedent_predicates = self.label(antecedent_predicates)
                                resultado = semantics.process_combinations(anaphor_predicates, antecedent_predicates,
                                                                           semantics.find_semantic_relation)

                                # print('\t'*2, 'resultado',  resultado)
                                if resultado:
                                    resultado = [_[0] for _ in resultado]
                                    # suma
                                    score = sum([_['score'] for _ in resultado])
                                    print('\t' * 2, score, resultado)
                                    scores.append((score, antecedent, resultado))

                            if scores:
                                # se ordena de mayor a menor puntuación
                                sorted_scores = sorted(scores, key=lambda x: -x[0])
                                selected = sorted_scores[0]
                                selected_antecedent = selected[1]
                                selected_label = selected[2][0]['relation']


            if selected_antecedent:
                self.add_edge(anaphor, selected_antecedent, selected_label)
                print('\t', position, '->', selected_antecedent.properties['text_index'],
                      selected_antecedent.properties['text'].lower(), '\t', selected_label)
            else:  # no ha encontrado nada, primera mención del determimante definido
                # indefinido o primera mención del determimante definido
                # nombre propio
                self.entity_tokens.append(anaphor)
                print('\t', position, '->', next(iterator))

    def collapse(self):
        # A IMPLEMENTAR: Collapsed graph <<<<<<<<<<<< CREA UN NUEVO GRAFO
        """
        hasta ahora cada token del texto estaba representado en el grafo. Pero se pueden unificar:
            los predicados con mismo synset > synset
            los determiner_tokens correferentes > entity
        """
        # elimina anáforas y predicados redundantes
        # puede haber duplicados "[...] en la casa. La casa es grande"
        # reduce según igualdad de synsets
        iterator = count(start=1)
        # entity_tokens = []
        for determiner_token in self.determiner_tokens:
            if determiner_token in self.entity_tokens:
                determiner_token.label = str(next(iterator))  # enumera referencias
            else:
                antecedent_target = self.search_nodes(start=determiner_token)
                assert len(antecedent_target) == 1, 'Sólo puede haber un destino por cada anáfora'
                self.bypass_node(determiner_token)

        """ [b] Crea forma lógica participante(predicado1, ...)
            2(EN, colina).
            3(EN, DE->HECHO_DE, grande, construir, casa, casa).
            1(TENER).
            4(construir, TENER, abuelo).        
        """
        print('Universo de interpretación:')
        for entity_token in self.entity_tokens:
            predicate_nodes = [_ for _ in self.search_nodes(end=entity_token) if _ in self.predicate_tokens]
            labels = ', '.join([str(_.label) for _ in predicate_nodes])
            print(f"{fg['orange']}{str(entity_token.label)}({fg['white']}{labels}{fg['orange']}){fg['white']}.")

        # print('\n')
        """ [c] Crea forma lógica predicado(participante1, ...)
            en(3, 2).
            casa(3).
            colina(2).
            de->hecho_de(3).
        """
        monovalent_predicate_tokens = [_ for _ in self.predicate_tokens if self.get_predicate_info(_)['valency'] == 1]
        for predicate in monovalent_predicate_tokens:
            labels = ', '.join([str(_.label) for _ in self.get_predicate_info(predicate)['arguments']])
            print(f"{fg['orange']}{str(predicate).upper()}({fg['white']}{labels}{fg['orange']}){fg['white']}.")

    # region "Display"
    def label(self, node):
        if isinstance(node, list) or isinstance(node, set):
            return [self.label(_) for _ in node]
        else:
            try:
                return node.label
            except:
                return '?'

    def format_graph(self):
        """ FORMAT
        1) functores
            distinguir
                ADJ y NOUN monovalentes PROPN
                ['VERB', 'ADV', 'ADP']
        2) determinantes y nombres propios (argumentos)
        3) la negación <<<<<<<<<<<<<<<<<<<
        4) lo creado
        """
        # self.predicate_tokens = []
        # self.flex_tokens = []
        # self.determiner_tokens = []  # nombres propios y determinantes
        # self.entity_tokens = []  # nombres propios y los determinantes que no sean anáfora (que no sean origen de una arista)

        for node in self.nodes.keys():
            properties = {}

            arity = len(self.search_edges(start=node))  # valencia, <<<<<<< PERO quita ADV y otros
            # print(arity, node, node.properties)
            if node.match_properties({'pos': ['PROPN']}):
                properties = {'shape': 'doublecircle'}  # doubleoctagon Mcircle
            elif node.match_properties(morphology.determinante):
                node.label = node.properties['text'].lower()
                properties = {'shape': 'doublecircle'}  # doubleoctagon Mcircle
            elif node.match_properties({'pos': ['AUX', 'FLEX']}):  # AUX, ej.: haber
                properties = {'fontcolor': 'gray19', 'color': 'gray', 'shape': 'Mcircle', 'fontsize': '10'}

            elif node.match_properties({'pos': ['SCONJ']}):
                properties = {'shape': 'invhouse'}
            # elif node.match_properties(self.pos_predicate_pattern):
            elif arity > 0:
                if node.match_properties({'pos': ['VERB', 'ADP']}):  # VERB ADP
                    properties = {'fontcolor': 'red', 'shape': 'invhouse', 'fontsize': '18'}
                elif node.match_properties({'pos': ['ADV', 'ADJ', 'NOUN']}):  # ADV ADJ NOUN
                    # if arity > 1:
                    #     properties = {'fontcolor': 'red', 'shape': 'invhouse', 'fontsize': '18'}
                    # else:
                    properties = {'fontcolor': 'black', 'shape': 'box', 'fontsize': '18'}
            else:
                # print('NO', node, node.properties)
                properties = {'fontcolor': 'gray50'}

            if node.ref_object is None:
                properties.update({'fontcolor': 'blue'})

            self.update_node_properties(node, properties)

    def print_latex(data):
        previous_start = None
        for predicate, pattern in data:
            if predicate['start'] != previous_start:
                previous_start = predicate['start']  # update current
                sentence = '"' + predicate['start'].sent.text + '"'
                print(f'\\centerline{{oración {sentence}}}')

            subtree = '"' + ' '.join([child.text for child in predicate['start'].subtree]) + '"'
            token_dict = patterns.create_dictionary(predicate['start'])
            print(f"""
                \\vspace*{{40px}}
                % {subtree}
                \\centerline{{segmento {subtree}}}
                {patterns.dict_to_latex_avm_min(token_dict)}

                \\vspace*{{10px}}
                Esta estructura de dependencias coincide con el patrón:
                \\vspace*{{10px}}

                \\centerline{{patrón {pattern['NAME']}}}
                {patterns.dict_to_latex_avm_min(pattern)}

                \\vspace*{{10px}}
                Resultando en el siguiente predicado:
                \\vspace*{{10px}}

                \\newpage
            """)

    # endregion

#endregion


# def NLG(self):
#     # 0 es una casa grande y roja que V tal y tal
#     pass


if __name__ == "__main__":
    text = 'El patio de mi casa es particular. Cuando llueve se moja.'
    doc = nlp(text)
    explacy.print_parse_info(nlp, text)

    graph = SpacyGraph(doc)
    graph.visualize()
