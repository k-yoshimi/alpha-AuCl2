"""Quantum Espressoの入力ファイルを生成する

このスクリプトは、基準となる入力ファイルから各種計算用の入力ファイルを生成します。
SCF計算、非SCF計算、バンド計算用の入力ファイルを作成します。

Parameters
----------
なし

Returns
-------
なし

Notes
-----
入力ファイル
-----------
input.toml : 計算パラメータの設定ファイル
    計算に必要な各種パラメータが記載されたTOMLファイル
    
scf.in.ref : 基準となる入力ファイル
    cif2cellで生成された基本的な入力ファイル

出力ファイル
-----------
scf.in : SCF計算用入力ファイル
    SCF計算用のパラメータが設定された入力ファイル

nscf.in : 非SCF計算用入力ファイル
    非SCF計算用のパラメータが設定された入力ファイル

band.in : バンド計算用入力ファイル
    バンド計算用のパラメータとk点パスが設定された入力ファイル

bands.in : バンド後処理用入力ファイル
    バンド構造の後処理用のパラメータが設定された入力ファイル

See Also
--------
cif2cell : CIFファイルから各種第一原理計算コード用の入力ファイルを生成するツール
"""

import subprocess
import os
import tomli
import glob
    
def modify_scf(ref_file_name, output_file_folder, info, cur_dir):
    """SCF計算用の入力ファイルを生成する

    Parameters
    ----------
    ref_file_name : str
        基準となる入力ファイル名
    output_file_folder : str
        出力先フォルダのパス
    info : dict
        計算パラメータの辞書
    cur_dir : str
        現在のディレクトリパス

    Returns
    -------
    なし
    """
    os.chdir(output_file_folder)
    with open(ref_file_name, "r") as fr:
        lines = fr.readlines()

    with open("scf.in", "w") as fw:
        header_lines = 9
        for line in lines[:header_lines]:
            fw.write(line)
        #print control info
        fw.write("&CONTROL\n")
        for key, value in info["control"].items():
            fw.write("  {}={}\n".format(key, value))
        fw.write("/ \n")
        for line in lines[header_lines:]:
            fw.write(line)
            if line.split("=")[0].strip() == "ntyp":
                for key, value in info["system"].items():
                    fw.write("  {}={}\n".format(key, value))
                fw.write("/ \n")    
                fw.write("&electrons\n")
                for key, value in info["electrons"].items():
                    fw.write("  {}={}\n".format(key, value))
        fw.write("K_POINTS {automatic}\n")
        str_k = ""
        for value in info["k_points"]["k_points"]:
            str_k += "{} ".format(value)
        fw.write(str_k+"\n")
    os.chdir(cur_dir)

def modify_nscf(ref_file_name, output_file_folder, info, cur_dir):
    """非SCF計算用の入力ファイルを生成する

    Parameters
    ----------
    ref_file_name : str
        基準となる入力ファイル名
    output_file_folder : str
        出力先フォルダのパス
    info : dict
        計算パラメータの辞書
    cur_dir : str
        現在のディレクトリパス

    Returns
    -------
    なし
    """
    os.chdir(output_file_folder)
    with open(ref_file_name, "r") as fr:
        lines = fr.readlines()

    with open("nscf.in", "w") as fw:
        header_lines = 9
        for line in lines[:header_lines]:
            fw.write(line)
        #print control info
        fw.write("&CONTROL\n")
        for key, value in info["control"].items():
            fw.write("  {}={}\n".format(key, value))
        fw.write("/ \n")
        for line in lines[header_lines:]:
            fw.write(line)
            if line.split("=")[0].strip() == "ntyp":
                for key, value in info["system"].items():
                    fw.write("  {}={}\n".format(key, value))
                fw.write("/ \n")    
                fw.write("&electrons\n")
                for key, value in info["electrons"].items():
                    fw.write("  {}={}\n".format(key, value))
        fw.write("K_POINTS {automatic}\n")
        str_k = ""
        for value in info["k_points"]["k_points"]:
            str_k += "{} ".format(value)
        fw.write(str_k+"\n")
    os.chdir(cur_dir)

def modify_band(ref_file_name, output_file_folder, info, cur_dir):
    """バンド計算用の入力ファイルを生成する

    Parameters
    ----------
    ref_file_name : str
        基準となる入力ファイル名
    output_file_folder : str
        出力先フォルダのパス
    info : dict
        計算パラメータの辞書
    cur_dir : str
        現在のディレクトリパス

    Returns
    -------
    なし
    """
    os.chdir(output_file_folder)
    with open(ref_file_name, "r") as fr:
        lines = fr.readlines()

    with open("band.in", "w") as fw:
        header_lines = 9
        for line in lines[:header_lines]:
            fw.write(line)
        #print control info
        fw.write("&CONTROL\n")
        for key, value in info["control"].items():
            fw.write("  {}={}\n".format(key, value))
        fw.write("/ \n")
        for line in lines[header_lines:]:
            fw.write(line)
            if line.split("=")[0].strip() == "ntyp":
                for key, value in info["system"].items():
                    fw.write("  {}={}\n".format(key, value))
                fw.write("/ \n")    
                fw.write("&electrons\n")
                for key, value in info["electrons"].items():
                    fw.write("  {}={}\n".format(key, value))
        fw.write("K_POINTS {crystal_b}\n")
        fw.write(" {}\n".format(info["k_points"]["k_points"]))
        str_k = info["k_points"]["k_path"]
        fw.write(str_k+"\n")
    os.chdir(cur_dir)

def write_bands(output_file_folder, info, cur_dir):
    """バンド後処理用の入力ファイルを生成する

    Parameters
    ----------
    output_file_folder : str
        出力先フォルダのパス
    info : dict
        計算パラメータの辞書
    cur_dir : str
        現在のディレクトリパス

    Returns
    -------
    なし
    """
    os.chdir(output_file_folder)
    prefix = info["control"]["prefix"]
    with open("bands.in", "w") as fw:
        fw.write("&BANDS\n")
        fw.write("prefix={}\n".format(prefix))
        fw.write("filband='{}.band'\n".format(prefix.replace("'", "")))
        fw.write("/")
    os.chdir(cur_dir)
    
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

current_directory = os.getcwd()
output_file_folder = "./"
modify_scf("scf.in.ref", output_file_folder, tomli_dict["scf"], current_directory)
modify_nscf("scf.in.ref", output_file_folder, tomli_dict["nscf"], current_directory)
modify_band("scf.in.ref", output_file_folder, tomli_dict["band"], current_directory)
write_bands(output_file_folder, tomli_dict["band"], current_directory)
