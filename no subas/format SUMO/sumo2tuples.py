# from lisp_parser.lisp_to_ast import parse_lisp_helper
import sys
import re
# import pytest
import json


import nltk


def tokenize_s_expression(data):
    # s_token_regex = re.compile(r'\(|\)|=>|[?\w]+')
    s_token_regex = re.compile(r';[^\n]+|"[^"]+"|\(|\)|=>|[?\w]+')
    tokens = s_token_regex.findall(data)
    return tokens


def parse_s_expression(tokens):
    new_predicate = []
    while tokens:
        token = tokens.pop(0)
        # print(token)
        if token == '(':
            new_predicate.append(parse_s_expression(tokens))
        elif token == ')':
            return new_predicate
        elif not token[0] == ';':
            new_predicate.append(token)
    return new_predicate[0]


def process_kif(data):
    # parentiza los datos para devolver las expresiones dentro de una única lista
    tokens = tokenize_s_expression('(' + data + ')')
    # print(tokens)
    kif_list = parse_s_expression(tokens[:])
    # print(kif_list)
    return kif_list


def parsedddd(branch, facts):
    """
    :param branch:
    :param facts:
    :return:

    (=>
       (instance ?L Lightning)
       (exists (?C)
          (and
             (instance ?C Cloud)
             (eventLocated ?L ?C))))
    (=>
      (instance ?T Thunder)
      (exists (?L)
        (and
          (instance ?L Lightning)
          (causes ?L ?T))))
    """
    def check(branch, facts):
        true_value = True
        functor = branch[0]
        if functor == 'and':
            for arg in branch[1:]:
                assert isinstance(arg, list)
                # if isinstance(arg, list):
                true_value &= check(arg, facts)
            return true_value
        elif functor == 'instance':
            conditions.append(branch[2])
            entities[branch[1]] = branch[2]
            return branch[2] in facts
        else:
            return False

    def assertf(branch):
        reserved_functors = ['and', 'exists']
        functor = branch[0]
        if functor == 'instance':
            entities[branch[1]] = branch[2]
        elif functor in reserved_functors:
            # if functor == 'and':
            for arg in branch[1:]:
                if isinstance(arg, list):
                    assertf(arg)
        elif len(branch) > 1:  # omit ['?C']
            # print('else', branch)
            assertions.append(branch)

    entities = {}
    conditions = []
    assertions = []
    functor = branch[0]
    if functor == '=>':
        # antecedent
        true_value = check(branch[1], facts)
        # print(true_value, branch[1], facts)
        if true_value:
            # consequent
            assertf(branch[2])
            return entities, conditions, assertions
        else:
            return []


def convert_rule(branch):
    """
    :param branch:
    :param facts:
    :return:

    (=>
       (instance ?L Lightning)
       (exists (?C)
          (and
             (instance ?C Cloud)
             (eventLocated ?L ?C))))
    (=>
      (instance ?T Thunder)
      (exists (?L)
        (and
          (instance ?L Lightning)
          (causes ?L ?T))))
    """
    def check(branch):
        functor = branch[0]
        is_terminal = all([isinstance(_, str) for _ in branch])
        if is_terminal:
            if len(branch) > 1:
                if functor == 'instance':
                    conditions.append(branch[2])
                    entities[branch[1]] = branch[2]
        else:
            for arg in branch[1:]:
                if isinstance(arg, list):
                    assertf(arg)
        # elif functor == 'and':
        #     for arg in branch[1:]:
        #         assert isinstance(arg, list)
        #         check(arg)

    def assertf(branch):
        reserved_functors = ['and', 'exists']
        # exists ( [] , attributes)
        functor = branch[0]
        is_terminal = all([isinstance(_, str) for _ in branch])
        if is_terminal:
            if len(branch) > 1:
                if functor == 'instance':
                    entities[branch[1]] = branch[2]
                else:
                    # new_assertion = [_ if _ not in entities else entities[_] for _ in branch]
                    # if wn_sumo:
                    #     new_assertion = [_ if _ not in wn_sumo else wn_sumo[_] for _ in new_assertion]
                    # assertions.append(new_assertion)
                    assertions.append(branch)
        else:
            for arg in branch[1:]:
                if isinstance(arg, list):
                    assertf(arg)

    entities = {}
    conditions = []
    assertions = []
    functor = branch[0]
    if functor == '=>':
        # if len(branch[1]) == 1:
        # antecedentassertions
        check(branch[1])
        if len(conditions) != 1:  # filter
            return
        assertf(branch[2])
        for index1, assertion in enumerate(assertions):
            for index2, member in enumerate(assertion):
                if member in entities:
                    assertions[index1][index2] = entities[member]
        assertions = [_ for _ in assertions if '?' not in ''.join(_)]

        return entities, conditions, assertions

