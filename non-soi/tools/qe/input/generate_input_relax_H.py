"""Quantum Espressoの構造最適化入力ファイルを生成する

このスクリプトは、CIFファイルからQuantum Espressoの構造最適化計算用の
入力ファイルを生成します。水素原子の位置のみを最適化対象とします。

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
input.toml : 計算パラメータの設定ファイル
    計算に必要な各種パラメータが記載されたTOMLファイル
    
*.cif : 結晶構造ファイル
    最適化したい結晶構造のCIFファイル

出力ファイル
----------
scf.in.ref : 参照入力ファイル
    cif2cellで生成された基本的な入力ファイル
    
scf_relax.in : 構造最適化用の入力ファイル
    水素原子のみを最適化対象とした計算用の入力ファイル
    ATOMIC_POSITIONSブロックで水素原子の座標のみが可変に設定される

See Also
--------
cif2cell : CIFファイルから各種第一原理計算コード用の入力ファイルを生成するツール
"""

import subprocess
import os
import tomli


def generate_base_file(file_name, output_file_folder):
    """cif2cellを使用して基本入力ファイルを生成する

    Parameters
    ----------
    file_name : str
        CIFファイルのパス
    output_file_folder : str
        出力先フォルダのパス

    Returns
    -------
    なし
    """
    os.makedirs(output_file_folder, exist_ok = True)
    os.chdir(output_file_folder)
    command = ["cif2cell", os.path.join(file_name), "-p", "quantum-espresso", "--pwscf-pseudostring=_ONCV_PBE-1.2.upf", "-o", "scf.in.ref", "--no-reduce"]
    subprocess.run(command)

def modify_relax(ref_file_name, output_file_folder, info):
    """構造最適化用の入力ファイルを生成する

    Parameters
    ----------
    ref_file_name : str
        参照入力ファイルのパス
    output_file_folder : str
        出力先フォルダのパス
    info : dict
        計算パラメータの辞書

    Returns
    -------
    なし
    """
    os.chdir(output_file_folder)
    with open(ref_file_name, "r") as fr:
        lines = fr.readlines()

    with open("scf_relax.in", "w") as fw:
        header_lines = 9
        for line in lines[:header_lines]:
            fw.write(line)
        #print control info
        fw.write("&CONTROL\n")
        for key, value in info["control"].items():
            fw.write("  {}={}\n".format(key, value))
        fw.write("/ \n")
        iflg_ATOMIC = False
        for line in lines[header_lines:]:
            if line.split()[0].strip() == "ATOMIC_POSITIONS":
                iflg_ATOMIC = True
                fw.write(line)
                continue
            if iflg_ATOMIC is True:
                if line.split()[0].strip()  == "H":
                    fw.write("{} {} {} {}\n".format(line.strip(), 1, 1, 1))
                else:
                    fw.write("{} {} {} {}\n".format(line.strip(), 0, 0, 0))
                continue
            fw.write(line)
            if line.split("=")[0].strip() == "ntyp":
                for key, value in info["system"].items():
                    fw.write("  {}={}\n".format(key, value))
                fw.write("/ \n")    
                fw.write("&electrons\n")
                for key, value in info["electrons"].items():
                    fw.write("  {}={}\n".format(key, value))
                fw.write("/\n")
                fw.write("&ions\n")
        fw.write("K_POINTS {automatic}\n")
        str_k = ""
        for value in info["k_points"]["k_points"]:
            str_k += "{} ".format(value)
        fw.write(str_k+"\n")
    os.chdir("../")
    
path_to_input = "input.toml"
with open(path_to_input, "rb") as f:
    tomli_dict = tomli.load(f)

#Set default dirs
for key in ["scf", "relax", "nscf", "band"]:
    for base_key, value in tomli_dict["base"].items():
        tomli_dict[key][base_key] = tomli_dict[key].get(base_key, value)
        for base_sec_key, value in tomli_dict["base"][base_key].items():
            print(key, base_key, base_sec_key, value)
            tomli_dict[key][base_key][base_sec_key] = tomli_dict[key][base_key].get(base_sec_key, value)
        

file_name = "2433895.cif".format(key)
output_file_folder = "./"
print(file_name, output_file_folder)
generate_base_file(file_name, output_file_folder)
modify_relax("scf.in.ref", output_file_folder, tomli_dict["relax"])
