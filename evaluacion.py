# -*- coding: utf-8 -*-
# by Alejandro Rojo Gualix 2021-06
import re



""" por ver
    'Pagué religiosamente lo que marcaba el taxímetro al taxista',
    'Pagué religiosamente al taxista lo que marcaba el taxímetro',
    'El superintendente, extraordinariamente disminuido por el susto, es hallado en el atolón de Mururoa.'
    'Saldremos cuando acabe de llover',

    'Cocino cuanto puedo',
    'No conduzcas si bebes',
    'Iré aunque llueva',
    'Vengo para que rematemos el trabajo',
    'Vino para arreglar la puerta',
"""


# ✅
"""
    ARGUMENTOS EVENTIVOS
        ADV -MENTE
        predicación secundaria
        O adv tiempo
        EN DELANTE...
    POSESIVOS
    ORACIÓN CON NÚCLEO SEMÁNTICO NO VERBAL
        APOSICIÓN
    HABER
    AMOD: adjetivos PARTICIPIOS o no PARTICIPIOS
"""
pruebas = {
    'básico': [
        'La casa',
    ],

    'negativas': [
        '✅La casa inadecuada para vivir',
        '✅La casa es inadecuada para vivir',  # in-adecuada -> no adecuada <<<<<<<<<<<<
        '✅La casa no es adecuada para vivir',  # cópula ADJ < 1 2 >
        '✅La casa no es adecuada para una familia con dos hijos',  # cópula ADJ < 1 2 >

        '✅La casa que no es grande',

        '✅No había visto el abismo',
        '✅Nunca había visto el abismo',
        '✅No había visto el abismo nunca',
        '✅Ninguno había visto el abismo',
        '✅Nadie había visto el abismo',
        # 'Ningún ser humano había visto el abismo',  # SPACY considera ser un AUX 😱😱😱😱

        '✅Juan no regaló el libro a Marta',
        '✅Juan no habló en la cocina',  # <<<<<<<<<<<<<<<< ámbito de la negación. Pudo estar en la cocina
    ],

    'O Complementos_regidos': [
        '✅Juan habló del libro a Marta',
        '✅Le hablé del proyecto',
        '✅Les hablé del proyecto',
        # '✅Las hablé con ellos',
        '✅hablé del proyecto a Marta',
        '✅Nosotros hablamos de la política que se hace ahora',  # ambigüedad con SE
        '✅Tiré de la palanca',
        '✅Pensé en ti',
        'Ubicaron la sede en Segovia',  # problema de que es ARG y no ADJ, ya ha sido escogido EN por el predicado
        'Introduje los garbanzos en el tarro en la cocina',
        'Me cansé de pensar tanto mis decisiones',
    ],

    'multiples_predicados': [
        '✅Pepe ronca en el sofá que compramos',  # NOUN->VERB sofá->compramos
        '✅Los bomberos regresan a la casa que ardió anoche',  # NOUN->VERB casa->ardió
        '✅Compré canela en el supermercado de la esquina',  # NOUN->NOUN

        '✅La hija que es ingeniera es muy profesional',

        'Lo dejamos donde nos dijo',  # suboración sustantiva CREA ADJUNTOS NO ARGUMENTOS
    ],


    'AUX': [  # pasiva, haber y estar
        '✅El fuego arruinó la casa',
        '✅La casa fue arruinada',
        '✅El regalo fue devuelto',
        '✅El libro fue regalado a Juan por Marta',

        # '✅Había visto el abismo',
        '✅No lo había imaginado',

        '✅La gente está disfrutando de las fiestas',

        'La casa es demasiado grande para él',
    ], 

    'alternancias de estructura informativa': [
        '✅La casa grande',  # ADJ MOD
        '✅La casa es grande',  # ADJ O cópula
        'La casa que es grande',  # ADJ O' cópula
        '✅La casa que vimos es grande',  # O' cópula ADJ

        '✅El libro de Pepe',
        '✅El libro es de Pepe',
        'El libro que es de Pepe',        
    ],

    'alternancias de participios': [
        'Introduje los garbanzos en el tarro fregado por ti',  # Argumento verbal presidido por 'en'

        # pasivas        
        '✅La casa arruinada',
        '✅La casa fue arruinada',
        '✅La casa arruinada por el fuego',
        '✅La casa fue arruinada por el fuego',
        '✅La casa que fue arruinada por el fuego',

        '✅Mi casa está ubicada en Segovia',
    ],
}