#
# with open('SUMO2WordNet_mappings.json', 'r', encoding='UTF-8') as f:
#     wn_sumo = json.load(f)


sample2 = """
(first (list 1 (+ 2 3) 9))
(=>
  (instance ?A Aqiqah)
  (exists (?AGENT)
    (and
      (agent ?A ?AGENT)
      (attribute ?A Muslim))))
(instance animal ser_animado)
(instance mamífero animal)
(instance ser_humano mamífero)
(instance Pepe ser_humano)
(vivir Pepe)
(hablar Manuel Pepe)
"""
sample = """
;; Niles, I., and Pease, A.  2001.  Towards a Standard Upper Ontology.
;; In Proceedings of the 2nd International Conference on Formal
(=>
  (instance ?CANDLE Candle)
  (material Wax ?CANDLE))

(=>
  (instance ?C Candle)
  (hasPurpose ?C
    (exists (?F)
      (and
        (instance ?F Fire)
        (resource ?F ?C)))))

(subclass Lightning WeatherProcess)
(subclass Lightning Radiating)
(documentation Lightning EnglishLanguage "A &%WeatherProcess which involves a significant 
release of electricity from a &%Cloud.")

(=>
   (instance ?L Lightning)
   (exists (?C)
      (and
         (instance ?C Cloud)
         (eventLocated ?L ?C))))

(subclass Thunder WeatherProcess)
(subclass Thunder RadiatingSound)
(documentation Thunder EnglishLanguage "Any instance of &%RadiatingSound which is caused by 
an instance of Lightning.")

(=>
  (instance ?T Thunder)
  (exists (?L)
    (and
      (instance ?L Lightning)
      (causes ?L ?T))))
"""

def get_tuples(kif_list):
    output = []
    for rule in kif_list:
        result = convert_rule(rule)
        if result:
            # print('\n', rule)
            entities, conditions, assertions = result
            # print('\n', entities, '\n', conditions, ' -> ', assertions)
            for assertion in assertions:
                new_tuple = (conditions[0], assertion)
                output.append(new_tuple)
                print(new_tuple)
    return output

kif_list = process_kif(sample)
get_tuples(kif_list)

# sys.exit(0)



if __name__ == "__main__":
    output = []

    import glob
    for filename in glob.glob('kifs/*.kif'):
        print(filename)
        # with open(os.path.join(os.cwd(), filename), 'r') as f:  # open in readonly mode
        with open(filename, 'r', encoding='UTF-8') as f:
            raw_kif_sumo = f.read()

        kif_list = process_kif(raw_kif_sumo)
        # print(json.dumps(kif_list, indent=2))
        output.extend(get_tuples(kif_list))

        # json_data = json.dumps(output, indent=2)
        print(len(output), filename)

    json_data = json.dumps(output, indent=2)
    # print(json_data)
    with open('tuples_SUMO.json', 'w', encoding='UTF-8') as f:
        f.write(json_data)
        f.write('\n')

    # do your stuff

    sys.exit(0)

    with open('SUMO_all.kif', 'r', encoding='UTF-8') as f:
    # with open('Mid-level-ontology.kif', 'r', encoding='UTF-8') as f:
        raw_kif_sumo = f.read()

    kif_list = process_kif(raw_kif_sumo)
    # print(json.dumps(kif_list, indent=2))
    output = get_tuples(kif_list)

    # json_data = json.dumps(output, indent=2)
    print(len(output))
    json_data = json.dumps(output)
    # print(json_data)
    with open('tuples_SUMO.json', 'a', encoding='UTF-8') as f:
        f.write(json_data)

    """
    ('Lightning', ['eventLocated', 'Lightning', 'Cloud'])
    ('Lightning', ...)
        'Lightning' -> ['eventLocated', 'Lightning', 'Cloud']
        'Lightning' -> [['eventLocated', 'Lightning', 'Cloud']]
    ('Thunder', ['causes', 'Lightning', 'Thunder'])
        'Thunder' -> ['causes', 'Lightning', 'Thunder']

     [['eventLocated', '?L', '?C']] 
     {'?L': 'Lightning', '?C': 'Cloud'}

    Lightning(L) -> eventLocated(L, C) ^ Cloud(C)
    Lightning(L) -> eventLocated(Cloud)
    
    "Lightning": [
        "forked_lightning.n.01",
        "lightning.n.01",
        "atmospheric_electricity.n.01",
        "thunderbolt.n.01"
    ],

    Mid-level-ontology.kif 3600-3605 	
        If a process is an instance of lightning,
        then there exists an entity such that the entity is an instance of cloud and the process is located at 2

      "electrical_discharge.n.01": [
        "Radiating",
        "Lightning"
      ],
    "atmospheric_electricity.n.01": [
        "Radiating",
        "Process",
        "RadiatingLight",
        "Lightning"
      ],
        "forked_lightning.n.01": [
        "Lightning"
      ],
      "lightning.n.01": [
        "Lightning"
      ],
        "elves.n.01": [
        "RadiatingLight",
        "Lightning"
      ],
      "jet.n.04": [
        "RadiatingLight",
        "Lightning"
      ],
      "thunderbolt.n.01": [
        "Lightning"
      ],
      "sprites.n.01": [
        "RadiatingLight",
        "Lightning"
      ],

    """

    sys.exit(0)

    # raw_kif_entries = re.split(r'[\n\t]{2,}', raw_kif_sumo)
    # remove_whitespaces = re.compile('[\n\t]+|\s{1,}')
    # kif_entries = [remove_whitespaces.sub(' ', entry) for entry in raw_kif_entries if entry != '' and entry[0] != ';']
    # pat2 = re.compile(r'^\((\w+) ')

    """ 200 tipos de cabeceros diferentes
    ss = set()
    for entry in kif_entries:
        fa = pat2.findall(entry)
        if fa:
            ss.add(fa[0])
 ;;;-------------------------------------------------------------------- ;;; Skilled Occupations ;;;-------------------------------------------------------------------- ;;; SkilledOccupation is defined in Mid-level-ontology.kif, here are more specific occupations that are instances or subclasses of SkilledOccupation.            
    """
    # for entry in kif_entries:
    facts_and_rules = [parse_lisp_helper(rule, 0)[0] for rule in kif_entries]
    # [print(rule) for rule in facts_and_rules]

    sys.exit(0)

    normalized = [remove_whitespaces.sub('', rule) for rule in lisp_rulebook.split('\n\n') if rule != '']
    print('\n', normalized)
    # omit ['?C']
    facts_and_rules = [parse_lisp_helper(rule, 0)[0] for rule in normalized]
    # [print(rule) for rule in facts_and_rules]
    rule = facts_and_rules[0]
    facts = ['lightning.n.01']
    SUMO_facts = [wn_sumo[_][0] for _ in facts if _ in wn_sumo]
    # SUMO_facts = ['Lightning']

    print('\n')
    entities, conditions, assertions = convert_rule(rule, SUMO_facts)
    print('\n', entities, '\n', conditions, '\n', assertions)


