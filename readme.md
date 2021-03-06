## Formalización semántica e inferencia computacional

Trabajo realizado para culminar el grado de Lingüística y lenguas aplicadas impartido en la Universidad Complutense de Madrid (UCM) realizado durante el periodo 2017-2021.

### Resumen del trabajo (teórico y práctico)

Se exponen aquí ciertas herramientas conceptuales y modelos para la formalización de las expresiones lingüísticas. La aproximación teórica es complementada por un prototipo computacional que analiza, de una manera simplificada, el significado de una oración o microtexto; tal aproximación permite modelar este proceso y descubrir las dificultades de una manera inmediata. El resultado de este análisis es un grafo semántico que es posteriormente ampliado mediante una base de conocimiento basándose, principalmente, en relaciones semánticas formalizadas como implicaciones (postulados del significado en Carnap, 1952) para representar el conocimiento explicitado por la oración y el implícito que resulta de integrar este en el sistema.

El prototipo realizado es un modelo para trazar computacionalmente parte de los procesos de comprensión humana del lenguaje. El flujo del programa comienza por una entrada: un texto u oración; a continuación formaliza sus predicados y a partir de estos infiere información nueva a través de una base de conocimiento.

![Flujo programa](./img/app_flow.png)

## App diagrams

### Modules

![Diagrama aplicación1](./img/modules.png)

### Classes

![Diagrama aplicación2](./img/graph.png)



![Diagrama aplicación3](./img/edges&nodes.png)

## Dependencies setup

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

## Spanish spacy corpora

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

