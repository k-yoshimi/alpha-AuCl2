"""現在のディレクトリ内のgnuplotスクリプトを実行する

このスクリプトは、カレントディレクトリ内の全ての.gnuplotファイルを検索し、
gnuplotコマンドを使用して順次実行します。

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
*.gnuplot : gnuplotスクリプトファイル
    実行するgnuplotスクリプトファイル
    プロットコマンドやスタイル設定などを含む

出力ファイル
-----------
なし
    各gnuplotスクリプトの実行結果は、
    スクリプト内で指定された出力先に保存されます

See Also
--------
gnuplot : データ可視化ツール
"""

import os
import subprocess

def run_gnuplot_scripts():
    # 現在のディレクトリから .gnuplot ファイルを取得
    gnuplot_files = [f for f in os.listdir() if f.endswith('.gnuplot')]
    
    # 各 .gnuplot ファイルを実行
    for gnuplot_file in gnuplot_files:
        print(f"Running {gnuplot_file}...")
        try:
            # gnuplot を使ってスクリプトを実行
            subprocess.run(['gnuplot', gnuplot_file], check=True)
            print(f"Successfully executed {gnuplot_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {gnuplot_file}: {e}")

if __name__ == "__main__":
    run_gnuplot_scripts()