pruebas2 = {
    'pp_sentences': [
        '✅Tengo casa',
        '✅Tengo ojos',

        '✅Esa casa es la mía',
        'La mía es grande',
        'La mía es chalet',
    ],

    'O con cuyo': [
        '✅Saturno era un abismo cuyo fondo ninguna sonda había hollado aún',  # cuyo

        'Es una mujer cuyo cantar es admirable',
        '✅El cliente cuya donación de mil euros nos ha ayudado',
    ],


    'PROPN': [
        'El río Guadalquivir significa río grande',
    ],



    'O nominalizadas': [
        'La tración de Fray Martín al bardo lo mató',
        'La obtención del premio hizo que estuviera muy feliz',
        '✅La obtención del premio le hizo estar muy feliz',
        '✅La obtención del premio fue un hito en su vida personal',

        '✅El ejército ganador de la guerra a Holanda desfiló por las calles',
        '✅El ejército ganado en la guerra a Holanda desfiló por las calles',
        '✅El vecino ganador del premio está muy feliz',  # amod:vecino
        '✅El ciudadano ganador del premio está muy feliz',  # amod:vecino

        '✅La donación de 2 millones del empresario a la fundación',
        'Mi amor es Sheila',
    ],


    'O ADV': [
        # no hace falta hacer nada con el nexo
        '✅Lo hicimos como nos lo explicaste',
        'Fui a la reunión a pesar de que tu no viniste',
        '✅Bebo porque tengo sed',  # PARA < evento1 evento2 >
        '✅Tengo sed, así que bebo',
    ],

    'correferencia': [
        '✅En la colina había antes una casa de piedra que construyó mi abuelo. La construcción era espléndida. La visitaba con frecuencia. Jugaba en su jardín.',
        # '✅En la colina había antes una casa de piedra que construyó mi abuelo. La vivienda era espléndida. La visitaba con frecuencia. Jugaba en su jardín.',

        # '✅En la colina había una casa que construyó mi abuelo. La visitaba. Yo jugaba en su jardín.',
        # de qué es el jardín ¿del abuelo o de la casa? el abuelo la construyó, no es su casa
        # '✅En la colina había una casa que construyó mi abuela. La visitaba. Yo jugaba en su jardín.',

        # 'La vecina es ingeniera. La veo a menudo.',  # N N correferencia PRONOMBRE
        # 'Vi su casa. La mía es más bonita',  # 2 pronombres posesivos PRONOMBRE
        # 'Ya tengo la planta y el macetero grande. Compré la que me dijiste',  # 2 consabido y género en determinante relativo
        # 'Tengo dos casas. Mi casa de Segovia es antigua. Mi casa de campo es grande',
    ],
    'TEXTO': [  # 'La casa arruinada fue su casa' SUYA
    ],

    'PROBLEMAS': [
        # múltiples dependencias
        # 'Tengo casa',
        # 'Tengo ojos',
        'Es una tragedia.',

        'El año en el que te conocí fue 2018',
        '2018 fue el año en el que te conocí',

        'Me dicen que el libro es de esa mujer',
        '¿Qué quieres comer hoy?',
        '¿Qué película quieres ver?'

    ],
    'AHORA': [
        '✅El trueno resonó en el valle mientras jugábamos a un juego de mesa.',


        'El libro fue regalado a Juan por Marta',
        "La casa que fue arruinada por el fuego",

        '✅Quiero que compres una casa',
        'Quiero comprar una casa',
        "La tración de Fray Martín al bardo lo mató",
    ]

}



