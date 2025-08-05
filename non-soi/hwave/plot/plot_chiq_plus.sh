set xtics 32
set size 0.25,0.5
X = 32
M = 64
set yrange [0:1.5]
set arrow from 32, 0 to 32, 1.49 nohead lw 1 dt (10, 5)
set arrow from 64, 0 to 64, 1.49 nohead lw 1 dt (10, 5)
plot "0GPa/chi0q_line.dat" u 1 w l, "1GPa/chi0q_line.dat" u 1 w l, "2.05GPa/chi0q_line.dat" u 1 w l, "2.945GPa/chi0q_line.dat" u 1 w l, "4.405GPa/chi0q_line.dat" u 1 w l, "8.05GPa/chi0q_line.dat" u 1 w l
set term postscript eps enhanced color
set output "chiq_plus.eps"
replot
exit