sys.exit(0)

import json
with open('SUMO-WordNet_Mappings.json', 'r', encoding='UTF-8') as f:
    wn_sumo = json.load(f)

print(wn_sumo)
sys.exit(0)

from nltk.corpus import wordnet as wn
# syn1 = wn.synset('forked_lightning.n.02')

syn1 = wn.synsets('thunderbolt')
print(syn1)


ss = wn.synset('thunderbolt.n.01')
print(ss.name())

print(ss.offset())
# print(ss.offset().zfill(8))


"""
{'greaterThan', 'conventionalLongName', 'currencyType', 'directoryOf', 'subLanguage', 'refers', 'disjointRelation', 'capability', 'attribute', 'relatedInternalConcept', 'equipmentCount', 'documentation', 'identityElement', 'codeMapping', 'range', 'defaultMeasure', 'rMProgramOf', 'meetsSpatially', 'experiencer', 'starts', 'initialPart', 'lengthOfPavedHighway', 'flagState', 'fleetDeadWeightTonnage', 'runningOn', 'militaryOfArea', 'disjointDecomposition', 'patient', 'component', 'managedBy', 'path', 'speedScaleAttribute', 'systemMeasured', 'origin', 'hasThroughVariable', 'termFormat', 'greaterThanOrEqualTo', 'domainSubclass', 'forall', 'surface', 'part', 'actionTendency', 'geographicSubregion', 'givenName', 'typicalPart', 'uses', 'unitMeasuringPerformance', 'dataProcessed', 'udaCanSignify', 'claimedTerritory', 'speedScaleAttributeMinMax', 'subOrganization', 'programRunning', 'cardinality', 'duration', 'not', 'systemBehavior', 'represents', 'equal', 'orientation', 'totalArea', 'contraryAttribute', 'KappaFn', 'utterance', 'deviceOS', 'task', 'economyType', 'typicallyContainsPart', 'meatOfAnimal', 'monitorApplicationData', 'abbreviation', 'monetaryValue', 'subAttribute', 'lessThanOrEqualTo', 'member', 'benchmarkPerformance', 'fitForMilitaryService', 'oppositeDirection', 'dataStreamSlack', 'capableAtLocation', 'trafficableForTrafficType', 'or', 'containsInformation', 'hasDimension', 'properPart', 'instance', 'militaryAge', 'vesselDisplacement', 'computerRunning', 'fleetGrossRegisteredTonnage', 'pastTense', 'finishes', 'time', 'hasVariable', 'subField', 'MeasureFn', 'performanceResult', 'hasSkill', 'manufacturer', 'trackWidth'...
"""