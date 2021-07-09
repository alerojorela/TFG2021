# -*- coding: utf-8 -*-
# by Alejandro Rojo Gualix 2021-06
import json
import re

# MÍOS
import utils.functions as functions
import predicates.graphs as graphs

filename = 'predicates/verbs_es.json'
with open(filename, 'r') as f:
    verbs_es = json.load(f)


""" Los argumentos de un predicado son expresiones referenciales formalizadas como sintagmas determinantes.
El núcleo de este sintagma puede ser:
    un nombre propio
    un determinante:
        con o sin complemento SN
            determinantes con complemento SN
            determinantes sin complemento SN (los tradicionales pronombres)

Haremos dos clasificaciones:
    Si establecen una referencia nueva o previa
        definidos: si se refieren a una referencia previa o antecedente (en ocasiones crean una nueva referencia)
        indefinidos: si crean una nueva referencia


PREPROCESAMIENTO
    los posesivos se convierten en predicados
¡LEMATIZACIÓN¡
    lemma elimina la flexión nominal (núm y gen)
    ultralemma elimina también la flexión sintáctica (nom acus dat gen) si procede
"""
sintagma_determinante = { 'pos': ['DET', 'PRON', 'PROPN'] }
determinante_sin_complemento = { 'pos': 'PRON' }
determinante_con_complemento = { 'pos': 'DET' }

# conjuntos disjuntos
sin_referencia = ['ninguno', 'nadie', 'nada']
# CREA una nueva referencia
indefinido = {'lemma': [
    'uno', 'alguno',
    'poco', 'escaso', 'mucho', 'demasiado', 'varios', 'tanto',
    'mismo', 'otro', 'todo', 'alguien', 'cualquier', 'quienquiera', 'demás',
]}
# indefinido = {'lemma': ['uno', 'algún', 'alguno', 'ningún', 'ninguno',
#     'poco', 'escaso', 'mucho', 'demasiado', 'todo', 'varios', 'otro', 'mismo', 'tanto', 'alguien', 'nadie', 'cualquier', 'quienquiera', 'demás']
# }
# CORREFERENCIA con un antecedente (en ciertos casos crea una referencia)
definido = {'lemma': [
    'mi', 'tu', 'nuestro', 'vuestro', 'mío', 'tuyo', 'su', 'suyo',  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    'yo', 'tu', 'nosotros', 'vosotros', 'me', 'te', 'nos', 'os', 'mí', 'ti', 'sí',
    'cuyo', 'cual', 'quien', 'cuanto', 'donde', 'que',
    'el', 'él', 'lo', 'le', 'se',
    # 'este', 'ese', 'aquel', 'tal',
    'esto', 'eso', 'aquello', 'tal',
]}


determinante = {'lemma': definido['lemma'] + indefinido['lemma']}


