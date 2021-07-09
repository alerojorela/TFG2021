# -*- coding: utf-8 -*-
# by Alejandro Rojo Gualix 2021-06
import re
import json
from itertools import count
# MÍOS
# import morphology

"""
http://clic.ub.edu/mbertran/ancora/lexentry.php?file=abandonar.lex.xml&lexicon=AnCoraVerb_ES
"""
filename = 'abandonar.lex.xml'
filename = 'ancora-verb-es_merged.xml'

import xml.etree.ElementTree as ET
tree = ET.parse(filename)
root = tree.getroot()


def map_sem_pred(lemma, pred, debug=False):
    if debug: print('> ', lemma, pred)
    best_match = None

    frames = root.findall(f"./lexentry[@lemma='{lemma}']//frame")
    for frame in frames:
        if debug: print('_' * 20)
        test = {
            'arguments': {},
            'adjuncts': pred.copy()
        }
          # shallow copy of the dictionary
        for argument in frame.findall("argument"):
            argument = argument.get('argument')
            function = argument.get('function')
            thematicrole = argument.get('thematicrole')

            constituent = argument.find("constituent")  # findall
            if constituent is not None:
                preposition = constituent.get("preposition")
                if debug: print(argument, function, thematicrole, preposition)
            else:
                if debug: print(argument, function, thematicrole)

            if argument == 'argM':
                if constituent is not None and preposition in test['adjuncts']:
                    test['adjuncts'][thematicrole] = test['adjuncts'][preposition]
                    del test['adjuncts'][preposition]
            else:
                if function == 'suj' and 'nsubj' in test['adjuncts']:  # match
                    test['arguments'][thematicrole] = test['adjuncts']['nsubj']
                    del test['adjuncts']['nsubj']
                elif function == 'cd' and 'posibilidad' in test['adjuncts']:  # match
                    test['arguments'][thematicrole] = test['adjuncts']['posibilidad']
                    del test['adjuncts']['posibilidad']

                elif thematicrole == 'ori' and 'de' in test['adjuncts']:  # match
                    test['arguments'][thematicrole] = test['adjuncts']['de']
                    del test['adjuncts']['de']
                elif thematicrole == 'ori' and 'desde' in test['adjuncts']:  # match
                    test['arguments'][thematicrole] = test['adjuncts']['desde']
                    del test['adjuncts']['desde']
                    
                elif constituent is not None and preposition in test['adjuncts']:
                    test['arguments'][thematicrole] = test['adjuncts'][preposition]
                    del test['adjuncts'][preposition]
                else:
                    if debug: print('UNMATCHED FRAME')
                    test = None
                    break  # next frame

        if test is not None:
            # if best_match is None or len(test['adjuncts'].keys()) < len(best_match['adjuncts'].keys()):
            if best_match is None or len(test['adjuncts']) < len(best_match['adjuncts']):                
                best_match = test

    # print('> ', test['arguments'], test['adjuncts'])
    return best_match


# toma dos listas, si halla un elemento en la primera devuelve el coposicionado en la otra
def map(value, arrs):
    index = arrs[0].index(value)
    if index == -1:
        return None
    else:
        return arrs[1][index]


