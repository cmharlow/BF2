import rdflib

bf2url = 'http://id.loc.gov/ontologies/bibframe.rdf'

bf2rdf = rdflib.Graph().parse(bf2url)
bf2rdf.serialize('BF2specs/bibframe2.rdf', format='pretty-xml')
bf2rdf.serialize('BF2specs/bibframe2.nt', format='nt')
bf2rdf.serialize('BF2specs/bibframe2.ttl', format='turtle')

