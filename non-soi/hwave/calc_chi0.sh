#!/bin/sh

calc_chi0(){
    mkdir $1GPa
    cd $1GPa
    cp -rf ../../$1GPa/dir-model .    
    cp ../ref/input_chi.toml .
    hwave input_chi.toml
    cd ..
    }


calc_chi0 0
calc_chi0 1.08
calc_chi0 1.56
calc_chi0 2.22
calc_chi0 2.62
calc_chi0 3.02
calc_chi0 3.69
calc_chi0 4.04
calc_chi0 4.45
calc_chi0 5.12
calc_chi0 5.65
calc_chi0 6.13
calc_chi0 7.51
calc_chi0 8.19



