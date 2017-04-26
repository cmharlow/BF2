#!/usr/bin/env python3
"""Look at BF2 version repository to understand churn."""
import datetime
import logging
import optparse
import os.path
import subprocess
import tempfile


def clone_repo(repo_uri, tmp_dir):
    """Clone repo from given URI into tmp_dir.

    Return temporary directory of git repo.
    """
    repo_dir = os.path.join(tmp_dir, 'repo')
    logging.info("Cloning into %s" % (repo_dir))
    subprocess.run(['git', 'clone', '-q', repo_uri, repo_dir], check=True)
    return(repo_dir)


def get_commit_ids(repo_dir):
    """Get a dict of commit ids by date.

    Parsed outout from git log following:

    >git log --pretty="format:%H %ai" BF2specs/bibframe2.nt
    04f3121ac8a9e45ee2c147897c8a4e0cca91d498 2016-05-16 13:22:23 -0400
    4d11c56bd030b17d0d3c3d68e4a6768a9ea704f2 2016-05-06 10:29:58 -0400
    ...
    """
    with subprocess.Popen(
            'cd %s; git log --pretty="format:%%H %%ai" BF2specs/bibframe2.nt'
            % (repo_dir),
            stdout=subprocess.PIPE, shell=True) as proc:
        log = proc.stdout.read().decode('utf-8')
    # Get dict of last commit for each day
    commits = {}
    last_cid = None
    last_date = None
    for line in reversed(log.split('\n')):
        (cid, date, time, tz) = line.split()
        if (last_date is not None and last_date != date):
            # Record last data
            commits[last_date] = last_cid
        last_date = date
        last_cid = cid
    # ...and last one must be last commit on that date
    commits[last_date] = last_cid
    return commits


def get_bf(repo_dir, filename, cid):
    """Get the bibframe triples from git as a list of lines."""
    subprocess.run('cd %s; git checkout -q %s' % (repo_dir, cid),
                   shell=True)
    filename = os.path.join(repo_dir, filename)
    triples = open(filename).read().split('\n')
    return triples


def compare_lists(a, b):
    """Compare lists, return counts of entries in both, a_only, b_only."""
    both = 0
    a_only = 0
    b_only = 0
    ab = set(a) | set(b)
    for entry in ab:
        if (entry in a):
            if (entry in b):
                both += 1
            else:
                a_only += 1
        elif (entry in b):
            b_only += 1
    return(both, a_only, b_only)


def date_inc(date, days):
    """Return string date which is date + days."""
    dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    dt = dt + datetime.timedelta(days=days)
    return dt.date()


GNUPLOT = '''set title "BIBFRAME2.0 changes by date"
set border
set grid
set tics in
set ticslevel 0.5

set xlabel "Date"
set timefmt "%Y-%m-%d"
set format x "%Y-%m"
set xdata time
set xrange ["{start_date}" : "{end_date}"]
set boxwidth 150000 absolute  # a bit over a day

set ylabel "Fraction of triples changed (%)"
set yrange [-{max_deleted} : {max_added}]
set ytics 10

set terminal png
set output '{graphfile}'

plot \
"{datafile}" using 1:(100.0*$3/$2) \
title "added triples" with boxes fs solid 0.7 lc rgb "#11AA00", \
"{datafile}" using 1:(-100.0*$4/$2) \
title "deleted triples" with boxes fs solid 0.7 lc rgb "#AA1100"
'''


p = optparse.OptionParser(description='BF2 change tracking tool',
                          usage='usage: %prog [options] (-h for help)')
p.add_option('--datafile', default='BF2_triples_changes.dat',
             help='data file to write to [default %default]')
p.add_option('--gnufile', default='BF2_triples_changes.gnu',
             help='gnuplot file to write to [default %default]')
p.add_option('--graphfile', default='BF2_triples_changes.png',
             help='graph file to write to [default %default]')
p.add_option('--no-graph', '-g', action='store_true',
             help='do not run gnuplot to make graph')
p.add_option('--verbose', '-v', action='store_true',
             help='verbose')
(opts, args) = p.parse_args()

logging.basicConfig(level=logging.INFO if opts.verbose else logging.WARN)

# Compare by last commit of the day on day when there are
# changes, write out a datafile of the numbers of triples
# (lines in BF2specs/bibframe2.nt) that are present and have
# been added/deleted.
#
earliest_date = "2099-01-01"
lateest_date = "2001-01-01"
max_deleted = 0
max_added = 0
with tempfile.TemporaryDirectory() as tmp_dir:
    repo_dir = clone_repo('https://github.com/cmh2166/BF2.git', tmp_dir)
    commits = get_commit_ids(repo_dir)
    with open(opts.datafile, 'w') as dfh:
        last_bf = None
        dfh.write("# Number of changes BF ontology (from ntriples lines)\n")
        dfh.write("#date     same added deleted (wrt previous version)  num\n")
        for date in sorted(commits.keys()):
            cid = commits[date]
            logging.info("Looking at commit %s -> %s" % (date, commits[date]))
            bf = get_bf(repo_dir, 'BF2specs/bibframe2.nt', cid)
            if (last_bf is None):
                earliest_date = date
            else:
                (same, deleted, added) = compare_lists(last_bf, bf)
                max_deleted = max(deleted / same, max_deleted)
                max_added = max(added / same, max_added)
                dfh.write("%10s  %8d %8d %8d  %8d\n" %
                          (date, same, added, deleted, len(bf)))
            last_bf = bf
            latest_date = date

# Run gnuplot and make a new graph
if (not opts.no_graph):
    with open(opts.gnufile, 'w') as gfh:
        gfh.write(GNUPLOT.format(datafile=opts.datafile,
                                 graphfile=opts.graphfile,
                                 start_date=date_inc(earliest_date, -30),
                                 end_date=date_inc(latest_date, 30),
                                 max_deleted=int(max_deleted * 120),
                                 max_added=int(max_added * 120)))
    subprocess.run('gnuplot %s' % (opts.gnufile), shell=True)
