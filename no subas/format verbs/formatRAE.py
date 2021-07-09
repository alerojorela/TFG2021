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
filename = 'RAE conjugaciones verbales.xml'

import xml.etree.ElementTree as ET
tree = ET.parse(filename)
# with open(filename, encoding="utf-8") as fp:
#     tree = ET.fromstring(fp.read())
root = tree.getroot()

TM_map = [
    'N0',
    'P0',
    'G0',
    'IP',
    'IF',
    'II',
    'C0',  # 7
    'IS', # 8
    'SP', # 9
    'SI', # 10
    'SF',
    'M0',
]
person_map = {
    'yo': '1S',
    'tú': '2S',
    'vos': '2S',
    'él': '3S',
    'nosotros': '1P',
    'vosotros': '2P',
    'ellos': '3P',
}

reg_remove = re.compile(r'^(?:me|te|se|nos|os) ')
# df = reg_remove.sub('', 'nos virilizamos')
# sys.exit(0)

form_dict = {}
tuples = []
def add_form(eagle_tag, form, lemma):
    assert len(eagle_tag) == 7, 'error'
    assert form, 'error: empty form'
    assert lemma, 'error: empty lemma'

    if form.count(' ') != 0:
        form = reg_remove.sub('', form)
    assert form.count(' ') == 0, 'error: form space'
    # print(eagle_tag, form, lemma)
    this_tuple = (eagle_tag, lemma)
    if form in form_dict:
        form_dict[form].append(this_tuple)
    else:
        form_dict[form] = [this_tuple]
    # tuples.append((eagle_tag, form, lemma))


verbs = root.findall(f"./Verbo")
for verb in verbs:
    heading = 'V'
    lemma = verb.get('Text')
    if lemma in ['haber', 'estar', 'ser']:
        heading += 'A'
    else:
        heading += 'M'
    for tense in verb.findall("./Tiempo"):
        value = tense.get('Text')
        index_tm = int(tense.get('tId')) - 1
        if index_tm < 3:  # formas infinitas
            persons = tense.findall("./P")
            eagle_tag = heading + TM_map[index_tm] + '0' * 3
            for person in tense.findall("./P"):
                form = person.get('Text')
                if form:
                    add_form(eagle_tag, form, lemma)

            # if len(persons) > 1 and index_tm != 2:  # gerundio �ampe�ndome �ampe�ndote
            #     assert len(persons) == 1, 'error: non finite form expected '
        else:
            for person in tense.findall("./P"):
                a = person.get('P')
                value_p = person_map[person.get('P')]
                eagle_tag = heading + TM_map[index_tm] + value_p + '0'
                form = person.get('Text')
                if form:
                    add_form(eagle_tag, form, lemma)


# with open('result.json', 'w', encoding="utf-8") as f:
#     f.write(json.dumps(form_dict, indent=2).encode("UTF-8"))
output = json.dumps(form_dict, indent=2)
import re
output = re.sub(r'\\u00f1', 'ñ', output)
output = re.sub(r'\\u00e1', 'á', output)
output = re.sub(r'\\u00e9', 'é', output)
output = re.sub(r'\\u00ed', 'í', output)
output = re.sub(r'\\u00f3', 'ó', output)
output = re.sub(r'\\u00fa', 'ú', output)
output = re.sub(r'\\u00fc', 'ü', output)

# with open('result.json', 'wb') as f:
with open('result.json', 'w') as f:
    # f.write(output.encode("UTF-8"))
    f.write(output)