# no hay que usar DICT_KEY, usa list( .keys() )
# obsérvese la tendencia de añadir un sufijo -(y)o a las formas sin complemento
lemas_posesivos = ['mi', 'tu', 'nuestro', 'vuestro', 'mío', 'tuyo', 'su', 'suyo']
# el género del poseedor se pierde. El género del posesivo no es el del poseedor, sino de el de lo poseído
# la nuestra -> DE<la nosotr@s>
# nuestra casa -> DE<una nosotr@s> ^ CASA<una>
posesivos_datos = {
    'mi': {'lemma': 'mi', 'possesor': 'yo', 'label': 'yo', 'num': 'sing', 'possessed': '3S'},
    'mis': {'lemma': 'mi', 'possesor': 'yo', 'label': 'yo', 'num': 'pl', 'possessed': '3P'},
    'tu': {'lemma': 'tu', 'possesor': 'tu', 'label': 'tu', 'num': 'sing', 'possessed': '3S'},
    'tus': {'lemma': 'tu', 'possesor': 'tu', 'label': 'tu', 'num': 'pl', 'possessed': '3P'},
    'nuestro': {'lemma': 'nuestro', 'possesor': 'nosotros', 'label': 'nosotr@s', 'gen': 'masc', 'num': 'sing',
                'possessed': 'el'},
    'nuestra': {'lemma': 'nuestro', 'possesor': 'nosotros', 'label': 'nosotr@s', 'gen': 'fem', 'num': 'sing',
                'possessed': 'la'},
    'nuestros': {'lemma': 'nuestro', 'possesor': 'nosotros', 'label': 'nosotr@s', 'gen': 'masc', 'num': 'pl',
                 'possessed': 'los'},
    'nuestras': {'lemma': 'nuestro', 'possesor': 'nosotros', 'label': 'nosotr@s', 'gen': 'fem', 'num': 'pl',
                 'possessed': 'las'},
    'vuestro': {'lemma': 'vuestro', 'possesor': 'vosotros', 'label': 'vosotr@s', 'gen': 'masc', 'num': 'sing',
                'possessed': 'el'},
    'vuestra': {'lemma': 'vuestro', 'possesor': 'vosotros', 'label': 'vosotr@s', 'gen': 'fem', 'num': 'sing',
                'possessed': 'la'},
    'vuestros': {'lemma': 'vuestro', 'possesor': 'vosotros', 'label': 'vosotr@s', 'gen': 'masc', 'num': 'pl',
                 'possessed': 'los'},
    'vuestras': {'lemma': 'vuestro', 'possesor': 'vosotros', 'label': 'vosotr@s', 'gen': 'fem', 'num': 'pl',
                 'possessed': 'las'},

    'mío': {'lemma': 'mío', 'possesor': 'yo', 'label': 'yo', 'gen': 'masc', 'num': 'sing', 'possessed': 'el'},
    'mía': {'lemma': 'mío', 'possesor': 'yo', 'label': 'yo', 'gen': 'fem', 'num': 'sing', 'possessed': 'la'},
    'míos': {'lemma': 'mío', 'possesor': 'yo', 'label': 'yo', 'gen': 'masc', 'num': 'pl', 'possessed': 'los'},
    'mías': {'lemma': 'mío', 'possesor': 'yo', 'label': 'yo', 'gen': 'fem', 'num': 'pl', 'possessed': 'las'},
    'tuyo': {'lemma': 'tuyo', 'possesor': 'tu', 'label': 'tu', 'gen': 'masc', 'num': 'sing', 'possessed': 'el'},
    'tuya': {'lemma': 'tuyo', 'possesor': 'tu', 'label': 'tu', 'gen': 'fem', 'num': 'sing', 'possessed': 'la'},
    'tuyos': {'lemma': 'tuyo', 'possesor': 'tu', 'label': 'tu', 'gen': 'masc', 'num': 'pl', 'possessed': 'los'},
    'tuyas': {'lemma': 'tuyo', 'possesor': 'tu', 'label': 'tu', 'gen': 'fem', 'num': 'pl', 'possessed': 'las'},
    # 'nuestro': {'lemma': 'nuestro', 'possesor': 'nosotros', 'label': 'nosotr@s', 'gen': 'masc', 'num': 'sing',
    #             'possessed': 'el'},
    # 'nuestra': {'lemma': 'nuestro', 'possesor': 'nosotros', 'label': 'nosotr@s', 'gen': 'fem', 'num': 'sing',
    #             'possessed': 'la'},
    # 'nuestros': {'lemma': 'nuestro', 'possesor': 'nosotros', 'label': 'nosotr@s', 'gen': 'masc', 'num': 'pl',
    #              'possessed': 'los'},
    # 'nuestras': {'lemma': 'nuestro', 'possesor': 'nosotros', 'label': 'nosotr@s', 'gen': 'fem', 'num': 'pl',
    #              'possessed': 'las'},
    # 'vuestro': {'lemma': 'vuestro', 'possesor': 'vosotros', 'label': 'vosotr@s', 'gen': 'masc', 'num': 'sing',
    #             'possessed': 'el'},
    # 'vuestra': {'lemma': 'vuestro', 'possesor': 'vosotros', 'label': 'vosotr@s', 'gen': 'fem', 'num': 'sing',
    #             'possessed': 'la'},
    # 'vuestros': {'lemma': 'vuestro', 'possesor': 'vosotros', 'label': 'vosotr@s', 'gen': 'masc', 'num': 'pl',
    #              'possessed': 'los'},
    # 'vuestras': {'lemma': 'vuestro', 'possesor': 'vosotros', 'label': 'vosotr@s', 'gen': 'fem', 'num': 'pl',
    #              'possessed': 'las'},

    'su': {'lemma': 'su', 'possesor': 'él', 'label': 'él/ella/ell@s', 'num': 'sing', 'possessed': '3S'},
    'sus': {'lemma': 'su', 'possesor': 'él', 'label': 'él/ella/ell@s', 'num': 'pl', 'possessed': '3P'},
    'suyo': {'lemma': 'suyo', 'possesor': 'él', 'label': 'él/ella/ell@s', 'gen': 'masc', 'num': 'sing',
             'possessed': 'el'},
    'suya': {'lemma': 'suyo', 'possesor': 'él', 'label': 'él/ella/ell@s', 'gen': 'fem', 'num': 'sing',
             'possessed': 'la'},
    'suyos': {'lemma': 'suyo', 'possesor': 'él', 'label': 'él/ella/ell@s', 'gen': 'masc', 'num': 'pl',
              'possessed': 'los'},
    'suyas': {'lemma': 'suyo', 'possesor': 'él', 'label': 'él/ella/ell@s', 'gen': 'fem', 'num': 'pl',
              'possessed': 'las'},

}