"""
EXPLORACIÓN DE VALORES
    search = root.findall(f".//constituent")
    conjunto = { searched.attrib['preposition'] for searched in search }    

RESULTADOS, valores
    frame
        type
            {'resultative', 'passive', 'ditransitive', 'transitive', 'cognate_object', 'default', 'intransitive', 'anticausative', 'causative', 'object_extension', 'unaccusative', 'impersonal', 'benefactive', 'oblique_subject'}
        lss [A VECES NO EXISTE]
            {'A33.ditransitive-theme-locative', 'B23.unaccusative-cotheme', 'B23.unaccusative-theme-cotheme', 'A34.ditransitive-patient-theme', 'A22.transitive-agentive-theme', 'D31.inergative-source', 'C41.state-benefactive', 'C31.state-scalar', 'C21.state-attributive', 'B21.unaccusative-state', 'D11.inergative-agentive', 'C11.state-existential', 'C42.state-experiencer', 'A31.ditransitive-patient-locative', 'A32.ditransitive-patient-benefactive', 'D21.inergative-experiencer', 'A23.transitive-agentive-extension', 'B12.unaccusative-passive-ditransitive', 'A13.ditransitive-causative-instrumental', 'A35.ditransitive-theme-cotheme', 'A11.transitive-causative', 'B11.unaccusative-motion', 'B22.unaccusative-passive-transitive', 'A12.ditransitive-causative-state', 'A21.transitive-agentive-patient'}    
        default [A VECES NO EXISTE]
            yes

    ARGUMENT
        argument
            {'arg0', 'arg1', 'arg2', 'arg3', 'arg4'
            , 'arg', 'argM',
            'argL', 'aer2', 'arm', 'arrgM'}
        thematicrole [A VECES NO EXISTE]
            {'', 'ins', 'ben', 'ext', 'exp', 'adv', 'src', 'atr', 'con', 'tm', 'en', 'cau', 'conadv', 'pat', 'fin', 'ein', 'por', 'de', 'a', 'tem', 'cot', 'des', 'según', 'mnr', 'ori', 'agt', 'dv', 'loc', 'tmp', 'efi'}
        function
            'ci', 'suj', 'cd',
            'atr' 'cpred'
            'creg',  'cag'
            , 'cc'

            <argument argument="arg0" function="cag" thematicrole="agt">
                <constituent preposition="por" type="sp"/>
            </argument>

            <lexentry lemma="aquejar" lng="es" type="verb"><sense id="1">
                <frame lss="A11.transitive-causative" type="default"><argument argument="arg0" function="suj" thematicrole="cau"/><argument argument="arg1" function="cd" thematicrole="tem"/></frame>
                <frame default="yes" lss="B22.unaccusative-passive-transitive" type="passive">
                <argument argument="arg1" function="suj" thematicrole="pat"/>
                <argument argument="arg0" function="cag" thematicrole="agt">
                    <constituent preposition="de" type="sp"/>
                </argument><examples><example>
                
        CONSTITUENT
            preposition
                {'a_favor_de', 'contra', 'sobre', 'a', 'sin', 'para', 'entre', 'em', 'frente', 'bajo', 'pa', 'de', 'como', 'porque', 'en_contra_de', 'ante', 'hacia', 'con', 'lo', 'desde', 'hasta', 'dentro', 'en', 'tras', 'antes', 'según', 'acerca_de', 'a_cerca_de', 'mientras', 'que', 'durante', 'amb', 'por', 'mediante', 'efi'}
                'em', 'pa', 'amb', 'efi'}
                'porque' 'lo', 'que',
            type
                sp
"""



"""
        ┌─► Yo        nsubj    yo         PRON      
   ┌┬───┴── tiré      ROOT     tirar      VERB      
   ││  ┌──► de        case     de         ADP       
   ││  │┌─► la        det      el         DET       
   │└─►└┴── palanca   obl      palanca    NOUN      
   └──────► .         punct    .          PUNCT     
        ┌─► Yo        nsubj    yo         PRON      
    ┌┬──┴── pensé     ROOT     pensar     VERB      
    ││  ┌─► en        case     en         ADP       
    │└─►└── ti        obj      tú         PRON      
    └─────► .         punct    .          PUNCT     
        ┌─► Mi        det      mi         DET       
     ┌─►└── casa      nsubj    casa       NOUN      
     │  ┌─► está      cop      estar      AUX       
    ┌┼──┴── ubicada   ROOT     ubicado    ADJ       
    ││  ┌─► en        case     en         ADP       
    │└─►└── Segovia   obl      Segovia    PROPN     
    └─────► .         punct    .          PUNCT     
        ┌─► Yo        nsubj    yo         PRON      
   ┌┬┬──┴── introduje ROOT     introducir VERB      
   │││  ┌─► los       det      el         DET       
   ││└─►└── garbanzos obj      garbanzo   NOUN      
   ││  ┌──► en        case     en         ADP       
   ││  │┌─► el        det      el         DET       
   │└─►└┴── tarro     obl      tarro      NOUN      
   │   ┌──► en        case     en         ADP       
   │   │┌─► la        det      el         DET       
   └──►└┴── cocina    obl      cocina     NOUN      
"""
function_mapping = [
    ['suj', 'cd', 'ci', 'creg', 
    'cag', 'atr', 'cpred', 'cc'],
    ['nsubj', 'obj', ['iobj', 'obj'], ['obj', 'obl'],
    'obl', 'ROOT', '?', 'obl'],
]
argument_regex = re.compile(r'(?:arg)(\d)')

# ['NOUN', 'PROPN', 'PRON'],
anomalias = []
def registra_anomalia(lemma, obj):
    anomalias.append(obj)
    # print('>>>>>>>>><< ANOMALIA', lemma)


