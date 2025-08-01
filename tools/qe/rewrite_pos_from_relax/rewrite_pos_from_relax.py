"""構造最適化後の原子座標と格子パラメータを入力ファイルに反映する

このスクリプトは、構造最適化計算の出力ファイルから最終的な原子座標と格子パラメータを抽出し、
入力ファイルの対応する部分を更新します。

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
scf_relax.out : 構造最適化計算の出力ファイル
    ATOMIC_POSITIONS (crystal)ブロックと
    CELL_PARAMETERS (alat)ブロックを含む必要があります

scf_relax.in : 更新対象の入力ファイル
    ATOMIC_POSITIONS {crystal}ブロックと
    CELL_PARAMETERS {alat}ブロックを含む必要があります

出力ファイル
----------
scf_relax.in : 更新された入力ファイル
    原子座標と格子パラメータが更新されます

scf_relax.in.bak : 更新前の入力ファイルのバックアップ
    元のファイルのコピー

See Also
--------
extract_last_atomic_positions : 最後の原子座標ブロックを抽出
extract_last_cell_parameters : 最後の格子パラメータを抽出
replace_atomic_positions : 原子座標を更新
replace_alat_and_cell_parameters : 格子パラメータを更新
"""

import shutil
import re

def extract_last_atomic_positions(out_file_path):
    """構造最適化計算の出力ファイルから最後の原子座標ブロックを抽出する

    Parameters
    ----------
    out_file_path : str
        構造最適化計算の出力ファイルのパス

    Returns
    -------
    list or None
        原子座標のブロック。見つからない場合はNone
        ブロックの最初の行は"ATOMIC_POSITIONS (crystal)"
        2行目以降は"原子種 x y z"の形式
    """
    try:
        with open(out_file_path, 'r') as file:
            lines = file.readlines()

        atomic_positions = []
        current_block = []
        inside_block = False

        # ファイルの内容をループして最後の ATOMIC_POSITIONS (crystal) ブロックを見つける
        for line in lines:
            if 'ATOMIC_POSITIONS (crystal)' in line:
                inside_block = True
                current_block = [line.strip()]  # 新しいブロックの開始
            elif inside_block:
                if line.strip() == '' or 'End final coordinates' in line:
                    inside_block = False  # 空行が出たらブロックの終了
                else:
                    current_block.append(line.strip())

        return current_block if current_block else None

    except FileNotFoundError:
        print(f"ファイル {out_file_path} が見つかりませんでした。")
        return None


def replace_atomic_positions(in_file_path, out_file_path):
    """入力ファイルの原子座標を更新する

    Parameters
    ----------
    in_file_path : str
        更新対象の入力ファイルのパス
    out_file_path : str
        構造最適化計算の出力ファイルのパス

    Returns
    -------
    なし
    """
    # scf_relax.out から最後の ATOMIC_POSITIONS (crystal) を取得
    new_atomic_positions = extract_last_atomic_positions(out_file_path)
    
    if new_atomic_positions is None:
        print("新しい ATOMIC_POSITIONS (crystal) が見つかりませんでした。")
        return

    # 元のファイルをバックアップ
    backup_file_path = in_file_path + '.bak'
    shutil.copy(in_file_path, backup_file_path)
    print(f"バックアップを作成しました: {backup_file_path}")

    # scf_relax.in を読み込み、ATOMIC_POSITIONS {crystal} ブロックを置き換え
    with open(in_file_path, 'r') as file:
        lines = file.readlines()

    inside_block = False
    new_lines = []
    for line in lines:
        if 'ATOMIC_POSITIONS {crystal}' in line:
            inside_block = True
            new_lines.append(line.strip())  # "ATOMIC_POSITIONS {crystal}" の行を追加
            new_lines.extend(new_atomic_positions[1:])  # 新しい原子位置データを追加
        elif inside_block:
            if line.strip() == '' or 'End final coordinates' in line:
                inside_block = False  # 空行でブロックの終了
            continue  # 元のブロックをスキップ
        else:
            new_lines.append(line.strip())  # 他の行はそのまま追加

    # 残りの行も保持して書き戻す
    remaining_lines = lines[len(new_lines):]
    new_lines.extend([line.strip() for line in remaining_lines])

    # 置き換えた内容をファイルに書き戻す
    with open(in_file_path, 'w') as file:
        file.write("\n".join(new_lines) + "\n")

    print(f"{in_file_path} の ATOMIC_POSITIONS {{crystal}} ブロックを更新しました。")