lemas_personales = ['yo', 'tu', 'nosotros', 'vosotros', 'me', 'te', 'nos', 'os', 'mí', 'ti', 'sí']
# personales exceptuando los no deícticos (los tradicionalmente denominados de 3ª persona)
personales_datos = {
    'yo': {'lemma': 'yo', 'label': 'yo'},
    'tu': {'lemma': 'tu', 'label': 'tu'},
    'usted': {'lemma': 'tu', 'label': 'usted'},  # no se va a considerar usted como diferente de la segunda persona
    'nosotros': {'lemma': 'nosotros', 'gen': 'masc', 'label': 'nosotros'},
    'nosotras': {'lemma': 'nosotros', 'gen': 'fem', 'label': 'nosotras'},
    'vosotros': {'lemma': 'vosotros', 'gen': 'masc', 'label': 'vosotros'},
    'vosotras': {'lemma': 'vosotros', 'gen': 'fem', 'label': 'vosotras'},
    'ustedes': {'lemma': 'vosotros', 'label': 'vosotras'},  # no se va a considerar usted como diferente de la segunda persona

    'me': {'lemma': 'me', 'ultralemma': 'yo', 'label': 'yo'},
    'te': {'lemma': 'te', 'ultralemma': 'tu', 'label': 'tu'},
    'nos': {'lemma': 'nos', 'ultralemma': 'nosotros', 'label': 'nosotr@s'},
    'os': {'lemma': 'os', 'ultralemma': 'vosotros', 'label': 'vosotr@s'},

    'mí': {'lemma': 'mí', 'ultralemma': 'yo', 'label': 'yo'},
    'ti': {'lemma': 'ti', 'ultralemma': 'tu', 'label': 'tu'},
    'sí': {'lemma': 'sí', 'ultralemma': 'él', 'label': 'él/ella/ell@s'},

}


lemas_relativos = ['cuyo', 'cual', 'quien', 'cuanto', 'donde', 'que']


# divido en 3?????????????????????????????????????
# excepto personales (1y2 personas) (y posesivos)

