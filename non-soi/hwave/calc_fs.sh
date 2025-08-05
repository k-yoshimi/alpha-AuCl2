#!/bin/sh

calc_fs(){
    hwave input.toml
    python3 calc_fs_2d.py
    }

calc_fs 


