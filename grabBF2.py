import rdflib

bf2url = 'http://id.loc.gov/ontologies/bibframe.rdf'

bf2rdf = rdflib.Graph().parse(bf2url)
bf2rdf.serialize('specs/bibframe2.xml', format='xml')
bf2rdf.serialize('specs/bibframe2.nt', format='nt')
bf2rdf.serialize('specs/bibframe2.ttl', format='turtle')