determinantes_datos = {
    '3': {},
    '3S': {'num': 'sing'},
    '3P': {'num': 'pl'},

    # DEFINIDOS
    'él': {'lemma': 'él', 'ultralemma': 'él', 'gen': 'masc', 'num': 'sing'},
    'ella': {'lemma': 'él', 'ultralemma': 'él', 'gen': 'fem', 'num': 'sing'},
    'ellos': {'lemma': 'él', 'ultralemma': 'él', 'gen': 'masc', 'num': 'pl'},
    'ellas': {'lemma': 'él', 'ultralemma': 'él', 'gen': 'fem', 'num': 'pl'},
    'lo': {'lemma': 'lo', 'ultralemma': 'él', 'gen': 'masc', 'num': 'sing'},
    'la': {'lemma': 'lo', 'ultralemma': 'él', 'gen': 'fem', 'num': 'sing'},
    'los': {'lemma': 'lo', 'ultralemma': 'él', 'gen': 'masc', 'num': 'pl'},
    'las': {'lemma': 'lo', 'ultralemma': 'él', 'gen': 'fem', 'num': 'pl'},
    'le': {'lemma': 'le', 'ultralemma': 'él', 'num': 'sing'},
    'les': {'lemma': 'le', 'ultralemma': 'él', 'num': 'sing'},
    'se': {'lemma': 'se', 'ultralemma': 'él'},
    'el': {'lemma': 'el', 'ultralemma': 'él', 'gen': 'masc', 'num': 'sing'},
    # 'la': {'lemma': 'el', 'ultralemma': 'él', 'gen': 'fem', 'num': 'sing'},
    # 'los': {'lemma': 'el', 'ultralemma': 'él', 'gen': 'masc', 'num': 'pl'},
    # 'las': {'lemma': 'el', 'ultralemma': 'él', 'gen': 'fem', 'num': 'pl'},
    'este': {'lemma': 'esto', 'gen': 'masc', 'num': 'sing'},
    'esta': {'lemma': 'esto', 'gen': 'fem', 'num': 'sing'},
    'estos': {'lemma': 'esto', 'gen': 'masc', 'num': 'pl'},
    'estas': {'lemma': 'esto', 'gen': 'fem', 'num': 'pl'},
    'esto': {'lemma': 'esto', 'num': 'sing'},
    'ese': {'lemma': 'eso', 'gen': 'masc', 'num': 'sing'},
    'esa': {'lemma': 'eso', 'gen': 'fem', 'num': 'sing'},
    'esos': {'lemma': 'eso', 'gen': 'masc', 'num': 'pl'},
    'esas': {'lemma': 'eso', 'gen': 'fem', 'num': 'pl'},
    'eso': {'lemma': 'eso', 'num': 'sing'},
    'aquel': {'lemma': 'aquello', 'gen': 'masc', 'num': 'sing'},
    'aquella': {'lemma': 'aquello', 'gen': 'fem', 'num': 'sing'},
    'aquellos': {'lemma': 'aquello', 'gen': 'masc', 'num': 'pl'},
    'aquellas': {'lemma': 'aquello', 'gen': 'fem', 'num': 'pl'},
    'aquello': {'lemma': 'aquello', 'num': 'sing'},
    'tal': {'lemma': 'tal', 'num': 'sing'},
    'tales': {'lemma': 'tal', 'num': 'pl'},

    # los relativos son anáforas, pero quizá no deberían ser antecedentes de ninguna otra anáfora
    'cuyo': {'lemma': 'cuyo', 'gen': 'masc', 'num': 'sing'},
    'cuya': {'lemma': 'cuyo', 'gen': 'fem', 'num': 'sing'},
    'cuyos': {'lemma': 'cuyo', 'gen': 'masc', 'num': 'pl'},
    'cuyas': {'lemma': 'cuyo', 'gen': 'fem', 'num': 'pl'},
    'cual': {'lemma': 'cual', 'num': 'sing'},
    'cuales': {'lemma': 'cual', 'num': 'pl'},
    'quien': {'lemma': 'quien', 'num': 'sing'},
    'quienes': {'lemma': 'quien', 'num': 'pl'},
    'cuanto': {'lemma': 'cuanto', 'gen': 'masc', 'num': 'sing'},
    'cuanta': {'lemma': 'cuanto', 'gen': 'fem', 'num': 'sing'},
    'cuantos': {'lemma': 'cuanto', 'gen': 'masc', 'num': 'pl'},
    'cuantas': {'lemma': 'cuanto', 'gen': 'fem', 'num': 'pl'},
    'donde': {'lemma': 'donde'},
    'que': {'lemma': 'que'},


    # INDEFINIDOS
    'uno': {'lemma': 'uno', 'gen': 'masc', 'num': 'sing'},
    'un': {'lemma': 'uno', 'gen': 'masc', 'num': 'sing'},
    'una': {'lemma': 'uno', 'gen': 'fem', 'num': 'sing'},
    'unos': {'lemma': 'uno', 'gen': 'masc', 'num': 'pl'},
    'unas': {'lemma': 'uno', 'gen': 'fem', 'num': 'pl'},
    'alguno': {'lemma': 'alguno', 'gen': 'masc', 'num': 'sing'},
    'algún': {'lemma': 'alguno', 'gen': 'masc', 'num': 'sing'},
    'alguna': {'lemma': 'alguno', 'gen': 'fem', 'num': 'sing'},
    'algunos': {'lemma': 'alguno', 'gen': 'masc', 'num': 'pl'},
    'algunas': {'lemma': 'alguno', 'gen': 'fem', 'num': 'pl'},
    'poco': {'lemma': 'poco', 'gen': 'masc', 'num': 'sing'},
    'poca': {'lemma': 'poco', 'gen': 'fem', 'num': 'sing'},
    'pocos': {'lemma': 'poco', 'gen': 'masc', 'num': 'pl'},
    'pocas': {'lemma': 'poco', 'gen': 'fem', 'num': 'pl'},
    'escaso': {'lemma': 'escaso', 'gen': 'masc', 'num': 'sing'},
    'escasa': {'lemma': 'escaso', 'gen': 'fem', 'num': 'sing'},
    'escasos': {'lemma': 'escaso', 'gen': 'masc', 'num': 'pl'},
    'escasas': {'lemma': 'escaso', 'gen': 'fem', 'num': 'pl'},
    'mucho': {'lemma': 'mucho', 'gen': 'masc', 'num': 'sing'},
    'mucha': {'lemma': 'mucho', 'gen': 'fem', 'num': 'sing'},
    'muchos': {'lemma': 'mucho', 'gen': 'masc', 'num': 'pl'},
    'muchas': {'lemma': 'mucho', 'gen': 'fem', 'num': 'pl'},
    'demasiado': {'lemma': 'demasiado', 'gen': 'masc', 'num': 'sing'},
    'demasiada': {'lemma': 'demasiado', 'gen': 'fem', 'num': 'sing'},
    'demasiados': {'lemma': 'demasiado', 'gen': 'masc', 'num': 'pl'},
    'demasiadas': {'lemma': 'demasiado', 'gen': 'fem', 'num': 'pl'},
    'varios': {'lemma': 'varios', 'gen': 'masc', 'num': 'pl'},
    'varias': {'lemma': 'varios', 'gen': 'fem', 'num': 'pl'},
    'tanto': {'lemma': 'tanto', 'gen': 'masc', 'num': 'sing'},
    'tanta': {'lemma': 'tanto', 'gen': 'fem', 'num': 'sing'},
    'tantos': {'lemma': 'tanto', 'gen': 'masc', 'num': 'pl'},
    'tantas': {'lemma': 'tanto', 'gen': 'fem', 'num': 'pl'},

    # ¿mismo sirve para algo? Coincide con otro det.
    'mismo': {'lemma': 'mismo', 'gen': 'masc', 'num': 'sing'},
    'misma': {'lemma': 'mismo', 'gen': 'fem', 'num': 'sing'},
    'mismos': {'lemma': 'mismo', 'gen': 'masc', 'num': 'pl'},
    'mismas': {'lemma': 'mismo', 'gen': 'fem', 'num': 'pl'},
    'otro': {'lemma': 'otro', 'gen': 'masc', 'num': 'sing'},
    'otra': {'lemma': 'otro', 'gen': 'fem', 'num': 'sing'},
    'otros': {'lemma': 'otro', 'gen': 'masc', 'num': 'pl'},
    'otras': {'lemma': 'otro', 'gen': 'fem', 'num': 'pl'},
    'todo': {'lemma': 'todo', 'gen': 'masc', 'num': 'sing'},
    'toda': {'lemma': 'todo', 'gen': 'fem', 'num': 'sing'},
    'todos': {'lemma': 'todo', 'gen': 'masc', 'num': 'pl'},
    'todas': {'lemma': 'todo', 'gen': 'fem', 'num': 'pl'},

    'alguien': {'lemma': 'alguien'},
    'cualquier': {'lemma': 'cualquier'},
    'quienquiera': {'lemma': 'quienquiera'},
    'demás': {'lemma': 'demás', 'num': 'pl'},

    # no son referencia
    'ninguno': {'lemma': 'ninguno', 'gen': 'masc', 'num': 'sing'},
    'ningún': {'lemma': 'ninguno', 'gen': 'masc', 'num': 'sing'},
    'ninguna': {'lemma': 'ninguno', 'gen': 'fem', 'num': 'sing'},
    'ningunos': {'lemma': 'ninguno', 'gen': 'masc', 'num': 'pl'},
    'ningunas': {'lemma': 'ninguno', 'gen': 'fem', 'num': 'pl'},
    'nadie': {'lemma': 'nadie', 'ultralemma': 'nadie'},
    'nada': {'lemma': 'nada', 'ultralemma': 'nada'},


}


