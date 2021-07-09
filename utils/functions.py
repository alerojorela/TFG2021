# -*- coding: utf-8 -*-
# by Alejandro Rojo Gualix 2021-06
import re


# Preparado para presentación de colores en consola. Basado en:
# https://stackoverflow.com/questions/27265322/how-to-print-to-console-in-color
fg = {'black': '\033[30m', 'red': '\033[31m', 'green': '\033[32m', 'orange': '\033[33m', 
    'blue': '\033[34m', 'magenta': '\033[35m', 'cyan': '\033[36m', 'white': '\033[37m'}
bg = {'black': '\033[40m', 'red': '\033[41m', 'green': '\033[42m', 'orange': '\033[43m',
    'blue': '\033[44m', 'magenta': '\033[45m', 'cyan': '\033[46m', 'white': '\033[47m'}


"""
┃ agr  = ┃ number = 'singular' ┃ ┃
┃        ┃ person = 3          ┃ ┃
┃                                ┃
┃ type = 'NP'                    ┃

"""


def matrix2_to_bool(matrix):
    bool_matrix = []
    for row in matrix:
        bool_matrix.append([bool(_) for _ in row])
    return bool_matrix


def is_bijection_matrix(bool_matrix):
    for row in bool_matrix:
        # if row.count(True) > 1:
        if len([_ for _ in row if _]) > 1:
            return False
    transposed_matrix = [*zip(*bool_matrix)]  # list(zip(*table))
    for col in transposed_matrix:
        # if col.count(True) > 1:
        if len([_ for _ in col if _]) > 1:
            return False
    return True


def force_bijection_matrix(bool_matrix):
    """ This function selects an equivalent matrix that has bijection between rows and columns

    My program checks items against patterns. I'll render patterns as rows and items as columns.
    | matches? | item1 | item2 | item  |
    | -------- | ----- | ----- | ----- |
    | pattern1 | True  | False | False |
    | pattern2 | False | True  | True  |
    | pattern3 | True  | True  | True  |
    However an item can only be selected once. So there must be just one True per column and one True per row. So only the following two alternatives are valid.

    alternative 1)
    | matches? | item1 | item2 | item  |
    | -------- | ----- | ----- | ----- |
    | pattern1 | True  | False | False |
    | pattern2 | False | True  | False |
    | pattern3 | False | False | True  |

    alternative 2)
    | matches? | item1 | item2 | item  |
    | -------- | ----- | ----- | ----- |
    | pattern1 | True  | False | False |
    | pattern2 | False | False | True  |
    | pattern3 | False | True  | False |

    TESTS:

    lista_bool = [
        [True, True],
        [False, True],
    ]
    # >> [[True, False], [False, True]]
    lista_bool = [
        [True, True, False],
        [False, True, False],
    ]
    # >> [[True, False, False], [False, True, False]]

    lista_bool = [
        [True, True, False],
        [False, True, False],
        [True, False, True],
    ]
    # >> [[True, False, False], [False, True, False], [False, False, True]]
    lista_bool = [
        [True, False, False],
        [False, True, True],
        [True, True, True],
    ]
    # >> [[True, False, False], [False, True, False], [False, False, True]]
    # >> [[True, False, False], [False, False, True], [False, True, False]]
    lista_bool = [
        [False, False, False],
        [False, True, True],
        [False, True, True],
    ]
    # >> [[True, False, False], [False, True, False], [False, False, True]]
    # >> [[True, False, False], [False, False, True], [False, True, False]]
    # >> [[False, True, False], [False, False, True], [True, False, False]]

    """
    def recursive(residue_matrix, new_matrix=[]):
        if not residue_matrix:
            if is_bijection_matrix(new_matrix):
                alternatives.append(new_matrix)
        else:
            first_row = residue_matrix[0]
            # if first_row.count(True) > 1:
            if len([_ for _ in first_row if _]) > 1:
                for id_col, col in enumerate(first_row):
                    if col:
                        # new_row = [False] * len(first_row)  # just one can be True
                        # new_row[id_col] = True
                        new_row = [None] * len(first_row)  # just one can be True
                        new_row[id_col] = col
                        recursive(residue_matrix[1:], [*new_matrix, new_row])
            else:  # no changes
                recursive(residue_matrix[1:], [*new_matrix, first_row])

    if not bool_matrix or (len(bool_matrix) == 1 and len(bool_matrix[0]) == 1):
        return bool_matrix
    else:
        alternatives = []
        recursive(bool_matrix)
        return alternatives


