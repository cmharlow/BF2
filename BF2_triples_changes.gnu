set title "BIBFRAME2.0 changes by date"
set border
set grid
set tics in
set ticslevel 0.5

set xlabel "Date"
set timefmt "%Y-%m-%d"
set format x "%Y-%m"
set xdata time
set xrange ["2016-03-28" : "2017-04-13"]
set boxwidth 150000 absolute  # a bit over a day

set ylabel "Fraction of triples changed (%)"
set yrange [-28 : 35]
set ytics 10

set terminal png
set output 'BF2_triples_changes.png'

plot "BF2_triples_changes.dat" using 1:(100.0*$3/$2) title "added triples" with boxes fs solid 0.7 lc rgb "#11AA00", "BF2_triples_changes.dat" using 1:(-100.0*$4/$2) title "deleted triples" with boxes fs solid 0.7 lc rgb "#AA1100"
