"""バンド構造をWannierバンドと共にプロットする

このスクリプトは、Quantum ESPRESSOのバンド計算結果とWannier90のバンド計算結果を
同一のプロット上に表示します。

Parameters
----------
なし

Returns
-------
なし

Notes
-----
入力ファイル
----------
pressure_cif.dat : 圧力値のリストを含むファイル
    各行に圧力値(GPa)が記載されている

{pressure}GPa/icl2.band.gnu : QEのバンド計算結果
    pressure : 圧力値(GPa)

{pressure}GPa/dir-wan/dat.iband : Wannier90のバンド計算結果
    pressure : 圧力値(GPa)

{pressure}GPa/icl2.save/data-file-schema.xml : QEの出力XMLファイル
    pressure : 圧力値(GPa)
    フェルミエネルギーの取得に使用

出力ファイル
----------
band/{pressure}GPa_band.pdf : バンド構造のプロット
    pressure : 圧力値(GPa)
    QEのバンド(点線)とWannierバンド(実線)を重ねて表示

band/band_plot_wan_all.gnu : gnuplotスクリプト
    全圧力のバンド構造をプロットするためのスクリプト
"""

import subprocess
import os
import tomli
import glob
import numpy as np

with open("pressure_cif.dat", "r") as fr:
    lines = fr.readlines()

os.makedirs("band", exist_ok=True)

def get_fermi_energy(file_name):
    """Quantum ESPRESSOの出力XMLファイルからフェルミエネルギーを取得する

    Parameters
    ----------
    file_name : str
        data-file-schema.xmlファイルのパス

    Returns
    -------
    float
        フェルミエネルギー(eV)
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(file_name)
    root = tree.getroot()
    from scipy import constants
    for name in root.iter('fermi_energy'):
        fermi_energy = float(name.text) * constants.physical_constants["Hartree energy in eV"][0]
    return fermi_energy


str_gnuplot = "set yrange[-1.2:0.5]\n"
for line in lines:
    words = line.split()
    output_file_folder = "{}GPa".format(words[1])
    command = ["cp", os.path.join(output_file_folder, "icl2.band.gnu"), os.path.join("band", "{}.band.gnu".format(words[1]))]
    subprocess.run(command)
    ene_f = get_fermi_energy(os.path.join(output_file_folder, "icl2.save", "data-file-schema.xml"))
    with open(os.path.join(output_file_folder, "icl2.band.gnu"), "r") as fr:
        lines_iband = fr.readlines()
    k_max = lines_iband[-2].split()[0]
    command = ["cp", os.path.join(output_file_folder, "dir-wan", "dat.iband"), os.path.join("band", "{}.dat.iband".format(words[1]))]
    subprocess.run(command)
    str_gnuplot += "set terminal pdf enhanced color\n"
    str_gnuplot += "set output '{}_band.pdf'\n".format(output_file_folder)
    str_gnuplot += "plot '{}.band.gnu' using ($1/{}):($2-{}) w lp, '{}.dat.iband' using 1:($2-{})\n".format(words[1], k_max, ene_f, words[1], ene_f)
with open(os.path.join("band", "band_plot_wan_all.gnu"), "w") as fw:
    fw.write(str_gnuplot)