""" ALLOWS UNBOUND ASSIGNMENT
Adds an item to a list in index position. If index is out of bounds, None items are inserted between
aver = [0, 1]
assign_to_list(aver, 5, 5)
assign_to_list(aver, 'UNO', 1)
print(aver)

compile_lists es una extensión del método 'insert' y por tanto permite introducir un elemento en una lista
pero además permite:
    1) si su índice es superior a la dimensión de la lista, rellenando con None
    2) compile_list=True
        en vez de reemplazar un valor preexistente por otro nuevo, añadirlo a una sublista en esa posición
"""
def assign_to_list(this_list, index, value, compile_list=False):
    if index >= len(this_list):
        for n in range(0, index - len(this_list)):
            this_list.append(None)
        this_list.append(value)
    else:
        if this_list[index] is None or not compile_list:
            this_list[index] = value  # creates or overwrites
        else:  # append to a list
            if isinstance(this_list[index], list):
                this_list[index].append(value)
            else:
                this_list[index] = [this_list[index], value]


def assign_to_dict(this_dict, key, value): # , compile_list=False):
    if not key in this_dict:
        this_dict[key] = value  # creates or overwrites
    else:  # append to a list
        if isinstance(this_dict[key], list):
            this_dict[key].append(value)
        else:
            this_dict[key] = [this_dict[key], value]  # two items begin a list


def replace_item(obj, search_for, replacement):
    if search_for in obj:
        index = obj.index(search_for)
        obj[index] = replacement


# via https://stackabuse.com/python-how-to-flatten-list-of-lists/
def flatten(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
    return list_of_lists[:1] + flatten(list_of_lists[1:])


# toma dos listas, si halla un elemento en la primera devuelve el coposicionado en la otra
def map(value, arrs):
    index = arrs[0].index(value)
    if index == -1:
        return None
    else:
        return arrs[1][index]



# console
def show_error(error_type, msg):
    print(f"{fg['red']}{error_type}{fg['white']}: {msg}")

def print_debug(msg, indent=''):
    print(indent + f"{fg['blue']}{msg}{fg['white']}")

def debug_dir(obj, indent = ''):
    for attr in (a for a in dir(obj)):
        try:
            print(indent, f"{fg['blue']}{attr.ljust(20)}{getattr(obj, attr)}{fg['white']}")
        except:
            print(indent, "Something went wrong")


format_pattern_regex = r'\d+'
""" similar to str.format but allows omitted parameters
e.g.
pattern: '0 < 3 1 >'
parameters: ['a', 'b', 'c']
return: 'a <  b >'
"""
def format_pattern(pattern: str, parameters: list):
    output = ''
    last_pos = 0
    for match in re.finditer(format_pattern_regex, pattern):
        index = int(match.group())
        replacement = parameters[index] if (index < len(parameters) and parameters[index] is not None) else ''  # allow optional parameters
        output += pattern[last_pos:match.start()] + replacement
        last_pos = match.end()
    output += pattern[last_pos:]
    return output


def regex_with_context(regex, text, context_width = 35):
    import re
    # obtenemos números en su contexto para evaluar si son fechas
    # regex = re.compile(r'(\d+)')
    # print(regex.findall(text))
    for i in regex.finditer(text):
        start, end = i.span()
        start = 0 if start - context_width < 0 else start - context_width
        end = len(text) if end + context_width > len(text) else end + context_width
        context = text[start: end]
        print(i.group(0).ljust(15) + context)
