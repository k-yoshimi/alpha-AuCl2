def filter_and_sort_by_column(input_file, cutoff_energy):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    quotient, remainder = divmod(int(lines[2]), 15)
    if remainder > 0:
        quotient += 1
    skipped_lines = 3 + quotient # header, norb, nwan
    
    # 9行目以降のデータを取得
    data_lines = lines[skipped_lines :]

    # カットオフエネルギーよりも絶対値が大きいものだけをフィルタリング
    filtered_data = [line for line in data_lines if abs(float(line.split()[5])) > cutoff_energy]

    # 6列目を浮動小数点数として解析し、その絶対値の降順でソート
    sorted_data = sorted(filtered_data, key=lambda x: abs(float(x.split()[5])), reverse=True)

    # 元のヘッダーとソートされたデータを連結して出力
    result = lines[:skipped_lines ] + sorted_data

    for line in result:
        print(line, end='')

# このスクリプトをファイルとして保存し、実行する場合は以下の部分を追加
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: script_name.py input_file cutoff_energy")
        sys.exit(1)

    input_file_path = sys.argv[1]
    cutoff = float(sys.argv[2])

    filter_and_sort_by_column(input_file_path, cutoff)