"""
    oraciones escogidas
    filtrado:
        con menos de 10 palabras
        descartan estructuras que el algoritmo aún no he implementado y no tiene sentido evaluar aún como:
            coordinación
            nombres propios complejos
            predicados nominalizados <<<<<<<<<<<<<
"""
oraciones_evaluacion = [
    'Todo esto le parece mágico.',
    '✅Razones no le faltan.',
    '✅Él lo sabe.',
    '✅Los asistentes quedaron atónitos.',
    # 'Incremento de la polarizabilidad molecular.',
    'Junto a él han surgido otros no menos importantes.',
    'De esa oposición extrema baste aquí una muestra.',

    '✅Ahora también los produce.',
    '✅La situación es muy grave.',
    'Es una tragedia.',
    '✅Un balazo lo derribó en el suelo.',
    '✅No murió en el acto.',  # es compleja
    '✅La vida aquí es muy divertida.',
    '✅Leipzig es una ciudad con mucha marcha.',
    '✅Constantemente abren nuevos bares.',
    '✅Que luego cierran.',
    'Es cierto que las viviendas son malas.',  # "Es cierto"
    'Su mujer procede de la vecina Sajonia-Anhalt.',
    'Cuando lo pusieron en libertad escapó.',  # FRASEOLOGÍA "poner en libertad"
    'La granja se encuentra en un estado desastroso.',
    '✅Sus motivos son de orden económico.',
    '✅Al principio todo fue difícil.',  # fixed 'al principio'
    '✅Más tarde se mudó mi mujer.',
    '✅Son las cinco de la mañana.',
    '✅Los encierros de este pueblo son peculiares.',
    'Desde hace días están concentrados.',
    'Con el personal me llevo bien.',  # sujeto relegado CON
    'Es difícil acostumbrarse a un nuevo sistema.',
    '✅La política industrial ha cambiado.',
    '✅La vuelta está prevista para el día 1 de junio.',  # compound
    '✅Yo soy partidario de cumplir la ley.',
    'Pero en pocos días se ha caído todo.',
    '✅Tenía carisma.',
    'Hoy la reubicación del ex ministro no resulta fácil.',
    '✅No sucedió.',
    '✅No se inmutó.',
    '✅Nadie lo entendió.',
    '✅Pero volvió a perder.',  # <<<<<<<<<<<<<<<
    'También para ella pasaban los años.',
    'Era una flor de ayer.',
    'Ella misma estaba sorprendida de su obediencia.',
    '✅No se arrepentirá.',
    'Ya no le quedaban fuerzas ni para arrepentirse.',
    '✅Me las enseñó usted.',
    '✅Es cierto.',
    '✅No esperó su respuesta.',
    '✅El Bósforo comunica mi infancia con mi muerte.',
    'En el Bósforo siempre hace sol.',  # hacer+hecho meteorológico y SIEMPRE
    'El embalse de agua.',
    '✅Entiende de vientos.',
    '✅Soy marino.',
    '✅Nunca he salido de Trinidad.',
]



def get_sentences(section, data, exclude_checked=False):
    if section:
        keys = [section]
    else:
        keys = list(data.keys())
    sentences = [_ for key in keys for _ in data[key]]  # flatten
    return filter_checked_members(sentences, exclude_checked=exclude_checked)


def filter_checked_members(data, exclude_checked=True):
    if exclude_checked:
        return [_ for _ in data if _[0] != '✅']
    else:
        return [_[1:] if _[0] == '✅' else _ for _ in data]


def count_checked_members(data):
    checked_members = [_ for _ in data if _[0] == '✅']
    unchecked_members = [_ for _ in data if _ not in checked_members]
    proportion = int(len(checked_members)/len(data)*100)

    print('\n'.join(checked_members))
    print('\n'.join(unchecked_members))
    print(f'\n{proportion}% de aciertos')
    print(f'Evaluación positiva de {len(checked_members)} oraciones y negativa de {len(unchecked_members)} oraciones')


def get_corpus_sentences():
    """ http://universal.elra.info/product_info.php?cPath=42_43&products_id=1509
    CESS-ESP Spanish Corpus
    This corpus contains 188,650 words of Spanish which have been syntactically annotated within the framework of the CESS-ECE project (Syntactically & Semantically Annotated Corpora, Spanish, Catalan, Basque). Different types of resources were created:

    - CESS-ESP: the syntactically annotated version.
    - AnCora-ESP: the semantically annotated version.
    - AnCora-LEX-ESP: a verbal lexicon (1869 entries).
    - AnCora-DEP-ESP: annotated with dependencies.

    The CESS-ESP, which is at core here, was annotated using constituents and functions (with AGTK, University of Pennsylvania).
    """
    # NLTK CESS ESP
    from nltk.corpus import cess_esp as cess

    # Read the corpus into a list,
    # each entry in the list is one sentence.
    # cess_sents = cess.tagged_sents()
    # sent = cess_sents[0:50]
    sentences = cess.sents()  # [0:100]
    for sentence in sentences:
        if len(sentence) < 10:
            print(' '.join(sentence))


if __name__ == "__main__":
    from main import run

    # ----------------- Evaluación -----------------
    for sent in filter_checked_members(oraciones_evaluacion, exclude_checked=True):
        run(sent, coreference=False, inference=False)
    count_checked_members(oraciones_evaluacion)