# admite un lemma o 
def convert_lexentry(lexentry):
    # <frame default="yes" lss="B22.unaccusative-passive-transitive" type="passive">
    lemma = lexentry.attrib['lemma']
    name = f'{lemma}'
    #name = lemma 

    # La diátesis es el nombre que se da a cada una las diferentes estructuras argumentales o predicados que pueden construirse a partir de un mismo verbo léxico
    diatesis = {
        'NAME': name, 'lemma': lemma, # , '#': 0,
        'ALTERNATIVES': []
    }
    # diatesis / alternative / posibilidad

    frames = lexentry.findall(f".//frame")  # ignore sense distinctions
    for frame in frames:  # diatesis
        tipo = frame.attrib['type']
        if 'lss' in frame.attrib:
            tipo += '-' + frame.attrib['lss']


        # impersonal
        if tipo == 'passive':
            alternative = { 'NAME': tipo, 'CHILDREN': [
                {'ALTERNATIVES': [
                    {'pos': 'AUX', 'lemma': 'ser'},
                    {'dep': 'obj', 'lemma': 'se'},
                ]}
            ]} # , 'OPTIONAL_CHILDREN': [] }
        else:
            alternative = { 'NAME': tipo, 'CHILDREN': [] } # , 'OPTIONAL_CHILDREN': [] }
        diatesis['ALTERNATIVES'].append( alternative )

        argument_counter = 0

        for argument in frame.findall("argument"):
            if argument.attrib['argument'] != 'argM':
                # posibilidad = {name: value for name, value in argument.attrib.items() if value }
                posibilidad = {}

                argument_regex = re.compile(r'(?:arg)([0-9L])')
                m = argument_regex.match(argument.attrib['argument'])
                if m:
                    # index = m.group(1)
                    # posibilidad['#'] = int(index) + 1
                    posibilidad['#'] = argument_counter + 1
                else:
                    continue
                    print("ANOMALIA-NO HAY")
                    posibilidad['#'] = f"ANOMALIA-{argument.attrib['argument']}"
                    registra_anomalia(lemma, frame)

                if 'thematicrole' in argument.attrib:  # no siempre existe este atributo
                    posibilidad['thematicrole'] = argument.attrib['thematicrole']
                else:
                    continue
                    print("ANOMALIA-NO HAY")
                    posibilidad['thematicrole'] = f"ANOMALIA-NO HAY thematicrole"
                    registra_anomalia(lemma, frame)

                argument_counter += 1

                posibilidad['pos'] = '@@NP_head@@'  # ['NOUN', 'PROPN', 'PRON']
                posibilidad['dep'] = map(argument.attrib['function'], function_mapping)

                """ problemas con pronombres que no requieren a
                TODOS OBJ
                        ┌─► Le        obj      él         PRON      
                    ┌┬──┴── hablé     ROOT     hablar     VERB      
                    ││  ┌─► del       case     del        ADP       
                    │└─►└── proyecto  obj      proyecto   NOUN      
                    └─────► .         punct    .          PUNCT 

                "hablé del proyecto a Marta ."
                    ┌┬┬───── hablé     ROOT     hablar     VERB      
                    │││  ┌─► del       case     del        ADP       
                    ││└─►└── proyecto  obj      proyecto   NOUN      
                    ││   ┌─► a         case     a          ADP       
                    │└──►└── Marta     obj      Marta      PROPN     
                    └──────► .         punct    .          PUNCT 
                """                    
                pronounsD = ['lo', 'la', 'los', 'las']
                pronounsI = ['le', 'les', 'se']

                constituents = argument.findall("constituent")  # findall
                if constituents:
                    marks = [constituent.attrib['preposition'] for constituent in constituents]
                    if 'de' in marks:
                        marks.append('del')

                    if argument.attrib['function'] == 'cd':
                        # ANCORA no señala que ciertas restricciones son opcionales como el 'a' del CD
                        if not (len(marks) == 1 and 'a' in marks):
                            posibilidad['ALTERNATIVES'] = [ 
                                { 'CHILDREN': [ {'lemma': marks} ] },
                                { 'lemma': pronounsD }
                            ]
                    elif argument.attrib['function'] == 'ci':
                        posibilidad['ALTERNATIVES'] = [ 
                            { 'CHILDREN': [ {'lemma': marks} ] },
                            { 'lemma': pronounsI }
                        ]
                    else:
                        posibilidad['CHILDREN'] = [ { 'lemma': marks } ]
                """
                else:
                    if argument.attrib['function'] == 'cd':
                        posibilidad['ALTERNATIVES'] = [
                            { 'lemma': pronounsD },
                            {}  # cualquier otro valor
                            ]       
                """

                if argument.attrib['function'] == 'suj':  # el sujeto puede recuperarse de la flexión del verbo finito
                    # posibilidad['fNOTFOUND'] = 'function(morphology.find_subject)'  # avoid it will be replaced later
                    posibilidad['fNOTFOUND'] = '@@morphology.find_subject@@'  # avoid it will be replaced later
                
                alternative['CHILDREN'].append(posibilidad)


                """
                if argument.attrib['function'] == 'suj':
                    posibilidad['fNOTFOUND'] = 'function(morphology.find_subject)'  # avoid it will be replaced later
                    alternative['OPTIONAL_CHILDREN'].append(posibilidad)
                    # 'OPTIONAL_CHILDREN': [{ 'fNOTFOUND': morphology.find_subject, 'dep': 'nsubj', 'pos': ['NOUN', 'PROPN', 'PRON'], '#':1 }]
                else:
                    alternative['CHILDREN'].append(posibilidad)
                """

        alternative['val'] = argument_counter # len(alternative['CHILDREN'])
        # alternative['val'] = len(alternative['OPTIONAL_CHILDREN']) + len(alternative['CHILDREN'])

    # reordena de mayor a menos valencia, establece preferencia por las diátesis con más valencia para capturar el mayor número de argumentos posibles
    diatesis['ALTERNATIVES'] = sorted(diatesis['ALTERNATIVES'], key=lambda x: x['val'], reverse = True)

    return diatesis


