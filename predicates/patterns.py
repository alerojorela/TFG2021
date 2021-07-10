# -*- coding: utf-8 -*-
# by Alejandro Rojo Gualix 2021-06
import re

# MÍOS
import predicates.morphology as morphology
import ontology.semantics as semantics

""" incongruencias copulativas
ROOT atributo
      ┌──► Es       cop      ser      AUX       
      │┌─► muy      advmod   mucho    ADV       
      └┼── grande   ROOT     grande   ADJ       
       └─► .        punct    .        PUNCT     
       ┌─► Está     cop      estar    AUX       
       ├── nueva    ROOT     nuevo    ADJ       
       └─► .        punct    .        PUNCT     
ROOT estar
  ┌┬────── Está     ROOT     estar    VERB      
  │└─►┌┬── enfrente advmod   enfrente ADV       
  │   │└─► de       fixed    de       ADP       
  │   └──► ti       obl      tú       PRON      
  └──────► .        punct    .        PUNCT     
┌┬──────── Estaba   ROOT     estar    VERB      
│└─►┌──┬── delante  advmod   delante  ADV       
│   │  └─► de       fixed    de       ADP       
│   │  ┌─► mis      det      mi       DET       
│   └─►└── ojos     obl      ojo      NOUN      
└────────► .        punct    .        PUNCT     
ROOT estar pero en no depende directamente de él. Lo considera caso
   ┌────── Está     ROOT     estar    VERB      
   │  ┌──► en       case     en       ADP       
   │  │┌─► la       det      el       DET       
   └─►└┴── pared    obl      pared    NOUN 
"""

NP_head = ['NOUN', 'PROPN', 'PRON']

recursive_keys = ['CHILDREN', '¬CHILDREN', 'OPTIONAL_CHILDREN', 'ALTERNATIVES']
function_keys = ['fPOSTPROC', 'fNOTFOUND', 'fRENAME']
""" function_keys son capaces de crear un token o modificar las propiedades de uno existente
fPOSTPROC actúa sobre el predicado en su totalidad, no sobre un elemento
    sin RETURN pues modifica predicado
    LO QUE SEA
fNOTFOUND crea un token
    RETURN {}
fRENAME. según tipo
    str LABEL 
    NO {} UPDATE 
    f() cualquier acción 
    ¿update?

CAMPOS OBLIGATORIOS PARA TODOS LOS TOKENS
{
    'mylemma': ,
    'text': ,
    'lemma': ,
    'pos': ,
    'text_index': 
}
"""
compulsory_attributes = ['mylemma', 'text', 'lemma', 'pos', 'text_index']


def get_sentences(section=None, exclude_checked=False):
    if section is None or section == '':
        sections = [_['SAMPLES'] for _ in patterns['es']]
    else:
        sections = [_['SAMPLES'] for _ in patterns['es'] if _['NAME'] == section]

    sentences = []
    for section in sections:
        if exclude_checked:
            sentences.extend([s for s in section if s[0] != '✅'])
        else:
            sentences.extend([s[1:] if s[0] == '✅' else s for s in section])

    return sentences
    text = '. '.join(sentences)


