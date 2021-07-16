# -*- coding: utf-8 -*-
# by Alejandro Rojo Gualix 2021-06
import sys
import json

# N+N
# PP
# ADJ y VERBOS
patterns = {
'es': [
    # N N
    #
    #
    # aposición ¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡ <<<<<<<<<<<<<<<<<<<<<<
    { 'NAME': 'N N COP',  # Mi hija es ingeniera
        'pos': ['NOUN', 'PROPN', 'PRON'], '#':0, 
        'CHILDREN': [
            {  'dep': 'nsubj', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':1 },
            { 'pos': 'AUX', 'lemma': 'ser' },
        ],
    },

    # entidades multipalabra
    { 'NAME': 'entidad N',
        'pos': 'PROPN', '#':0, 
        'CHILDREN': [
            { 'dep': ['flat'], '#':0 },
        ],
    },



    { 'NAME': 'det-posesivo',   # mis ojos / mi casa
        'pos': ['NOUN', 'PROPN'], '#':1, 'CHILDREN': [
            { 'pos': 'DET', 'lemma': morphology.mappings['posesivos'][0], '#':2}
        ]
    },

    # "La vecina cuya casa ardió ."     vecina ardió casa cuya  
    # "La ciudad cuyo ayuntamiento es enorme ."     ciudad enorme ayuntamiento cuyo
    { 'NAME': 'TENER-cuyo',  # Mi hija es ingeniera
        'pos': ['NOUN', 'PROPN', 'PRON'], '#':1, 'CHILDREN': [
            { 'CHILDREN': [  # no especificado: nos es indiferente si es un verbo o un adjetivo el núcleo de la suboración
                {'pos': ['NOUN', 'PROPN', 'PRON'], '#':2, 'CHILDREN': [
                    { 'lemma': 'cuyo', '#':0, 'fRENAME': 'TENER-cuyo' }
                ]}
            ] },
        ],
    },

    # PP
    #
    # atención a nmod y acl. Los 2 patrones '...COP' resuelven también suboraciones adjetivas
    # caso especial (por eso tiene preferencia en la lista) para desambiguar el valor de 'de'
    { 'NAME': 'NOUN PP+N',
        'pos': 'NOUN',
        'ALTERNATIVES': [
            # nombres deverbales o ción|mi?ento|aj[eo]|encia|ura|zón|dora?|der[ao]
            # https://literaturaespanolasigloxxi.wordpress.com/2020/06/20/sustantivos-deverbales-en-espanol/
            { 'NAME': 'nombre_deverbal+args',
                'text': re.compile(r'(?:ción|mi?ento|aj[eo]|encia|ura|zón|dora?|der[ao])$'), '#':0, 'CHILDREN': [  # using regular expression
                    { 'dep': 'nmod', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':1, 'CHILDREN': [  # 'dep': 'nmod' es importante puesto que una oración puede verificarse doblemente como NdeN y NCOPdeN; como esta "El libro que es de Pepe ."
                        { 'dep': 'case', 'lemma': ['de', 'del', 'por', 'a', 'al', 'con'] }
                    ]}
                ]
            },
            { 'NAME': 'de', '#':1,  'CHILDREN': [
                { 'dep': 'nmod', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':2, 'CHILDREN': [  # 'dep': 'nmod' es importante puesto que una oración puede verificarse doblemente como NdeN y NCOPdeN; como esta "El libro que es de Pepe ."
                    { 'dep': 'case', 'lemma': ['de', 'del', 'con'], '#':0 }  # familia con dos hijos 
                ]}
            ]},
            { 'NAME': 'sin de', '#':1, 'CHILDREN': [
                { 'dep': 'nmod', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':2, 'CHILDREN': [ # 'dep': 'nmod' es importante puesto que una oración puede verificarse doblemente como NdeN y NCOPdeN; como esta "El libro que es de Pepe ."
                    { 'dep': 'case', '#':0 }
                ]}
            ]},

        ]
    },

    { 'NAME': 'NOUN PP+N COP', '#':2,
        'pos': ['NOUN', 'PROPN', 'PRON'], 
        'CHILDREN': [
            { 'pos': 'AUX', 'lemma': 'ser' },
            {  'dep': 'nsubj', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':1 },
            { 'dep': 'case', '#':0,
                'ALTERNATIVES': [
                    { 'NAME': 'N de N COP', 
                        'lemma': ['de', 'del', 'con']
                    },
                    { 'NAME': 'N+PP+N COP' },  # el complementario
                ],
            },
        ],
    },

    # ESTAR
    #    es ROOT, a diferencia de SER que siempre es AUX y depende del atributo
    #
    { 'NAME': 'estar+PP',  # "La bicicleta está en la pared ."
        'lemma': 'estar',
        'CHILDREN': [
            {  'dep': 'nsubj', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':1 },
            { 'dep': 'obl', '#':2, 'CHILDREN': [
                { 'dep': 'case', '#':0 }
            ]}
        ],
    },
    { 'NAME': 'estar+ADVPP',  # "Saturno estaba delante de mis ojos ."
        'lemma': 'estar',
        'CHILDREN': [
            {  'dep': 'nsubj', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':1 },
            { 'dep': 'advmod', '#':0, 'CHILDREN': [
                { 'dep': 'obl', '#':2 }
            ]}
        ],
    },


    # el tiempo muchas veces se expresa sin 'en' "Hablamos la próxima semana" pero "Nos vimos en febrero"
    { 'NAME': 'lugar o tiempo',  # "Pepe ronca en el sofá que compramos."
        'pos': 'VERB',
        'CHILDREN': [  # relative 'dep': 'acl', 
            {  'dep': 'nsubj', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':1 },
            { 'dep': 'obl', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':2, 'CHILDREN': [ # 'dep': 'nmod' es importante puesto que una oración puede verificarse doblemente como NdeN y NCOPdeN; como esta "El libro que es de Pepe ."
                { 'dep': 'case', 'lemma': 'en', '#':0, 'fRENAME': 'ESTAR' }
            ]}
        ],
    },


    # amod: adjetivos PARTICIPIOS o no PARTICIPIOS
    # aunque 'la silla comprada' y 'la silla fue comprada' tengan un parecido evidente, en tanto que el participio simplifica una suboración
    # no obstante, son analizadas como dos categorías diferentes: adj y verbo respectivamente
    # aquí se ocupa del adj
    #
    { 'NAME': 'adj',
        'pos': 'NOUN', 
        'ALTERNATIVES': [
            { 'NAME': 'adj-participio-por',  # "La casa arruinada por el fuego ."
                '#':2, 'CHILDREN': [
                    { 'dep': 'amod', '#':0, 'CHILDREN': [
                        { 'pos': ['NOUN', 'PROPN', 'PRON'], '#':1, 'CHILDREN': [
                            { 'dep': 'case', 'lemma': 'por' }  # complemento agente
                        ]}
                    ]}
                ]
            },
            # adjetivo o adjetivo participial
            { 'NAME': 'sin por',  # La casa adecuada para vivir.
                '#':1, 'CHILDREN': [ 
                    { 'dep': 'amod', '#':0, 
                        'OPTIONAL_CHILDREN': [
                            { '#':2, 'CHILDREN': [  # cualquier token, en principio verbo o nombre
                                { 'lemma': ['para', 'según'], 'pos': 'ADP' }
                            ]}
                        ]
                    }
                ],
            },
        ]
    },


    { 'NAME': 'adj COP',
        'pos': 'ADJ', '#':0,
        'CHILDREN': [ 
            { 'dep': 'cop', 'pos': 'AUX' },  # estar o ser
            {  'dep': 'nsubj', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':1 },
        ],
        'OPTIONAL_CHILDREN': [
            { '#':2, 'CHILDREN': [
                { 'lemma': ['para', 'según'], 'pos': 'ADP' }  # La casa es adecuada para vivir.
            ]}
        ]
    },

    # sujeto objeto OI

    # Debe estar antes que 'Oración', pues la pasiva es un caso particular que reordena los complementos
    # el núcleo es el verbo con contenido léxico, y el auxiliar (portador del sintagma flexivo) depende de él
    { 'NAME': 'Oración',  # "El libro fue regalado a Juan por Marta ."
        'pos': 'VERB', '#':0,
        'ALTERNATIVES': [
            { 'NAME': 'pasiva SER',  # "El libro fue regalado a Juan por Marta ."
                'CHILDREN': [
                    { 'pos': 'AUX', 'lemma': 'ser' },
                    {  'dep': 'nsubj', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':2},
                ],
                'OPTIONAL_CHILDREN': [
                    { '#':1, 'CHILDREN': [
                        { 'dep': 'case', 'lemma': 'por' }  # complemento agente
                    ]},
                    { 'dep': 'obj', '#':3, 'CHILDREN': [  # iobj -> obj
                        { 'dep': 'case', 'lemma': 'a' }
                    ]}
                ]
            },
            { 'NAME': 'ELSE',  #
                'CHILDREN': [
                    {  'dep': 'nsubj', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':1 },
                ],            
                'OPTIONAL_CHILDREN': [  # relative 'dep': 'acl', 
                    { 'dep': ['ccomp', 'xcomp'], '#':2 },  # mark:que ccomp:volverías / xcomp:volver. "Me dicen que el libro es de esa [ccomp:]mujer ."
                    { 'dep': 'obj', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':2 },
                    { 'dep': 'iobj', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':3 }
                ],
            }
        ]
    }


]  # 'es'
}



"""
import pprint
pprint.pprint(patterns[0]['include'], width=1)
import json
print(json.dumps(patterns[0]['include'], indent=4))
"""

"""
%  escape braces: \{ \}
%  : -> &
%  , -> \\
% ' ->
% _ -> -
"""
def dict_to_latex_avm(obj, level=0):
    if level == 0:
        print('\\vspace*{100px}')
        print(f"\n% {pattern['name']}")
        print(pattern['name'])
        print('\\vspace*{10px}')
        # print(f"\\centerline{{{pattern['name']}}}")
        print('\\avm{')  # \n\t', end='
    indent = '\t' * (level + 1)
    
    if isinstance(obj, dict):
        if '#' in obj:
            print(f"\n{indent}\\{obj['#']} \{{")
            del obj['#']
        else:    
            print(f'\n{indent}\{{')
        # Iterate over all key-value pairs of dictionary by index

        for index, (key, value) in enumerate(obj.items()):        
        # for key, value in obj.items():
            tt = '' if index == 0 else '\\\\ '
            print(f'{indent}{tt}{key} & ', end='')
            dict_to_latex_avm(value, level + 1)
        print(f'\n{indent}\}}')   
    elif isinstance(obj, list):
        print(f'\n{indent}[')
        for index, value in enumerate(obj):
            tt = '' if index == 0 else '\\\\ '
            print(indent + tt, end='')
            # print(f'{indent}{tt}{key} & ', end='')
            dict_to_latex_avm(value, level + 1)
        print(f'\n{indent}]')
    # elif isinstance(obj, str):
    # elif isinstance(obj, bool):        
    else: # atomic
        print(obj)
        
    if level == 0:
        print('}')


def dict_to_latex_avm2(obj, level=0):
    if level == 0:
        print('\\avm{\n\t', end='')
    indent = '\t' * (level + 1)
    
    if isinstance(obj, dict):
        print(f'\{{')
        # Iterate over all key-value pairs of dictionary by index
        for index, (key, value) in enumerate(obj.items()):        
        # for key, value in obj.items():
            tt = '' if index == 0 else '\\\\ '
            print(f'{indent}{tt}{key} & ', end='')
            dict_to_latex_avm(value, level + 1)
        print(f'{indent}\}}')   
    elif isinstance(obj, list):
        print(f'[', end='')
        for index, value in enumerate(obj):
            tt = '' if index == 0 else '\\\\ '
            # print(f'{indent}{tt}{key} & ', end='')
            dict_to_latex_avm(value, level + 1)
        print(f'{indent}]')
    # elif isinstance(obj, str):
    # elif isinstance(obj, bool):        
    else: # atomic
        print(obj)
        
    if level == 0:
        print('}')



# diction= { 'name': 'adj', 'predicate': {'name': 'adj'}}
# dict_to_latex_avm(diction)


def dict_to_latex_avm5(pattern):
    output = json.dumps(pattern, indent=4)    
    print(output)


# Para ejecutar desde el exterior
if __name__ == "__main__":
    print('__main__')

    # 'f[^']+': ?([^,\s])+,
    # 
    item = patterns['es'][0]
    print(item)
    dict_to_latex_avm(item)

    sys.exit(0)
    for pattern in patterns['es']:
        dict_to_latex_avm(pattern['HAS'])