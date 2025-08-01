#!/bin/sh
#SBATCH -J 3.17GPa
#SBATCH -p F144cpu
#SBATCH --time=24:00:00
#SBATCH -N 144
#SBATCH -n 288
#SBATCH -c 64
#SBATCH -o log.%j
#SBATCH -e log.%j
#SBATCH --exclusive
ulimit -s unlimited
KMP_STACKSIZE=1g
export KMP_STACKSIZE
source /home/issp/materiapps/intel/respack/respackvars.sh
date
srun calc_chiqw < respack.in > chiqw.out
calc_w3d < respack.in > calc_w3d.out
calc_j3d < respack.in > calc_j3d.out
date
