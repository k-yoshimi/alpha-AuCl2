#!/bin/sh

calc_fs(){
    mkdir $1GPa
    cd $1GPa
    cp -rf ../../$1GPa/dir-model .    
    cp ../0GPa/input.toml .
    hwave input.toml
    python3 ../calc_fs_2d.py --p $1
    cd ..
    }

calc_fs 0
calc_fs 1
calc_fs 1.5
calc_fs 2.05
calc_fs 2.555
calc_fs 2.945
calc_fs 3.675
calc_fs 4.405
calc_fs 5.1
calc_fs 5.78
calc_fs 6.46
calc_fs 6.945
calc_fs 7.49
calc_fs 8.05



