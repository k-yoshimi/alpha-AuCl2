"""RESPACKの入力ファイルを生成する

このスクリプトは、Quantum ESPRESSOの計算結果からRESPACKの入力ファイルを生成します。
フェルミエネルギーをQuantum ESPRESSOの出力から取得し、エネルギーウィンドウを設定します。

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

respack.in.ref : RESPACKの入力ファイルのテンプレート
    Lower_energy_window, Upper_energy_windowの値が置換される

出力ファイル
----------
{pressure}GPa/respack.in : 各圧力値に対するRESPACKの入力ファイル
    pressure : 圧力値(GPa)
"""

import subprocess
import os
import glob
    
with open("pressure_cif.dat", "r") as fr:
    lines = fr.readlines()

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

def generate_respack_in(fermi_ene, output_file_folder):
    """RESPACKの入力ファイルを生成する

    Parameters
    ----------
    fermi_ene : float
        フェルミエネルギー(eV)
    output_file_folder : str
        出力ディレクトリのパス

    Returns
    -------
    なし
    """
    os.chdir(output_file_folder)
    str_respack = ""
    window_range = [-1.2, 0.6]
    with open("../respack.in.ref", "r") as fr:
        lines = fr.readlines()
    for line in lines:
        if line.split("=")[0] == "Lower_energy_window":
            str_respack += "Lower_energy_window={},\n".format(fermi_ene+window_range[0]) 
        elif line.split("=")[0] == "Upper_energy_window":
            str_respack += "Upper_energy_window={},\n".format(fermi_ene+window_range[1])
        else:
            str_respack += line
    with open("respack.in", "w") as fw:
        fw.write(str_respack)
    os.chdir("../")
    
for line in lines:
    words = line.split()
    output_file_folder = "{}GPa".format(words[1])
    ene_f = get_fermi_energy(os.path.join(output_file_folder, "icl2.save", "data-file-schema.xml"))
    generate_respack_in(ene_f, output_file_folder)   
