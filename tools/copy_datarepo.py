import os
import shutil
import glob

# カレントディレクトリを対象とする
current_dir = os.getcwd()
destination_path = './'  # コピー先のパスを設定してください

# カレントディレクトリ内のファイルを処理
dest_folder = os.path.join(destination_path, 'organized_data')

# コピー先にフォルダを作成
os.makedirs(dest_folder, exist_ok=True)

# qeディレクトリを新規作成
qe_folder = os.path.join(dest_folder, 'qe')
os.makedirs(qe_folder, exist_ok=True)

# *.in, *.out, *.band.gnuファイルをqeディレクトリにコピー
for file in glob.glob(os.path.join(current_dir, '*.in')) + glob.glob(os.path.join(current_dir, '*.out')) + glob.glob(os.path.join(current_dir, '*.band.gnu')):
    shutil.copy(file, qe_folder)

for file_name in ['respack.in', 'calc_wan.out']:
    file_path = os.path.join(qe_folder, file_name)
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"Deleted: {file_path}")

# respackディレクトリを新規作成
respack_folder = os.path.join(dest_folder, 'respack')
os.makedirs(respack_folder, exist_ok=True)

# respack.inとcalc_wan.outファイルをrespackディレクトリにのみコピー（存在する場合）
for file_name in ['respack.in', 'calc_wan.out']:
    src_file_path = os.path.join(current_dir, file_name)
    if os.path.isfile(src_file_path):
        shutil.copy(src_file_path, respack_folder)

# dir-intWとdir-modelディレクトリをrespackディレクトリにコピー
for dir_name in ['dir-intW', 'dir-model']:
    src_dir_path = os.path.join(current_dir, dir_name)
    if os.path.isdir(src_dir_path):
        shutil.copytree(src_dir_path, os.path.join(respack_folder, dir_name), dirs_exist_ok=True)

                
