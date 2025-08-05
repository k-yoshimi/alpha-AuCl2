"""構造最適化後の原子座標を基準入力ファイルに反映する

このスクリプトは、構造最適化計算の出力ファイルから最終的な原子座標を抽出し、
基準入力ファイルの原子座標を更新します。

Parameters
----------
なし

Returns
-------
なし

Notes
-----
入力ファイル:
    scf_relax.out : 構造最適化計算の出力ファイル
    scf.in.ref : 基準入力ファイル

出力ファイル:
    scf.in.ref : 更新された基準入力ファイル
    scf.in.ref.bak : 更新前の基準入力ファイルのバックアップ
"""

import subprocess
import os
import numpy as np

def get_atomic_pos(file_name):
    """構造最適化計算の出力ファイルから最終的な原子座標を取得する

    Parameters
    ----------
    file_name : str
        構造最適化計算の出力ファイルのパス

    Returns
    -------
    list
        原子座標のリスト。各要素は[原子種, x座標, y座標, z座標]の形式
    """
    with open(file_name, "r") as fr:
        lines = fr.readlines()
    for idx, line in enumerate(lines):
        if line.strip() == "Begin final coordinates":
            line_start = idx
        if line.strip() == "End final coordinates":
            line_end = idx
    atom_pos = lines[line_start+3:line_end]
    pos_info = []
    for words in atom_pos:
        info = words.split()
        pos_info.append([info[0], info[1], info[2], info[3]])
    return pos_info

def rewrite_scf_in_ref(output_file_folder, pos_info, file_name="scf.in.ref"):
    """基準入力ファイルの原子座標を更新する

    Parameters
    ----------
    output_file_folder : str
        出力先フォルダのパス
    pos_info : list
        原子座標のリスト
    file_name : str, optional
        基準入力ファイル名。デフォルトは"scf.in.ref"

    Returns
    -------
    なし
    """
    os.chdir(output_file_folder)
    subprocess.run(["cp", file_name, "{}.bak".format(file_name)])    
    with open(file_name, "r") as fr:
        lines = fr.readlines()
    str_write = ""
    for line in lines:
        str_write += line
        if line.strip() == "ATOMIC_POSITIONS {crystal}":
            break
    for pos in pos_info:
        str_write += "{} {} {} {}\n".format(pos[0], pos[1][:12], pos[2][:12], pos[3][:12])

    with open(file_name, "w") as fw:
        fw.write(str_write)
    

output_file_folder = "./"
pos_relaxed = get_atomic_pos(os.path.join(output_file_folder, "scf_relax.out"))
rewrite_scf_in_ref(output_file_folder, pos_relaxed)
