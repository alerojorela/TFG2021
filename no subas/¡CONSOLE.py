import sys
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Extrae los predicados de una oración o texto.')
    # INPUT
    """ DISPLAY FORMAT
        latex
        dot
        dotweb
    """
    # parser.add_argument('--dot', action='store_true', help='devuelve grafos en formato dot (graphviz)')
    # parser.add_argument('--dotweb', action='store_true',
    #                     help='Visualiza los grafos en la página https://dreampuf.github.io/GraphvizOnline/')
    """ DISPLAY INFO
        spacy and output [always]
        pattern
        predicate
    """
    # positional
    parser.add_argument('-t', '--text', nargs=1, metavar='text', type=str, help='oración o texto a procesar')
    # optional
    # parser.add_argument('-e', '--evaluation', action='store_true', help='')
    parser.add_argument('-s', '--samples', action='store_true', help='')
    parser.add_argument('-nc', '--no-coreference', action='store_false', help='no analiza la correferencia')
    parser.add_argument('-ni', '--no-inference', action='store_false', help='no realiza inferencias')
    # Namespace(no_inference=False, no_coreference=False, samples=False, text='papar itrip')

    args = parser.parse_args()
    # print(args)

    if args.samples:
        text = 'El trueno resonó en el valle.'
        text = 'En la colina había una casa de piedra. La casa era grande.'
    elif args.text:
        text = args.text[0]
    else:
        parser.error("One argument is required!")
        sys.exit(1)

    print(text)