def get_determiner_lemma(word, pos):
    if word in personales_datos:
        return personales_datos[word]
    elif word in posesivos_datos:
        return posesivos_datos[word]
    elif pos == 'DET' and word == 'la':  # problemas homofonía
        return {'lemma': 'el', 'gen': 'fem', 'num': 'sing'}
    elif pos == 'DET' and word == 'los':
        return {'lemma': 'el', 'gen': 'masc', 'num': 'pl'}
    elif pos == 'DET' and word == 'las':
        return {'lemma': 'el', 'gen': 'fem', 'num': 'pl'}
    elif word in determinantes_datos:
        return determinantes_datos[word]
    else:
        functions.show_error('😱 SPACY ERROR', word + ' is not a determiner')
        raise ValueError('')
        # raise ValueError(f'😱 SPACY ERROR: {word} is not a determiner')



"""
Pronombres personales tónicos
    ['yo', 'tu', 'él', 'ella', 'nosotros', 'nosotras', 'vosotros', 'vosotras', 'ellos', 'ellas']
Pronombres personales átonos
    ['me', 'te', 'lo', 'la', 'le', 'se', 'nos', 'os', 'los', 'las', 'les', #
Pronombres personales tónicos en SPREP     
    'mí', 'ti', 'sí'
"""
pronouns = {
    '1S': {'lemma': 'yo', 'label': 'yo'},
    '2S': {'lemma': 'tu', 'label': 'tú'},
    '1P': {'lemma': 'nosotros', 'label': 'nosotr@s'},
    '2P': {'lemma': 'vosotros', 'label': 'vosotr@s'},
    '3S': {'lemma': 'él', 'label': 'él/ella'},
    '3P': {'lemma': 'ellos', 'label': 'ell@s'},
}


