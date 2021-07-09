import sys
import json
from collections import defaultdict

def create_verb_forms_dict():
    my_dict = defaultdict(list)
    """
    derrumbó VMIS3S0
    des d NCFP000 VMSP2S0
    """
    with open('lista 06-verbos.txt', 'r') as f:
        for line in f.readlines():
            # print(line)
            k, v = line.split()
            my_dict[k].append(v)

    print(my_dict)

    with open('verbs_es.json', 'w') as f:
        # Para guardar los datos en el archivo abierto en modo escritura, basta con usar el método dump.
        # Cuando se guardan datos con json, el archivo creado se puede abrir con un editor de texto y ver el
        # contenido. De ahí que si los datos a guardar incluyen strings que puedan tener caracteres que no
        # sean ASCII (caracteres típicos de la lengua inglesa), por defecto json no guarda esos caracteres
        # sino que guarda un código (formado por caracteres ASCII). Como no tenemos problemas en guardar
        # caracteres "especiales" (vocales con tildes, eñes, aperturas de interrogación y exclamación...),
        # ponemos el parámetro ensure_ascii a False.
        json.dump(my_dict, f, ensure_ascii=False)


create_verb_forms_dict()
sys.exit(0)
