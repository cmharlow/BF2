import rdflib
from rdflib.namespace import DCTERMS
from git import Repo
import os
from apscheduler.schedulers.blocking import BlockingScheduler
import argparse

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=60)
def scheduled_job():
    main()

bf2url = 'http://id.loc.gov/ontologies/bibframe.rdf'
bfURI = 'http://id.loc.gov/ontologies/bibframe/'


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
        oldBFdate = oldBFdate.toPython()
    newBFdate = newBF.value(rdflib.URIRef(bfURI), DCTERMS.modified).toPython()
    if oldBFdate == newBFdate:
        return(False, None)
    else:
        return(True, newBFdate)


def main():
    """Grab Bibframe 2 RDF spec from id.loc.gov, check for diffs."""
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
        print(message)
        index.commit(message)
        o.push()
    else:
        print('No updates captured.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process BF2 manually or \
                                     through scheduler.')
    parser.add_argument("-s", "--sched", action="store_true", dest="sched",
                        default=False, help="use scheduler to run")
    parser.add_argument("-m", "--man", action="store_true", dest="man",
                        default=False, help="run manually")
    parser.add_argument("-r", "--repo", dest="repo",
                        default="/Users/Christina/Projects/BF2",
                        help="repo working directory")

    args = parser.parse_args()

    if os.path.isfile('.git/config.lock'):
        os.remove('.git/config.lock')
    repo = Repo(args.repo)
    config = repo.config_writer()
    config.set_value("user", "email", "cmharlow@gmail.com")
    config.set_value("user", "name", "cmh2166")
    index = repo.index

    if not args.sched and not args.man:
        parser.print_help()
        exit()
    elif args.man:
        main()
    elif args.sched:
        sched.start()
        sched.shutdown(wait=True)
