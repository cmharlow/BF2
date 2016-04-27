import rdflib
from rdflib.namespace import DCTERMS
from gittle import Gittle
import os

bf2url = 'http://id.loc.gov/ontologies/bibframe.rdf'
bfURI = 'http://id.loc.gov/ontologies/bibframe/'

repo_path = '.'
repo_url = 'git@github.com:cmh2166/BF2.git'
repo = Gittle(repo_path, origin_uri=repo_url)
key_file = open(os.environ['PRIVATE_KEY_DIR'])
repo.auth(pkey=key_file)


def writeBF2(graph):
    """Grab most recent BF2 spec from id.loc.gov, serialize for comparison."""
    graph.serialize('BF2specs/bibframe2.rdf', format='pretty-xml')
    graph.serialize('BF2specs/bibframe2.nt', format='nt')
    graph.serialize('BF2specs/bibframe2.ttl', format='turtle')


def diffDate(oldBF, newBF):
    oldBFdate = oldBF.value(rdflib.URIRef(bfURI), DCTERMS.modified).toPython()
    newBFdate = newBF.value(rdflib.URIRef(bfURI), DCTERMS.modified).toPython()
    if oldBFdate == newBFdate:
        return(False, None)
    else:
        return(True, newBFdate)


def main():
    """Grab Bibframe 2 RDF spec from id.loc.gov hourly, check for diffs."""
    # Get any changes made directly to GitHub BF2 repo first.
    repo.pull()

    # Get the most recent BF2 Spec from id.loc.gov
    newbf2rdf = rdflib.Graph().parse(bf2url)
    oldbf2rdf = rdflib.Graph().parse('BF2specs/bibframe2.rdf')

    # Check dcterm:modified date of currently stored BF2, new BF2 specs
    (updates, date) = diffDate(oldbf2rdf, newbf2rdf)

    # If the date modified values are different, overwrite the files locally
    if updates:
        writeBF2(newbf2rdf)
        # Stage, Commit and Push any changes
        repo.stage('BF2specs/*')
        repo.commit(name='Christina Harlow', email='cmharlow@gmail.com',
                    message='pulling latest BF2 updates of: ' + str(date))
        repo.push()


if __name__ == '__main__':
    main()