def convert_lemma(lemma):
    lexentry = root.find(f"./lexentry[@lemma='{lemma}']")
    return convert_lexentry(lexentry)


def convert_to_JSON(lemmas=None):
    esquema_ejemplo = { 'NAME': 'Oración',
        'pos': 'VERB', '#':0,
        'ALTERNATIVES': [  # 1 alternativas de verbos
            { 'NAME': 'VerboLEMMA', 'lemma': '<<<<<<<<<<<',
                'ALTERNATIVES': [
                    { 'CHILDREN': [
                        { 'pos': 'AUX', 'lemma': 'ser' },
                    ]}
                ]
            }
        ]
    }

    verbos = { 'NAME': 'Oración',
        'pos': 'VERB', '#':0,
        'ALTERNATIVES': []
    }

    if not lemmas:
        lexentries = root.findall(f"./lexentry")
        for lexentry in lexentries:
            if not lexentry.attrib['lemma'] in ['estar']:
                output = convert_lexentry(lexentry)
                # output.replace
                verbos['ALTERNATIVES'].append(output)
    elif isinstance(lemmas, list): 
        output = [convert_lemma(lemma) for lemma in lemmas]
        verbos['ALTERNATIVES'].extend(output)
    else:
        output = convert_lemma(lemmas)
        verbos['ALTERNATIVES'].append(output)

    final_string = "import morphology\nNP_head = ['NOUN', 'PROPN', 'PRON']\npatterns = { 'es': [\n"+ json.dumps(verbos, indent=4) + "\n]}"
    # replace for function call because:
    # TypeError: Object of type function is not JSON serializable
    # "function(find_subject)" -> find_subject
    # final_string = re.sub(r'"function\((.+)\)"', r'\1', final_string)
    final_string = re.sub(r'"@@(.+)@@"', r'\1', final_string)
    return final_string


# Para ejecutar desde el exterior
if __name__ == "__main__":
    lista = ['hablar', 'tirar', 'pensar', 'ubicar', 'introducir', 'dar']
    output = convert_to_JSON()

    console = True
    if console:
        print(output)
    else:
        filename = 'ancora_patterns.py'
        with open(filename, 'w') as f:
            f.write(output)

    import sys
    sys.exit(0)

    convert_to_JSON()
    convert_to_JSON('abandonar')


"""
    <lexentry lemma="abandonar" lng="es" type="verb">
        <sense id="1">
            <frame default="yes" lss="A21.transitive-agentive-patient" type="default">
            <argument argument="arg0" function="suj" thematicrole="agt"/>

<frame default="yes" lss="A21.transitive-agentive-patient" type="default"><argument argument="arg0" function="suj" thematicrole="agt"/><argument argument="arg1" function="cd" thematicrole="pat"/>
<frame lss="B22.unaccusative-passive-transitive" type="passive">


'text' 'dep' 'lemma' 'pos'  

<argument argument="arg0" function="cag" thematicrole="agt">
    <constituent preposition="por" type="sp"/>
</argument>
->
{ #:"0"         'pos':['NOUN', 'PROPN', 'PRON']     dep: "????"         thematicrole:"agt" 
, 'CHILDREN': [
        { 'dep': 'case', 'lemma': 'por' }  # complemento agente
]
}


<argument argument="arg0" function="cag" thematicrole="agt">
    <constituent preposition="por" type="sp"/>
</argument>

<argument argument="arg0" function="suj" thematicrole="agt"/>
<argument argument="arg1" function="cd" thematicrole="pat">
    <constituent preposition="a" type="sp"/>
</argument>                
"""
