"""圧力依存のバンド構造をプロットするためのgnuplotスクリプトを生成する

このスクリプトは、異なる圧力下でのバンド構造計算結果を収集し、
それらを比較するためのgnuplotスクリプトを生成します。

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
pressure_cif.dat : 圧力とCIFファイルの対応リスト
    各圧力とそれに対応するCIFファイル名が記載されたリストファイル
    1行目: 圧力[GPa] CIFファイル名

band.gnu : バンドデータファイル
    各圧力フォルダ内のバンド構造データ
    k点とエネルギー値が記載されたファイル

data-file-schema.xml : 計算結果XMLファイル
    Quantum Espressoの計算結果が記載されたXMLファイル
    フェルミエネルギーなどの情報を含む

出力ファイル
-----------
band/band_plot.gnu : gnuplotスクリプトファイル
    生成されたプロット用スクリプト
    y軸範囲の設定とプロットコマンドを含む

band/*.band.gnu : バンドデータファイル
    各圧力のバンド構造データ
    フェルミエネルギーを基準(0)としたエネルギー値に変換される

See Also
--------
gnuplot : データ可視化ツール
Quantum Espresso : 第一原理計算ソフトウェア
"""

import subprocess
import os
    
with open("pressure_cif.dat", "r") as fr:
    lines = fr.readlines()


os.makedirs("band", exist_ok=True)
str_gnuplot = "set yrange[-2:2]\n"
str_gnuplot += "plot "

def get_fermi_energy(file_name):
    """XMLファイルからフェルミエネルギーを取得する

    Parameters
    ----------
    file_name : str
        data-file-schema.xmlファイルのパス

    Returns
    -------
    float
        フェルミエネルギー (eV単位)

    Notes
    -----
    XMLファイルからfermi_energyタグの値を取得し、
    原子単位(Hartree)からeV単位に変換して返します。
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(file_name)
    root = tree.getroot()
    from scipy import constants
    for name in root.iter('fermi_energy'):
        fermi_energy = float(name.text) * constants.physical_constants["Hartree energy in eV"][0]
    return fermi_energy
    
for line in lines:
    words = line.split()
    output_file_folder = "{}GPa".format(words[1])
    command = ["cp", os.path.join(output_file_folder, "icl2.band.gnu"), os.path.join("band", "{}.band.gnu".format(words[1]))]
    subprocess.run(command)
    ene_f = get_fermi_energy(os.path.join(output_file_folder, "ICl2.save", "data-file-schema.xml"))
    str_gnuplot += "'{}.band.gnu' using 1:($2-{}) w lp,".format(words[1], ene_f)
    
str_gnuplot = str_gnuplot[:-1]
with open(os.path.join("band", "band_plot.gnu"), "w") as fw:
    fw.write(str_gnuplot)
