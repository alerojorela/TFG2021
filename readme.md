

## Instalación

```
import nltk
nltk.download('omw')

# https://stackoverflow.com/questions/52677634/pycharm-cant-find-spacy-model-en
~/PycharmProjects/pythonProject/venv/bin/python -m spacy download en
~/PycharmProjects/pythonProject/venv/bin/python -m spacy download es_core_news_sm
~/PycharmProjects/pythonProject/venv/bin/python -m spacy download es_core_news_md
~/PycharmProjects/pythonProject/venv/bin/python -m spacy download es_core_news_lg
~/PycharmProjects/pythonProject/venv/bin/python -m spacy download es_dep_news_trf

# wget https://raw.githubusercontent.com/tylerneylon/explacy/master/explacy.py
```



## Corpus de Spacy

```
es_core_news_lg
---------------
Spanish pipeline optimized for CPU. Components: tok2vec, morphologizer, parser, senter, ner, attribute_ruler, lemmatizer.
Components: 
    [v] tok2vec
    morphologizer
    parser
    [v] senter
    [v] ner
    attribute_ruler
    lemmatizer.

es_dep_news_trf
---------------
Spanish transformer pipeline (dccuchile/bert-base-spanish-wwm-cased). Components: transformer, morphologizer, parser, attribute_ruler, lemmatizer.
Components:
    [x] transformer
    morphologizer
    parser
    attribute_ruler
    lemmatizer.
```