def extract_last_cell_parameters(out_file_path):
    """構造最適化計算の出力ファイルから最後の格子パラメータを抽出する

    Parameters
    ----------
    out_file_path : str
        構造最適化計算の出力ファイルのパス

    Returns
    -------
    tuple
        (格子定数, 格子ベクトルのリスト)。見つからない場合は(None, None)
        格子定数はalat値(atomic unit)
        格子ベクトルは3x3の行列で、各行は空白区切りの3つの数値
    """
    try:
        with open(out_file_path, 'r') as file:
            lines = file.readlines()

        # "CELL_PARAMETERS (alat= xxx)" の値と、その下の3x3行列を取得
        alat_value = None
        cell_parameters_block = []
        inside_block = False

        for line in lines:
            if 'CELL_PARAMETERS (alat=' in line:
                inside_block = True
                alat_value = float(re.search(r'alat= ([0-9.]+)', line).group(1))  # alatの数値を抽出
                cell_parameters_block = []  # 新しいブロックの開始
            elif inside_block:
                if len(line.strip().split()) == 3:  # 3x3の行列の各行を抽出
                    cell_parameters_block.append(line.strip())
                else:
                    inside_block = False  # 他の行が来たらブロックの終了

        return alat_value, cell_parameters_block

    except FileNotFoundError:
        print(f"ファイル {out_file_path} が見つかりませんでした。")
        return None, None


def replace_alat_and_cell_parameters(in_file_path, alat_value, cell_parameters_block):
    """入力ファイルの格子定数と格子ベクトルを更新する

    Parameters
    ----------
    in_file_path : str
        更新対象の入力ファイルのパス
    alat_value : float
        新しい格子定数(atomic unit)
    cell_parameters_block : list
        新しい格子ベクトルのリスト
        3x3の行列で、各行は空白区切りの3つの数値

    Returns
    -------
    なし
    """
    if alat_value is None or not cell_parameters_block:
        print(f"置き換えるべきデータが見つかりませんでした。")
        return

    # 原子単位系 (au) からオングストローム (Å) に変換 (1 au = 0.529177 Å)
    alat_value_angstrom = alat_value * 0.529177
    
    # 元のファイルをバックアップ
    backup_file_path = in_file_path + '.bak'
    shutil.copy(in_file_path, backup_file_path)
    print(f"バックアップを作成しました: {backup_file_path}")

    with open(in_file_path, 'r') as file:
        lines = file.readlines()

    # ファイル内容の置き換え
    new_lines = []
    inside_cell_block = False

    for line in lines:
        # A = xxx の行を置き換え
        if line.strip().startswith('A ='):
            new_line = re.sub(r'A\s*=\s*[0-9.]+', f'A = {alat_value_angstrom:.6f}', line)  # 小数点以下6桁に設定
            new_lines.append(new_line.strip())
        # CELL_PARAMETERS {alat} ブロックを置き換え
        elif 'CELL_PARAMETERS {alat}' in line:
            new_lines.append(line.strip())
            new_lines.extend(cell_parameters_block)  # 3x3の行列を挿入
            inside_cell_block = True
        elif inside_cell_block:
            # 既存のCELL_PARAMETERSの内容をスキップ
            if len(line.strip().split()) == 3:  # 行列データが続く限りスキップ
                continue
            else:
                inside_cell_block = False
                new_lines.append(line.strip())  # 3x3行列が終わったら残りの行を追加
        else:
            new_lines.append(line.strip())

    # 書き戻し
    with open(in_file_path, 'w') as file:
        file.write("\n".join(new_lines) + "\n")

    print(f"{in_file_path} の A と CELL_PARAMETERS ブロックを更新しました。")

in_file_path = 'scf_relax.in'
out_file_path = 'scf_relax.out'
# for in_file_path in ["scf.in", "nscf.in", "band.in"]:
replace_atomic_positions(in_file_path, out_file_path)
# scf_relax.out から alat と CELL_PARAMETERS を取得
alat_value, cell_parameters_block = extract_last_cell_parameters(out_file_path)
print(alat_value)
# scf.in を更新
replace_alat_and_cell_parameters(in_file_path, alat_value, cell_parameters_block)
#
# for in_file_path in ["scf.in", "nscf.in", "band.in"]:
#     replace_atomic_positions(in_file_path, out_file_path)
#     # scf_relax.out から alat と CELL_PARAMETERS を取得
#     alat_value, cell_parameters_block = extract_last_cell_parameters(out_file_path)
#     # scf.in を更新
#     replace_alat_and_cell_parameters(in_file_path, alat_value, cell_parameters_block)
