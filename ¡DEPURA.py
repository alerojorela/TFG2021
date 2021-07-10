# -*- coding: utf-8 -*-
# by Alejandro Rojo Gualix 2021-06
import sys
import evaluacion
from main import run


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


if __name__ == "__main__":
    print('DEBUG')

    text = 'la casa de piedra que vimos este verano cercana a la playa'
    text = 'la casa de piedra donde vivía una anciana'
    text = 'En la colina había una casa de piedra. La casa era grande. La construyó mi abuelo.'
    text = 'El abuelo está roncando en el sillón.'

    from predicates import patterns as patterns
    print('\n'.join([_['NAME'] for _ in patterns.patterns['es']]))
    """
    CON ARGUMENTO EVENTIVO
        entidad N
        adverbio -mente
        ✅predicación secundaria - adj
        predicación secundaria - gerundio
        x O adv tiempo
        ✅verbo+EN
        x verbo+advmod
        ✅ESTAR+EN
        ✅ESTAR+advmod
        # AUX Prep
        ✅EN←donde
    POSESIVOS
        ✅det-posesivo
        AUX posesivo
    N
        N COP SN
    PP
        ✅NOUN PP+N
        ✅NOUN COP PP+N
        ✅TENER←cuyo
    ADJ
        ✅adj
        ✅adj COP
    HABER
        haber+en
        haber+ADVPP
        EXISTIR
    """
    # sentences = patterns.get_sentences('haber+en', exclude_checked=False)
    # sentences = evaluacion.get_sentences('oraciones_estar', exclude_checked=True)
    # sentences = evaluacion.get_sentences('multiples_predicados', data=evaluacion.pruebas, exclude_checked=False)
    sentences = evaluacion.get_sentences(None, data=evaluacion.pruebas, exclude_checked=True)

    print('\n'.join(sentences))
    sentences = [
        # 'La casa',
        # 'La casa que es grande',
        # 'La casa grande',
        # 'Comía mientras estudiaba',


        # 'El libro que es de Pepe',
        # 'Introduje los garbanzos en el tarro en la cocina',
        # 'Lo dejamos donde nos dijo',
        # 'La casa es demasiado grande para él',
        # 'Introduje los garbanzos en el tarro fregado por ti',
    ]
    # for sentence in sentences:
    #     run(sentence, coreference=False, inference=False)

    sentences = [
        'Leí el libro. El autor es extraordinario.'
    ]
    for sentence in sentences:
        run(sentence, coreference=True, inference=True)


    sys.exit(0)