""" PRINCIPALES SECCIONES
ARGUMENTOS EVENTIVOS
POSESIVOS
ORACIÓN CON NÚCLEO SEMÁNTICO NO VERBAL
    APOSICIÓN
AMOD: adjetivos PARTICIPIOS o no PARTICIPIOS
HABER
ORACIONES
"""
# N+N
# PP
# ADJ y VERBOS
patterns = {
    'es': [
        # entidades multipalabra
        {'NAME': 'entidad N', 'SAMPLES': [

        ],
         'pos': 'PROPN', '#': 0,
         'CHILDREN': [
             {'dep': ['flat'], '#': 0},
         ],
         },

        # ******************************************************************
        # ARGUMENTOS EVENTIVOS
        #
        #
        # los predicados poseen, además de los argumentos habituales, uno más que representa al
        # acontecimiento completo, y que recibe el nombre de argumento eventivo:
        # ADV -MENTE: operación subsectiva con el verbo
        {'NAME': 'adverbio -mente', 'SAMPLES': [
            # ejemplos en Escandell, 2004
            '✅Mario come lentamente.',
            '✅David levantó al bebé cuidadosamente.',
            '✅La matrícula ha aumentado considerablemente.',
        ],
         'pos': 'VERB',
         'CHILDREN': [
             # {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 1},
             {'pos': ['FLEX', 'AUX'], '#': 1},
             {'text': re.compile(r'mente$'), 'dep': 'advmod', 'pos': 'ADV', '#': 0}
         ],
         },

        {'NAME': 'predicación secundaria - adj', 'SAMPLES': [
            '✅Nombraron delegada a Laura.',
            '✅Avanzó alicaído.',
            '✅Llegó entusiasmado a la excursión.',
            '✅Compró barato su piso.',  # piso barato / persona barata
            '✅Compró entusiasmada su piso.',  # piso entusiasmada / persona entusiasmada
        ],
         'pos': 'VERB',
         'CHILDREN': [
             # {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 1},
             {'pos': ['FLEX', 'AUX'], '#': 1},
             {'dep': 'obj', 'pos': 'ADJ', '#': 0}
         ],
         },

        {'NAME': 'predicación secundaria - gerundio', 'SAMPLES': [
            'Respondió considerando nuestra opinión.',
        ],
         'pos': 'VERB',
         'CHILDREN': [
             # {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 1},
             {'pos': ['FLEX', 'AUX'], '#': 1},
             {'text': re.compile(r'ndo$'), 'dep': 'advcl', 'pos': 'VERB', '#': 0}
         ],
         },

        # O' ADVERBIALES TIEMPO
        # cuando, mientras, antes de que, despueś de que
        {'NAME': 'O adv tiempo', 'SAMPLES': [
            '✅Comía mientras estudiaba.',
            # '✅Me alegré cuando te encontré por la calle',  # misma persona yo-me
            # 'Saldremos cuando acabes de estudiar',
            # 'Fui después de que terminaras de hablar',
            # 'Me explicaron el motivo antes de que te fueras',  # ANTES < explicar ir > ¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿
        ],
         'pos': ['VERB'],
         'CHILDREN': [
             {'pos': ['FLEX', 'AUX'], '#': 1},
             {'pos': ['VERB'], 'dep': 'advcl',
              'CHILDREN': [
                  {'pos': ['FLEX', 'AUX'], '#': 2},
                  {'pos': 'SCONJ', 'dep': 'mark', 'lemma': ['cuando', 'mientras', 'antes', 'después'], '#': 0}
              ]
              }
         ]
         },

        # LUGAR
        # Extracción del complemento de lugar a cualquier verbo
        # a) "Hablé en la cocina" -> en <yo cocina>
        # b) argumento eventivo  -> en <evento cocina>
        {'NAME': 'verbo+EN', 'SAMPLES': [
            '✅Ahora ronca en el sillón.',
        ],
         'pos': 'VERB',
         'CHILDREN': [
             # {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 1},
             {'pos': ['FLEX', 'AUX'], '#': 1},
             {'dep': 'obl', 'pos': NP_head, '#': 2, 'CHILDREN': [
                 # 'dep': 'nmod' es importante puesto que una oración puede verificarse doblemente como NdeN y NCOPdeN; como esta "El libro que es de Pepe ."
                 {'dep': 'case', 'lemma': 'en', '#': 0}
                 # {'dep': 'case', 'lemma': 'en', '#': 0, 'fRENAME': 'EN'}
                 # {'dep': 'case', '#': 0}
             ]}
         ],
         },

        {'NAME': 'verbo+advmod', 'SAMPLES': [
            'Pepe dome delante de la televisión.',  # error de Spacy
        ],
         'pos': 'VERB',
         'CHILDREN': [
             # {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 1},
             {'pos': ['FLEX', 'AUX'], '#': 1},
             {'dep': 'advmod', '#': 0, 'CHILDREN': [
                 {'dep': 'obl', '#': 2}
             ]}
         ],
         },

        #         Dependency analysis tree
        # Dep tree Token     Dep type Lemma     Part of Sp
        # ──────── ───────── ──────── ───────── ──────────
        #     ┌─►  La        det      el        DET
        #  ┌─►└──  bicicleta nsubj    bicicleta NOUN
        # ┌┴─────  está      ROOT     estar     VERB
        # │  ┌──►  en        case     en        ADP
        # │  │┌─►  la        det      el        DET
        # └─►└┴──  pared     obl      pared     NOUN
        #
        # {'ALTERNATIVE': [
        #     {'NAME': '1', 'dep': 'obl', 'pos': NP_head, '#': 2, 'CHILDREN': [
        #         {'dep': 'case', 'lemma': 'en', '#': 0, 'fRENAME': 'EN'}
        #         # {'dep': 'case', '#': 0}
        #     ]},
        #     {'NAME': '2', 'dep': 'advmod', '#': 0, 'CHILDREN': [
        #         {'dep': 'obl', 'pos': NP_head, '#': 2}
        #     ]},
        # ]}
        {'NAME': 'ESTAR+EN', 'SAMPLES': [
            'La bicicleta está en la pared',
        ],
         'lemma': 'estar', '#': 3,  # CORRECCIÓN PARA SPACY QUE CONSIDERA ESTAR VERBO Y LO PONE EN LA RAÍZ !!!
         'CHILDREN': [
             {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 1},
             {'dep': 'obl', 'pos': NP_head, '#': 2, 'CHILDREN': [
                 {'dep': 'case', 'lemma': 'en', '#': 0, 'fRENAME': 'EN'}
             ]},
         ],
         },

        {'NAME': 'ESTAR+advmod', 'SAMPLES': [
            '✅La casa de Alberto está enfrente de ti',
            '✅Está enfrente de ti',
            '✅Saturno estaba delante de mis ojos',
        ],
         'lemma': 'estar', '#': 3,  # CORRECCIÓN PARA SPACY ¡¡¡QUE CONSIDERA ESTAR VERBO Y LO PONE EN LA RAÍZ !!!
         'CHILDREN': [
             {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 1},
             {'dep': 'advmod', '#': 0, 'CHILDREN': [
                 {'dep': 'obl', 'pos': NP_head, '#': 2}
             ]},
         ],
         },

        # INUTIL
        # {'NAME': 'AUX Prep', 'SAMPLES': [
        #     'La bicicleta está en la pared',
        #     'La casa de Alberto está enfrente de ti',
        #     'Está enfrente de ti',
        #     'Saturno estaba delante de mis ojos',
        # ],
        #  # 'pos': 'VERB', 'lemma': 'estar', '#': 0,
        #  'pos': 'ADP', '#': 0,
        #  'CHILDREN': [
        #      # {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 1},
        #      {'pos': ['FLEX', 'AUX'], '#': 1},
        #      {'dep': 'obl', 'pos': NP_head, '#': 2}
        #  ],
        #  },

        {'NAME': 'EN←donde', 'SAMPLES': [
            '✅La ciudad donde nos conocimos.',  # -> nos conocimos en La ciudad
            '✅La casa donde nací',  # -> nací en la casa
        ],
         'pos': NP_head, '#': 2,  # antecedente
         'CHILDREN': [
             {'pos': 'VERB',  # relative 'dep': 'acl',
              'CHILDREN': [
                  # {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 1},
                  {'pos': ['FLEX', 'AUX'], '#': 1},
                  {'lemma': 'donde', 'pos': 'PRON', '#': 0, 'fRENAME': 'EN'}
              ]}
         ]
         },

        # ******************************************************************
        # POSESIVOS
        #
        #
        # """
        # "Mi casa es grande."
        #  grande < casa >   	patrón[adj COP]
        #  DE < casa mi >   	patrón[det-posesivo]
        #
        # "Esa casa es mía."
        #  DE < casa mía >   	patrón[N N COP/N posesivo COP]
        #
        # "La mía es grande."
        #  grande < él/ella >   	patrón[adj COP]
        #
        # "La mía es chalet."
        #  chalet < él/ella >   	patrón[N N COP/N N COP]
        #
        # ES UN PROBLEMA PARA EL ADJETIVO, ya que tiene que hallar La
        #    ┌─►   La     det      el     DET
        # ┌─►└──   mía    nsubj    mía    DET
        # │  ┌─►   es     cop      ser    AUX
        # └──┼──   grande ROOT     grande ADJ
        #    └─►   .      punct    .      PUNCT
        # """
        {'NAME': 'det-posesivo', 'fPOSTPROC': morphology.reorganiza_det_pos, 'SAMPLES': [
            '✅Mis ojos',
            '✅Mi casa',
            '✅Mi casa es grande',
        ],
         'pos': ['NOUN', 'PROPN'], '#': 2,
         'CHILDREN': [
             {'pos': 'DET', 'lemma': morphology.lemas_posesivos, '#': 1}
         ]
         },

        {'NAME': 'AUX posesivo', 'SAMPLES': [
            'Esa casa es mía',
        ],
         'fPOSTPROC': morphology.reorganiza_det_pos,  # esta casa es mía
         'pos': 'PRON', 'lemma': morphology.lemas_posesivos, '#': 1,
         'CHILDREN': [
             {'pos': 'AUX', 'lemma': 'ser'},
             {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 2},
         ]
         },

        # {'NAME': 'pron-posesivo', 'fPOSTPROC': morphology.reorganiza_det_pos,
        #     'lemma': morphology.lemas_posesivos, '#': 2,
        #     'CHILDREN': [
        #         {'pos': 'DET', '#': 1}
        #     ]
        # },
        # la mía está delante de ti     DE<la yo> delante<la tu>
        # {'NAME': 'pron-posesivo COP', 'fPOSTPROC': morphology.reorganiza_det_pos, '#': 2, # la mía es chalet
        #     'CHILDREN': [
        #         {'dep': 'cop', 'pos': 'AUX'},  # estar o ser
        #         {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 2,
        #             'CHILDREN': [
        #                 {'pos': 'AUX', '#': 1},
        #             ],
        #         },
        #     ],
        #  },

        # N N
        # aposición ¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡ <<<<<<<<<<<<<<<<<<<<<<

        # ******************************************************************
        # ORACIÓN CON NÚCLEO SEMÁNTICO NO VERBAL
        #
        #
        {'NAME': 'N COP SN', 'SAMPLES': [
            'Itsaso es mi hija',
            'La ingeniera es Itsaso',
            '✅La hija es ingeniera',
        ],
         'pos': NP_head,
         'CHILDREN': [
             {'pos': 'AUX', 'lemma': 'ser'},
         ],
         '¬CHILDREN': [{'dep': 'case'}],  # sin caso
         'ALTERNATIVES': [
             # {'NAME': 'Posesivo', 'fPOSTPROC': morphology.reorganiza_det_pos,  # esta casa es mía
             #  'pos': 'PRON', 'lemma': morphology.lemas_posesivos, '#': 1,
             #  'CHILDREN': [
             #      {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 2},
             #  ]
             #  },
             {'NAME': 'Nombre propio',  # La ingeniera es Itsaso
              'pos': 'PROPN', '#': 1,
              'CHILDREN': [
                  {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': ['NOUN', 'PRON'], '#': 0},
              ]
              },
             {'NAME': 'Nombre propio sujeto',  # Itsaso es mi hija
              'pos': ['NOUN', 'PRON'], '#': 0,
              'CHILDREN': [
                  {'dep': 'nsubj', 'pos': 'PROPN', '#': 1},
              ]
              },
             {'NAME': 'N',  # La hija es ingeniera
              'pos': NP_head, '#': 0,
              'CHILDREN': [
                  {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': ['NOUN', 'PRON'], '#': 1},
                  # {'dep': 'nsubj', 'pos': NP_head, '#': 1
                  # 'CHILDREN': [
                  #     {'pos': 'DET', '#': 1},
                  # ]},
                  # },
              ]
              }
         ],
         },
        # ******************************************************************
        # N+PP: posesión y otros
        #
        #
        # atención a nmod y acl. Los 2 patrones '...COP' resuelven también suboraciones adjetivas
        # caso especial (por eso tiene preferencia en la lista) para desambiguar el valor de 'de'
        {'NAME': 'NOUN PP+N', 'SAMPLES': [
            '✅El libro del profesor',
            '✅El supermercado de la esquina',
            '✅La caja de latón',  # subsectivo
            '✅La caja de madera',
            '✅La caja de mi abuela',
            '✅La casita del pueblo',
            '✅La rueda de la bicicleta',  # la meronimia no está en el wordnet español

            '✅La caja de Nicolasa Gómez',
            '✅Mi tía de Toledo está disfrutando del tiempo allí',
            'La catedral de Burgos fue diseñada por un francés',

            '✅El libro de Pepe',
            '✅El puente sobre el río ardió.',  # NOUN->NOUN
        ],
         'pos': 'NOUN',
         'ALTERNATIVES': [
             # nombres deverbales o ción|mi?ento|aj[eo]|encia|ura|zón|dora?|der[ao]
             # https://literaturaespanolasigloxxi.wordpress.com/2020/06/20/sustantivos-deverbales-en-espanol/
             {'NAME': 'nombre_deverbal+args',
              'text': re.compile(r'(?:ción|mi?ento|aj[eo]|encia|ura|zón|dora?|der[ao])$'), '#': 0,
              'CHILDREN': [  # using regular expression
                  {'dep': 'nmod', 'pos': NP_head, '#': 1, 'CHILDREN': [
                      # 'dep': 'nmod' es importante puesto que una oración puede verificarse doblemente como NdeN y NCOPdeN; como esta "El libro que es de Pepe ."
                      {'dep': 'case', 'lemma': ['de', 'del', 'por', 'a', 'al', 'con', 'sin']}
                  ]}
              ],
              'OPTIONAL_CHILDREN': [
                  {'dep': 'nmod', 'pos': NP_head, '#': 2, 'CHILDREN': [
                      # 'dep': 'nmod' es importante puesto que una oración puede verificarse doblemente como NdeN y NCOPdeN; como esta "El libro que es de Pepe ."
                      {'dep': 'case', 'lemma': ['a', 'al']}
                  ]}
              ],
              },
             {'NAME': 'de', '#': 1, 'fPOSTPROC': semantics.precisa_de, 'CHILDREN': [
                 {'dep': 'nmod', 'pos': NP_head, '#': 2, 'CHILDREN': [
                     # 'dep': 'nmod' es importante puesto que una oración puede verificarse doblemente como NdeN y NCOPdeN; como esta "El libro que es de Pepe ."
                     {'dep': 'case', 'lemma': ['de', 'del', 'con', 'sin'], '#': 0}  # familia con dos hijos
                 ]}
             ]},
             {'NAME': 'sin de', '#': 1, 'CHILDREN': [
                 {'dep': 'nmod', 'pos': NP_head, '#': 2, 'CHILDREN': [
                     # 'dep': 'nmod' es importante puesto que una oración puede verificarse doblemente como NdeN y NCOPdeN; como esta "El libro que es de Pepe ."
                     {'dep': 'case', '#': 0}
                 ]}
             ]},

         ]
         },

        {'NAME': 'NOUN COP PP+N', 'SAMPLES': [
            "✅El libro es de Pepe.",
            "La comida es sin sal.",
            "✅El regalo es para ti.",
        ],
         '#': 2, 'pos': NP_head,
         'CHILDREN': [
             {'pos': 'AUX', 'lemma': 'ser'},
             {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 1},
             {'dep': 'case', '#': 0,
              'ALTERNATIVES': [
                  {'NAME': 'N COP de N', 'fPOSTPROC': semantics.precisa_de,
                   'lemma': ['de', 'del', 'con', 'sin']
                   },
                  {'NAME': 'N COP PP+N '},  # el complementario
              ],
              },
         ],
         },

        {'NAME': 'TENER←cuyo', 'SAMPLES': [
            '✅La vecina cuya casa ardió',  # vecina ardió casa cuya
            '✅La ciudad cuyo ayuntamiento es enorme',  # ciudad enorme ayuntamiento cuyo
        ],
         'pos': NP_head, '#': 1, 'CHILDREN': [
            {'CHILDREN': [
                # CHILDREN no especificado: nos es indiferente si es un verbo o un adjetivo el núcleo de la suboración
                {'pos': NP_head, '#': 2, 'CHILDREN': [
                    {'lemma': 'cuyo', '#': 0, 'fRENAME': 'TENER←cuyo'}
                ]}
            ]},
        ],
         },

        # ******************************************************************
        # ADJETIVOS                             PARTICIPIOS o no PARTICIPIOS
        #
        #
        # aunque 'la silla comprada' y 'la silla fue comprada' tengan un parecido evidente, en tanto que el participio simplifica una suboración
        # no obstante, son analizadas como dos categorías diferentes: adj y verbo respectivamente
        # aquí se ocupa del adj
        #
        {'NAME': 'adj', 'SAMPLES': [
            "✅La casa adecuada para vivir.",

            '✅La casa grande',  # ADJ MOD
            "✅La casa arruinada por el fuego.",
        ],
         'pos': 'NOUN',
         'ALTERNATIVES': [
             {'NAME': 'por', '#': 2,
              'CHILDREN': [
                  {'dep': 'amod', '#': 0, 'CHILDREN': [
                      {'pos': NP_head, '#': 1, 'CHILDREN': [  # complemento agente
                          {'dep': 'case', 'lemma': 'por'}
                      ]}
                  ]}
              ]
              },
             # adjetivo o adjetivo participial
             {'NAME': 'sin por', '#': 1,
              'CHILDREN': [
                  {'dep': 'amod', '#': 0,
                   'OPTIONAL_CHILDREN': [
                       {'#': 2, 'CHILDREN': [  # cualquier token, en principio verbo o nombre
                           {'lemma': ['para', 'según'], 'pos': 'ADP'}
                       ]}
                   ]
                   }
              ],
              },
         ]
         },

        {'NAME': 'adj COP', 'SAMPLES': [
            '✅La casa está nueva',
            '✅Está nueva',
            # 'Es muy grande',  # error de SPACY  ┌──►     Es     advmod   es     ADV
            '✅La casa es grande',

            '✅La casa es grande para él',  # cópula ADJ < 1 2 >  ¿ELIMINAMOS ADVERBIO?
            # 'La casa es adecuada para vivir.',  # SPACY juzga que es una pasiva de ADECUAR

        ],
         'pos': 'ADJ', '#': 0,
         '¬CHILDREN': [{'dep': 'nsubj', 'lemma': morphology.lemas_posesivos}],  # la mía es grande <<<<<<<<<<<
         'CHILDREN': [
             {'dep': 'cop', 'pos': 'AUX'},  # estar o ser
             {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 1},
         ],
         'OPTIONAL_CHILDREN': [
             {'#': 2, 'CHILDREN': [
                 {'lemma': ['para', 'según'], 'pos': 'ADP'}
             ]}
         ]
         },

        # ******************************************************************
        # HABER
        #
        #
        # ESPACIO-TIEMPO en adverbios de localización o el complemento de lugar 'en'
        # el tiempo muchas veces se expresa sin 'en' "Hablamos la próxima semana" pero "Nos vimos en febrero"
        #
        #
        # ESTAR con atributo de lugar
        #    es ROOT, a diferencia de SER que siempre es AUX y depende del atributo
        # {'NAME': 'estar+PP',  # "La bicicleta está en la pared ."
        #     'lemma': 'estar',
        #     'CHILDREN': [
        #         {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#':1},
        #         {'dep': 'obl', '#':2, 'CHILDREN': [
        #             {'dep': 'case', '#':0}
        #         ]}
        #     ],
        # },
        # {'NAME': 'estar+ADVPP',  # "Saturno estaba delante de mis ojos ."
        #     'lemma': 'estar',
        #     'CHILDREN': [
        #         {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#':1},
        #         {'dep': 'advmod', '#':0, 'CHILDREN': [
        #             {'dep': 'obl', '#':2}
        #         ]}
        #     ],
        # },
        # HABER es un caso particular:
        # es impersonal, siempre está en singular.
        # variante HAY en presente
        # Siempre rige un objeto por su falta de concordancia, da igual que sea otro tiempo "había"
        # haber no necesita complemento circunstancial, esto se observa bien en obras de ficción: 'había un planeta en el que...'
        {'NAME': 'haber+en', 'SAMPLES': [
            "En la colina hay una casa de piedra.",
        ],
         'lemma': ['haber', 'existir'],
         'CHILDREN': [
             {'dep': 'obj', 'pos': NP_head, '#': 1},
             {'dep': 'obl', 'pos': NP_head, '#': 2, 'CHILDREN': [
                 # 'dep': 'nmod' es importante puesto que una oración puede verificarse doblemente como NdeN y NCOPdeN; como esta "El libro que es de Pepe ."
                 {'dep': 'case', 'lemma': 'en', '#': 0, 'fRENAME': 'EN'}
             ]}
         ],
         },

        {'NAME': 'haber+ADVPP', 'SAMPLES': [
        ],
         'lemma': 'haber',  # ""Próxima a ella hay otra casa más antigua."
         'CHILDREN': [
             {'dep': 'obj', 'pos': NP_head, '#': 1},
             {'dep': 'advmod', '#': 0, 'CHILDREN': [
                 {'pos': NP_head, '#': 2}
             ]}
         ],
         },

        # {'NAME': 'EXISTIR', 'SAMPLES': [
        # ],
        #  'lemma': ['haber', 'existir'], '#': 0, 'fRENAME': 'EXISTIR',  # "Próxima a ella hay otra casa más antigua."
        #  'CHILDREN': [
        #      {'dep': 'obj', 'pos': NP_head, '#': 1},
        #  ],
        #  },


        # ******************************************************************
        # SUBORACIONES SUSTANTIVAS
        #
        #
        {'NAME': 'Oración', 'SAMPLES': [
            'Le dijimos que no iríamos',
            'Siempre había imaginado que volverías',  # no obtiene el lema de volverías
            '✅Quiero que compres una casa',
            'Quiero comprar una casa',
            'Pero volvió a perder.',
        ],
         'pos': 'VERB', '#': 0,
         'CHILDREN': [
             {'pos': 'VERB', 'dep': ['ccomp', 'xcomp'], '#': 1},
         ],
         },


        # ******************************************************************
        # ORACIONES
        #
        #
        # ORDEN: esta entrada debe ser la última
        # sujeto objeto OI
        # Debe estar antes que 'Oración', pues la pasiva es un caso particular que reordena los complementos
        # el núcleo es el verbo con contenido léxico, y el auxiliar (portador del sintagma flexivo) depende de él
        {'NAME': 'Oración', 'SAMPLES': [
            '✅Entonces nuestras manos se buscaban',  # ambigüedad con SE: aquí es un reflexivo, no otro pronombre de 3ª
            '✅Ganó el premio',  # O' cópula ADJ
        ],
         'pos': 'VERB', '#': 0,
         'ALTERNATIVES': [
             {'NAME': 'pasiva SER',  # "El libro fue regalado a Juan por Marta ."
              'CHILDREN': [
                  {'pos': 'AUX', 'lemma': 'ser'},
                  {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 1},
              ],
              'OPTIONAL_CHILDREN': [
                  {'#': 2, 'CHILDREN': [
                      {'dep': 'case', 'lemma': 'por'}  # complemento agente
                  ]},
                  {'dep': 'obj', '#': 3, 'CHILDREN': [  # iobj -> obj
                      {'dep': 'case', 'lemma': 'a'}
                  ]}
              ]
              },
             {'NAME': 'activa',  #
              'CHILDREN': [
                  {'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': NP_head, '#': 1},
              ],
              'OPTIONAL_CHILDREN': [  # relative 'dep': 'acl',
                  # alternatives
                  {'dep': ['ccomp', 'xcomp'], '#': 2},
                  # mark:que ccomp:volverías / xcomp:volver. "Me dicen que el libro es de esa [ccomp:]mujer ."
                  {'dep': 'obj', 'pos': NP_head, '#': 2},
                  {'dep': 'iobj', 'pos': NP_head, '#': 3}
              ],
              }
         ]
         },

    ]  # 'es'
}

"""  ************************************************************************************
        ▄                                          
       ▄██▄   ▄▄▄▄   ▄▄▄ ▄▄    ▄▄▄▄   ▄▄▄▄    ▄▄▄▄  
        ██   ▀▀ ▄██   ██▀ ▀▀ ▄█▄▄▄██ ▀▀ ▄██  ██▄ ▀  
        ██   ▄█▀ ██   ██     ██      ▄█▀ ██  ▄ ▀█▄▄ 
        ▀█▄▀ ▀█▄▄▀█▀ ▄██▄     ▀█▄▄▄▀ ▀█▄▄▀█▀ █▀▄▄█▀ 

NO recursión de patrones call economizar
'MERGE': True
como nombres propios. {1} y fixed {1}


************************************************************************************ """

""" 

DISTINGUIR CD DEL CI. ambos pueden tener marca 'a'
, 'OPTIONAL_CHILDREN': {'dep': 'obj', 'pos': NP_head, '#':2, 'HASNOT': [
{'dep': 'case'}  # cd sin caso  <<<<<<<<<<<<<<<<<<<<<
]},


ví a la gata
    *dí a la gata a Pepe
recomendé a Juan a Basilio

¿cuáles son los ARGUMENTOS DEL VERBO?
atender a CASE O SIN CASE, obj y obl

∅ a     2xobj obj obj/case
 ││└─►└── libro     obj      libro      NOUN      
 ││   ┌─► a         case     a          ADP       
 │└──►└── Marta     obj      Marta      PROPN     
de a     2xobj/case
 │││  ┌─► del       case     del        ADP       
 ││└─►└── libro     obj      libro      NOUN      
 ││   ┌─► a         case     a          ADP       
 │└──►└── Marta     obj      Marta      PROPN     
en     obl/case
 ┌┬──┴┴── habló     ROOT     hablar     VERB      
 ││  ┌──► en        case     en         ADP       
 ││  │┌─► la        det      el         DET       
 │└─►└┴── cocina    obl      cocina     NOUN      
∅ en     obj obl/case
  ┌┬───── Introduje ROOT     introducir VERB      
  ││  ┌─► los       det      el         DET       
  │└─►└── garbanzos obj      garbanzo   NOUN      
  │  ┌──► en        case     en         ADP       
  │  │┌─► el        det      el         DET       
  └─►└┴── tarro     obl      tarro      NOUN 

hay un 'nsubj' pero existen dos obj
"Juan no regaló el libro a Marta ."
"Juan no habló del libro a Marta"



"""

""" FORMATO de los patrones

CONCEPTOS
    PROPIEDAD de un token, es un par atributo valor, los atributos pueden ser de los siguientes tipos:
        'text' 'dep' 'lemma' 'pos'  
    {} CONDICIÓN es un diccionario de propiedades que debe verificar ese token
        por ejemplo el lema de la cópula 'ser' puede especificarse máximamente así:
            {'dep': 'cop', 'pos': 'AUX', 'lemma': 'ser'}
    {} POSIBILIDAD es una extensión de una condición, una de varias sobre la que se itera, se nombra con 'NAME' para trazar el análisis
        y puede poseer CHILDREN y/o ALTERNATIVES que permiten corresponder estructuras complejas
        {name: '', ..., 'CHILDREN': [] }
    [] CHILDREN y ALTERNATIVES 
        Desde el punto de vista lógico se asemeja la acción de CHILDREN al operador lógico '∧' y ALTERNATIVES a '∨'
        CHILDREN[0] ∧ CHILDREN[1] ∧ CHILDREN[2] ∧ (OPTIONAL[3] ⊤ ... ⊤ OPTIONAL[N])
        CHILDREN
            es una lista de condiciones necesarias que deben verificar algunos hijos del token
                'CHILDREN': [ { condición1}, ..., { condiciónN } ]
        ALTERNATIVES
            es una lista de posibilidades
            cada lista es una alternativa y posee un nombre para registrar el itinerario 
                'ALTERNATIVES': [ 
                    {'NAME': '1', PROPIEDADES DEL ELEMENTO ACTUAL
                        'CHILDREN': [ { condición1}, ..., { condiciónN } ]
                    }
                    ...
                    {'NAME': '2', PROPIEDADES DEL ELEMENTO ACTUAL
                        'CHILDREN': [ { condición1}, ..., { condiciónN } ]
                    }
                ]
            ALTERNATIVES es una evaluación mínima de ∨
                ALTERNATIVES es una evaluación mínima ( también llamada evaluación de circuito corto o evaluación McCarthy)
                basada en el operador lógico ∨
                son estructuras de control en vez de simples operadores aritméticos,
                se toma el primer elemento que verifica la condición
    [] OPTIONAL_CHILDREN Los opcionales no afectan al valor de verdad, pero alteran la visualización de los complementos
        #:X promueve a argumento
            failed_function: function_name    que sirve para ejecutar una función en caso de que no se halle. 
                None
                non None <- token                
            Esa función puede forzar un valor para este complemento evaluando el contexto
        #:None REMOVE    elimina de los complementos
        si no existe la clave # se mantiene en complementos


NUMERACIÓN
    0 functor
    >0 argumentos
    <0 adyacentes

el patrón nos muestra un 'CHILDREN' cuya condición es
    {'pos': 'ADJ'}
y se halla un token con el que hay correspondencia
    este a su vez requiere un hijo que verifique esta condición es
        {'dep': 'cop', 'lemma': 'ser'}
    y se halla un token hijo de aquél con el que hay correspondencia

OPTIONAL
    puede ser True o una función que será ejecutada en caso de que no se verifique
FUNCIONES
    imagina que te es cómodo incluir todos los adv
        INCLUDE: [ {'pos': 'ADV'} ]
        pero hay unos pocos de esos que quieres excluir
        EXCLUDE: [ {'pos': 'ADV', 'lemma': 'no'} ]
    attributos negativos
        {'¬dep': 'case'} ABSURDO
        {'dep': '¬case'}                

    EXPAND
        ┌┬┬─┴┴── regaló    ROOT     regalar    VERB      
        │││  ┌─► el        det      el         DET       
        ││└─►└── libro     obj      libro      NOUN      
        ││   ┌─► a         case     a          ADP       
        │└──►└── Marta     obj      Marta      PROPN     
        └──────► .         punct    .          PUNCT   
"""


def create_dictionary(token):
    if token.pos_ == 'PUNCT':
        return None
    properties = {
        'text': token.text.lower(),
        'lemma': token.lemma_,
        'dep': token.dep_,
        'pos': token.pos_,
    }
    properties = {
        'text': token.text.lower(),
        'dep': token.dep_,
        'pos': token.pos_,
    }
    children_properties = [create_dictionary(child) for child in token.children]
    children_properties = [item for item in children_properties if item is not None]  # remove None
    if children_properties:
        properties['CHILDREN'] = children_properties
    return properties


def dict_to_latex_avm(obj):
    def recursive(obj, level):
        indent = '\t' * level
        output2 = ''
        if isinstance(obj, dict):
            if '#' in obj:
                output2 += f"\n{indent}\\{obj['#']} \{{\n"
                del obj['#']
            else:
                output2 += f'\n{indent}\{{\n'
            # Iterate over all key-value pairs of dictionary by index

            for index, (key, value) in enumerate(obj.items()):
                # for key, value in obj.items():
                tt = '' if index == 0 else '\\\\ '
                new_key = key.replace('_', '-')
                output2 += f'{indent}{tt}{new_key} & '
                output2 += recursive(value, level + 1)
            output2 += f'\n{indent}\}}\n'
        elif isinstance(obj, list):
            output2 += f'\n{indent}[\n'
            for index, value in enumerate(obj):
                tt = '' if index == 0 else '\\\\ '
                output2 += indent + tt
                # output2 += f'{indent}{tt}{key} & ', end='')
                output2 += recursive(value, level + 1)
            output2 += f'\n{indent}]\n'

        elif callable(obj):
            output2 += obj.__name__.replace('_', '-')
        elif isinstance(obj, str):
            output2 += obj.replace('_', '')
        elif isinstance(obj, int):
            output2 += str(obj)
        else:  # atomic
            output2 += obj
        return output2 + '\n'

    return f"""
\\vspace*{{10px}}
\\avm{{
{recursive(obj, 1)}}}"""


def dict_to_latex_avm_min(obj):
    result = dict_to_latex_avm(obj)
    return re.sub(r'\s{2,}', ' ', result)


# Para ejecutar desde el exterior
if __name__ == "__main__":
    print('__main__')

    item = patterns['es'][0]
    result = dict_to_latex_avm_min(item)
    print(result)
