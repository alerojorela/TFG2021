import sys
import requests
import collections
from nltk.corpus import stopwords
# ...

with open('ontology/conceptNet_usedfor.tsv', 'r') as f:
    tuples = [line.strip().split('\t') for line in f.readlines()]
    data_dump = {_[0]: _[1] for _ in tuples}


def query(term, relationship):
    if relationship == 'UsedFor':
        if term in data_dump:
            return data_dump[term]

    # response = requests.get('http://api.conceptnet.io/c/en/%s' % term)
    response = requests.get('http://api.conceptnet.io/query?start=/c/en/%s&rel=/r/%s&limit=1000' % (term, relationship))
    obj = response.json()

    if not obj['edges']:
        return
    data = []
    for edge in obj['edges']:
        if edge['rel']['label'] == relationship:
            end = edge['end']['label']
            # print(end)
            data.append(end)
            # if 'surfaceText' in edge:
            #     print('\t', edge['surfaceText'])

    # bridge ->
    # text = """
    # crossing a river
    # cross a river
    # cross over a body of water
    # cross a bay
    # cross water
    # """
    by_terms = True
    if by_terms:
        text = ' '.join(data)
        tokens = text.split()
    else:
        tokens = data
    # remove stop words
    lexical_tokens = [token for token in tokens if token not in stopwords.words('english')]

    results = list(collections.Counter(lexical_tokens).items())
    # print(results)
    b = collections.Counter(lexical_tokens).most_common(1)
    result = b[0][0]

    if relationship == 'UsedFor':
        print(f'a {term} is used for {result}')
        with open('ontology/conceptNet_usedfor.tsv', 'a') as f:
            f.write(term + '\t' + result + '\n')

    return result


if __name__ == "__main__":
    term = 'cat'
    print('UsedFor\t', query(term, 'UsedFor'))

    print('CreatedBy\t', query(term, 'CreatedBy'))

    print('AtLocation\t', query(term, 'AtLocation'))

    print('LocatedNear\t', query(term, 'LocatedNear'))


