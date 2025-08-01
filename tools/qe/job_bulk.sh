#!/bin/sh
#SBATCH -J icl2_qe
#SBATCH -p F144cpu
#SBATCH --time=24:00:00
#SBATCH -N 144
#SBATCH -n 288
#SBATCH -c 64
#SBATCH -o log.%j
#SBATCH -e log.%j
#SBATCH --exclusive
#SBATCH --mem-per-cpu=1840
ulimit -s unlimited
KMP_STACKSIZE=1g
export KMP_STACKSIZE
source /home/issp/materiapps/intel/respack/respackvars.sh
date

source  /home/issp/materiapps/intel/espresso/espressovars.sh
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}


run_job_scf() {
    local dir=$1
    cd "./$dir"
    srun --exclusive -N 16 -n 64 -c 32 --mem-per-cpu=1840 pw.x -nk 8 -in scf.in > scf.out &
    cd - >/dev/null
}

run_job_band() {
    local dir=$1
    cd "./$dir"
    srun --exclusive -N 16 -n 64 -c 32 --mem-per-cpu=1840 pw.x -nk 8 -in band.in > band.out &
    cd - >/dev/null
}


run_job_bands() {
    local dir=$1
    cd "./$dir"
    srun -n 1 -c 128 -N 1 --exclusive --mem-per-cpu=1840 bands.x -in bands.in > bands.out &
    cd - >/dev/null
}


run_job_nscf() {
    local dir=$1
    cd "./$dir"
    srun --exclusive -N 16 -n 64 -c 32 --mem-per-cpu=1840 pw.x -nk 8 -in nscf.in > ncf.out &
    cd - >/dev/null
}

dirs=(
    "0GPa"
    "0_cellGPa"
    "1.10GPa"
    "1.89GPa"
    "10.12GPa"
    "10.96GPa"
    "10.9GPa"
    "11.86GPa"
    "3.36GPa"
    "4.83GPa"
    "6.33GPa"
    "7.37GPa"
    "7.71GPa"
    "8.30GPa"
    "8.57GPa"
    "9.38GPa"
    "9.64GPa"
)

for dir in "${dirs[@]}"; do
    run_job_scf "$dir"
done

wait

for dir in "${dirs[@]}"; do
    run_job_band "$dir"
done

wait

for dir in "${dirs[@]}"; do
    run_job_bands "$dir"
done

wait

for dir in "${dirs[@]}"; do
    run_job_nscf "$dir"
done

wait

date