# region "IP" sintagma flexivo
# The Leipzig Glossing Rules
# I Indicativo S Subjuntivo M Imperativo C Condicional
mood_mapping = {
    'I': 'IND',
    'S': 'SBJV',
    'M': 'IMP',
    'C': 'COND'
}
"""
Presente
Pasado
Imperfecto
Futuro
"""
tense_mapping = {
    'P': 'PRS',
    'I': 'PST',  # pasado imperfecto
    'S': 'PST',  # pasado perfecto
    'F': 'FUT'
}
def get_analytical_flex_info(word1, word2):
    # ambigüedad del participio de los valores de distinguir VOZ PASIVA O ASPECTO PERFECTO
    # he visto -> aspecto perfecto
    # es visto -> voz pasiva
    ind_flex = get_flex_info(word1['text'], word1['lemma'])
    aff_flex = get_flex_info(word2['text'], word2['lemma'])
    if ind_flex and aff_flex:
        ind_flex = ind_flex[0]
        aff_flex = aff_flex[0]
        if word1['lemma'] == 'ser' and aff_flex['aspect'] == 'PRF':
            ind_flex.update({'voice': 'PASS'})  # no es aspecto PRF sino voz pasiva
        else:
            ind_flex.update({'voice': 'NPASS'})
            ind_flex.update(aff_flex)
        # print(ind_flex, aff_flex)
        return ind_flex


