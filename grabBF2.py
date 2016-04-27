import rdflib
from rdflib.namespace import DCTERMS
from git import Repo

bf2url = 'http://id.loc.gov/ontologies/bibframe.rdf'
bfURI = 'http://id.loc.gov/ontologies/bibframe/'

repo = Repo('/Users/Christina/Projects/BF2')
assert not repo.bare
config = repo.config_writer()
config.set_value("user", "email", "cmharlow@gmail.com")
config.set_value("user", "name", "cmh2166")
index = repo.index


def writeBF2(graph):
    """Grab most recent BF2 spec from id.loc.gov, serialize for comparison."""
    graph.serialize('BF2specs/bibframe2.rdf', format='pretty-xml')
    graph.serialize('BF2specs/bibframe2.nt', format='nt')
    graph.serialize('BF2specs/bibframe2.ttl', format='turtle')


def diffDate(oldBF, newBF):
    oldBFdate = oldBF.value(rdflib.URIRef(bfURI), DCTERMS.modified)
    if not oldBFdate:
        for obj in oldBF.objects((None, DCTERMS.modified)):
            oldBFdate = obj.toPython()
    else:
        oldBFdate = oldBF.toPython()
    newBFdate = newBF.value(rdflib.URIRef(bfURI), DCTERMS.modified).toPython()
    if oldBFdate == newBFdate:
        return(False, None)
    else:
        return(True, newBFdate)


def main():
    """Grab Bibframe 2 RDF spec from id.loc.gov hourly, check for diffs."""
    # Get any changes made directly to GitHub BF2 repo first.
    o = repo.remotes.origin
    o.pull()

    # Get the most recent BF2 Spec from id.loc.gov
    newbf2rdf = rdflib.Graph().parse(bf2url)
    oldbf2rdf = rdflib.Graph().parse('BF2specs/bibframe2.rdf')

    # Check dcterm:modified date of currently stored BF2, new BF2 specs
    (updates, date) = diffDate(oldbf2rdf, newbf2rdf)

    # If the date modified values are different, overwrite the files locally
    if updates:
        writeBF2(newbf2rdf)
        # Stage, Commit and Push any changes
        index.add(['BF2specs'])
        message = 'BF2 spec changes of: ' + str(date)
        index.commit(message)


if __name__ == '__main__':
    main()
