# http://www.nltk.org/howto/corpus.html

# 
# 
# # The VerbNet corpus is a lexicon that divides verbs into classes, based on their syntax-semantics linking behavior. The basic elements in the lexicon are verb lemmas, such as 'abandon' and 'accept', and verb classes, which have identifiers such as 'remove-10.1' and 'admire-31.2-1'. These class identifiers consist of a representative verb selected from the class, followed by a numerical identifier. The list of verb lemmas, and the list of class identifiers, can be retrieved with the following methods:
# 
from nltk.corpus import verbnet
out = verbnet.lemmas()[20:25]
print(out)
# ['accelerate', 'accept', 'acclaim', 'accompany', 'accrue']
out = verbnet.classids()[:5]
print(out)
# ['accompany-51.7', 'admire-31.2', 'admire-31.2-1', 'admit-65', 'adopt-93']
# 
# # The classids() method may also be used to retrieve the classes that a given lemma belongs to:
# 
out = verbnet.classids('accept')
print(out)
# ['approve-77', 'characterize-29.2-1-1', 'obtain-13.5.2']
# 
# The primary object in the lexicon is a class record, which is stored as an ElementTree xml object. The class record for a given class identifier is returned by the vnclass() method:
# 
out = verbnet.vnclass('remove-10.1') # doctest: +ELLIPSIS
print(out)
# <Element 'VNCLASS' at ...>
# 
# The vnclass() method also accepts "short" identifiers, such as '10.1':
# 
out = verbnet.vnclass('10.1') # doctest: +ELLIPSIS
print(out)
# <Element 'VNCLASS' at ...>
# 
# See the Verbnet documentation, or the Verbnet files, for information about the structure of this xml. As an example, we can retrieve a list of thematic roles for a given Verbnet class:
# 

def getPredicate(name):
	# Theme
	# Experiencer [+animate]
	# Predicate
	print('\n', name)
	vn = verbnet.vnclass(name)
	for themrole in vn.findall('THEMROLES/THEMROLE'):
		print(themrole.attrib['type'], end=' ')
		for selrestr in themrole.findall('SELRESTRS/SELRESTR'):
		    print('[%(Value)s%(type)s]' % selrestr.attrib, end=' ')
		print()



word = 'admire'
word = 'marry'

print('*' * 50)
print(word)
ids = verbnet.classids(word)
[getPredicate(id) for id in ids]


# 
# The Verbnet corpus also provides a variety of pretty printing functions that can be used to display the xml contents in a more concise form. The simplest such method is pprint():
# 

print('\n', verbnet.pprint('57'))
# weather-57
#   Subclasses: (none)
#   Members: blow clear drizzle fog freeze gust hail howl lightning mist
#     mizzle pelt pour precipitate rain roar shower sleet snow spit spot
#     sprinkle storm swelter teem thaw thunder
#   Thematic roles:
#     * Theme[+concrete +force]
#   Frames:
#     Intransitive (Expletive Subject)
#       Syntax: LEX[it] LEX[[+be]] VERB
#       Semantics:
#         * weather(during(E), Weather_type, ?Theme)
#     NP (Expletive Subject, Theme Object)
#       Syntax: LEX[it] LEX[[+be]] VERB NP[Theme]
#       Semantics:
#         * weather(during(E), Weather_type, Theme)
#     PP (Expletive Subject, Theme-PP)
#       Syntax: LEX[it[+be]] VERB PREP[with] NP[Theme]
#       Semantics:
#         * weather(during(E), Weather_type, Theme)
# 
# 