def get_flex_info(word, lemma=None):
    output = []
    word = word.lower()
    if word in verbs_es:
        entries = verbs_es[word]
        for entry in entries:
            tag, entry_lemma = entry
            if lemma is not None and entry_lemma != lemma:
                continue
            if tag[0] == 'V':  # Verb Main/Aux
                append = True
                # A T M P
                mood = tag[2]
                assert mood != '0', ''
                if mood in mood_mapping.keys():
                    person_number = tag[4:6]  # la flexión verbal en español no codifica género (en árabe sí por ejemplo)
                    if tag[3] == 'S':  # cuidado con pret. perf., es el único tiempo simple perfecto
                        obj = {'aspect': 'PRF'}
                    else:
                        obj = {'aspect': 'IPFV'}
                    if tag[3] != '0':
                        obj['tense'] = tense_mapping[tag[3]]
                    obj.update({'mood': mood_mapping[mood], 'voice': 'NPASS', 'person': person_number})
                    # return [obj]
                    # # condense
                    # for i in output:
                    #     if i['mood'] == obj['mood'] and i['tense'] == obj['tense']:
                    #         i['text'] += '/' + obj['text']
                    #         append = False
                # non finite
                elif mood == 'G':  # gerundio
                    obj = {'aspect': 'PROG'}
                elif mood == 'P':  # participio <<<<<<<<<<<<< VOZ PASIVA O ASPECTO PERFECTO
                    obj = {'aspect': 'PRF'}
                elif mood == 'N':  # infinitivo
                    obj = {}

                # if append:
                output.append(obj)
    return output


""" sintagma flexivo
casos:
1) parent VERBO FINITO. fácil
2) parent VERBO NO FINITO. hay que acudir al auxiliar
"""
def find_inflection(graph, token):
    verbs_info = get_flex_info(token.properties['text'].lower())
    if verbs_info:
        verb_info = verbs_info[0]  # <<<<<<<<<<<<<<<<<<
        if 'mood' in verb_info:  # forma finita
            return verb_info
        else:  # no finito
            if 'aspect' not in verb_info:  # infinitivo
                # si es infinitivo, su sujeto es correferente con el sujeto de la oración superior
                # ej.: (yo) quiero (yo) comprar.
                if hasattr(token, 'head'):
                    return find_inflection(graph, token.head)
            elif verb_info['aspect'] == 'PRF' or verb_info['aspect'] == 'PROG':  # participio o gerundio
                # entonces rige un AUX que posee la flexión temporal
                pattern = {'pos': 'AUX'}
                matched = [_ for _ in graph.children(token) if _.match_properties(pattern)]
                if matched:
                    return find_inflection(graph, matched[0])

    else:
        functions.show_error('ERROR', 'verb form is not found: ' + token.properties['text'])


