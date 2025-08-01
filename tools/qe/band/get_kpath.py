"""CIFファイルからk点経路を生成する

このスクリプトは、CIFファイルから結晶構造を読み込み、seekpathを使用して
バンド計算に必要なk点経路を自動生成します。

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
*.cif : 結晶構造ファイル
    k点経路を生成したい結晶構造のCIFファイル

出力ファイル
-----------
kpoints.dat : k点リストファイル
    Quantum Espresso用のk点経路データ
    各行には対称点の名前と3次元座標が記載される
    セグメント間は空行で区切られる

See Also
--------
seekpath : 結晶構造からk点経路を自動生成するライブラリ
ase : 原子構造の操作を行うライブラリ
"""

import ase.io
import seekpath

# CIFファイルの読み込み
structure = ase.io.read('2433895.cif')

# POSCAR形式に変換
cell = (structure.get_cell(), structure.get_scaled_positions(), structure.get_atomic_numbers())

# seekpathでk-pathを自動生成
seekpath_data = seekpath.get_path(cell)

# バンド計算に必要なk点経路の情報を表示
print("High symmetry points:", seekpath_data['point_coords'])
print("K-path:", seekpath_data['path'])

# Quantum Espressoで使うk点リストを出力
with open('kpoints.dat', 'w') as f:
    for segment in seekpath_data['path']:
        start, end = segment
        k_start = seekpath_data['point_coords'][start]
        k_end = seekpath_data['point_coords'][end]
        f.write(f"{start} {k_start[0]} {k_start[1]} {k_start[2]}\n")
        f.write(f"{end} {k_end[0]} {k_end[1]} {k_end[2]}\n")
        f.write("\n")
