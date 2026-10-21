import sys
from rdflib import Graph, Literal, URIRef
from urllib.parse import urlsplit

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} inputFile outputFile")
    sys.exit(1)

idProp = URIRef('https://vocabs.acdh.oeaw.ac.at/schema#hasIdentifier')
titleProp = URIRef('https://vocabs.acdh.oeaw.ac.at/schema#hasTitle')

dataset = Graph()
dataset.parse(sys.argv[1], format='turtle')

with open(sys.argv[2], 'w', encoding='utf8') as output:
    for sbj, prop, obj in dataset:
        sbj = urlsplit(prop).path

        prop = urlsplit(prop).fragment
        prop = prop.replace('has', 'has ').replace('isPart', 'is part ').replace('By', ' by')
        prop = prop.lower();

        if isinstance(obj, Literal):
            obj = str(obj)
        else:
            try:
                _, _, obj = next(dataset.triples((obj, titleProp, None)))
            except StopIteration:
                obj = str(obj)

        output.write(f"{sbj} {prop} {obj}.\n")