def get_person_properties(person):
    return {'lemma': pronouns[person]['lemma'],
            'text': pronouns[person]['label'],
            # 'old_lemma': person,
            # 'label': pronouns[person]['label'],
            'pos': 'PRON',
            'DET': get_determiner_lemma(pronouns[person]['lemma'], 'PRON')
            }

def find_subject(graph, token):
    if token.match_properties( {'pos': ['VERB', 'AUX']} ):
        flexion = find_inflection(graph, token)
        if flexion is not None:  # and 'lemma' in flexion:
            person = flexion['person']
            return get_person_properties(person)
    else:  # puede ser un atributo, que rige un AUX que posee la flexión temporal
        pattern = {'pos': 'AUX'}
        matched = [_ for _ in graph.children(token) if _.match_properties(pattern)]
        if matched:
            return find_subject(graph, matched[0])  # find subject in AUX
    # print('<<<<<<<<<<<<<< subject not found', token)

#endregion


def reorganiza_det_pos(predicate):
    determiner = predicate.arguments[0].properties
    """
    suple el género del determinante, no especificado en 'mi' 'tu' 'su' y sus plurales mediante el nombre o adjetivo
        mi abuelo   gen:'masc'
        sus casas   gen:'fem'
    el número ya está especificado en el determinante
    """
    # if 'num' not in determiner['DET']:
    #     number = predicate.arguments[1].ref_object.morph.get("Number")
    #     if 'Sing' in number:
    #         determiner['DET']['num'] = 'sing'
    #     elif 'Plur' in number:
    #         determiner['DET']['num'] = 'pl'
    if 'gen' not in determiner['DET']:
        gender = predicate.arguments[1].ref_object.morph.get("Gender")
        if 'Masc' in gender:
            determiner['DET']['gen'] = 'masc'
        elif 'Fem' in gender:
            determiner['DET']['gen'] = 'fem'

    # crea nuevo predicado
    # functor
    if predicate.functor is None:
        properties = {'lemma': 'de', 'text': 'de', 'old_lemma': 'de', 'pos': 'ADP',
                      'text_index': predicate.arguments[0].properties['text_index']}
        # predicate.functor = graph.MyNode(properties['lemma'].upper(), properties)
        predicate.functor = graphs.MyNode('TENER', properties)

    # poseedor
    properties = {'lemma': determiner['DET']['possesor'],
                  'text': determiner['DET']['label'],
                    'old_lemma': determiner['old_lemma'],
                    'pos': 'PRON',  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< NO VALE PARA MÍO TUYO SUYO
                    'text_index': predicate.arguments[0].properties['text_index'],
                    'DET': determiner['DET']}
    properties['DET']['ultralemma'] = determiner['DET']['possesor']
    # sustituye al determinante en el predicado, pero luego al reconocerse como faltante será reubicado en el grafo
    predicate.arguments[0] = graphs.MyNode(properties['lemma'], properties)




# Para ejecutar desde el exterior
if __name__ == "__main__":
    forma = 'vote'   # ['VMM03S0', 'VMSP1S0', 'VMSP3S0']
    print(forma, get_flex_info(forma))
    formas = ['estaba', 'hablar', 'hablado', 'hablando', 'noexiste']
    [print(forma, get_flex_info(forma)) for forma in formas]

    """
    vote [{'mood': 'M', 'tense': '0', 'text': 'él/ella'}, {'mood': 'S', 'tense': 'P', 'text': 'yo/él/ella'}]
    estaba [{'mood': 'I', 'tense': 'I', 'text': 'yo/él/ella'}]
    hablar [{'mood': 'N'}]
    hablado [{'mood': 'P'}]
    hablando [{'mood': 'G'}]
    noexiste []
    """



