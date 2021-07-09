import sys
import json
import re
# import nltk
from nltk.corpus import wordnet as wn

"""
n    NOUN 
v    VERB 
a    ADJECTIVE 
s    ADJECTIVE SATELLITE 
r    ADVERB 
"""
filename = 'SUMO-WordNet_Mappings.txt'

with open(filename, 'r', encoding='UTF-8') as f:
    file_data = f.readlines()

wordnet2sumo = {}
sumo2wordnet = {}
pat = re.compile(r'(\b\d{8}) (?:\d\d )?([nvasr])')
pat = re.compile(r'^(\d{8}) (?:\d\d )?([nvasr])')
sumo_id = re.compile(r'&%(\w+).$')
for line in file_data:
    if line[0:2] != ';;':
        # print(line)
        msumo1 = sumo_id.findall(line)
        if msumo1:
            assert len(msumo1) == 1
            msumo = msumo1[0]
            # print(line, msumo1)
            for match in pat.findall(line):
                offset = int(match[0].zfill(8))
                ss = wn.synset_from_pos_and_offset(pos=match[1], offset=offset)
                name = ss.name()
                # print(match, '-->', name)
                if name in wordnet2sumo:
                    if msumo not in wordnet2sumo[name]:
                        wordnet2sumo[name].append(msumo)
                else:
                    wordnet2sumo[name] = [msumo]

                if msumo in sumo2wordnet:
                    if name not in sumo2wordnet[msumo]:
                        sumo2wordnet[msumo].append(name)
                else:
                    sumo2wordnet[msumo] = [name]

                # print(match, end='')
            # print()


with open('WordNet2SUMO_mappings.json', 'w', encoding='UTF-8') as f:
    new_data = json.dumps(wordnet2sumo, indent=2)
    print(new_data)
    f.write(new_data)

with open('SUMO2WordNet_mappings.json', 'w', encoding='UTF-8') as f:
    new_data = json.dumps(sumo2wordnet, indent=2)
    f.write(new_data)

