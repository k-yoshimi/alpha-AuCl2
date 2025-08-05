"""2次元フェルミ面を計算・プロットする

このスクリプトは、バンド計算の結果から2次元フェルミ面を計算し、可視化します。

Parameters
----------
--input : str, optional
    入力ファイルのパス。デフォルトは "input.toml"

Returns
-------
なし

Notes
-----
入力ファイル
----------
input.toml : 計算パラメータを含むTOMLファイル
    mode:
        param:
            CellShape : [int, int, int]
                格子サイズ (Lx, Ly, Lz)
            filling : float 
                フィリング
    file:
        output:
            path_to_output : str
                出力ディレクトリのパス
            eigen : str
                固有値データファイルの名前(拡張子なし)

eigenvalues.npz : バンド計算の固有値データ
    eigenvalue : ndarray
        固有値データ。shape=(波数点数, 軌道数)
    wavevector_index : ndarray
        波数点のインデックス

出力ファイル
----------
energy.dat : kz=0でのエネルギー値
    各行に kx ky E_1 E_2 ... E_n の形式でエネルギー値を出力
    kx, ky : [-π, π]の範囲の波数
    E_n : n番目の軌道のエネルギー値

FermiSurface_mod_orb{orbital}.pdf : 各軌道のフェルミ面プロット
    orbital : 軌道のインデックス
    フェルミ面を白黒で表示(フェルミ面の内側が白、外側が黒)

See Also
--------
scipy.interpolate.RegularGridInterpolator : 2次元補間に使用
matplotlib.pyplot.contourf : フェルミ面のプロットに使用
"""

import numpy as np
import os
import tomli
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, default="input.toml", help="input file of hwave")

args = parser.parse_args()
file_toml = args.input
if os.path.exists(file_toml):
    print("Reading input file: ", file_toml)
    with open(file_toml, "rb") as f:
        input_dict = tomli.load(f)
else:
    raise ValueError("Input file does not exist")

print("Reading eigenvalues")
output_info_dict = input_dict["file"]["output"]
data = np.load(os.path.join(output_info_dict["path_to_output"], output_info_dict["eigen"] + ".npz"))
eigenvalues = data["eigenvalue"]
wave_index = data["wavevector_index"]
wavevector_unit = data["wavevector_unit"]
#k_vec = np.dot(wave_index,wavevector_unit)

data = np.load(os.path.join(output_info_dict["path_to_output"], output_info_dict["green"] + ".npz"))
green = data["green"]
for i in range(green.shape[2]):
    print("N({},{})".format(i,i),green[0,0,i,0,i].real*2)


Lx, Ly, Lz = input_dict["mode"]["param"]["CellShape"]
n_filling = input_dict["mode"]["param"]["filling"]
norb = eigenvalues.shape[1]
print("Lx, Ly, Lz, norb: ", Lx, Ly, Lz, norb)
eigenvalues = eigenvalues.reshape(Lx*Ly*Lz*norb)
print(eigenvalues.shape)
fermi_ene = np.sort(eigenvalues)[int(Lx*Ly*Lz*norb*n_filling)]
eigenvalues -= fermi_ene
eigenvalues = eigenvalues.reshape((Lx, Ly, Lz, norb))
eig = np.zeros((Lx+1, Ly+1, Lz+1, norb))
print("Writing Energy at kz = 0 to energy.dat")
kx_org = np.linspace(-np.pi, np.pi, Lx+1, endpoint=True)
ky_org = np.linspace(-np.pi, np.pi, Ly+1, endpoint=True)

print(eigenvalues.shape)
with open("energy.dat", "w") as fw:
    for i in range(Lx+1):
        for j in range(Ly+1):
            fw.write("{} {} ".format(kx_org[i], ky_org[j]))
            for orb in range(norb):
                ene = eigenvalues[int(i+Lx/2)%Lx][int(j+Ly/2)%Ly][0%Lz][orb]
                eig[i][j][0][orb] = ene
                fw.write("{} ".format(ene))
            fw.write("\n")

import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

def plot(fermi, norb):
    plt.xlabel(r"$k_x/\pi$")
    plt.xticks(np.linspace(-np.pi, np.pi, 4, endpoint=False),np.linspace(-1.0, 1.0, 4, endpoint=False))
    plt.yticks(np.linspace(-np.pi, np.pi, 4, endpoint=False),np.linspace(-1.0, 1.0, 4, endpoint=False))
    plt.ylabel(r"$k_y/\pi$")
    plt.gca().set_aspect('equal', adjustable='box') # グラフの縦横の比をそろえるコマンド   
    plt.contourf(kx, ky, fermi>1e-3, cmap=plt.cm.binary) # 条件(ret>0)を満たす部分を白、満たさない部分を黒とする。
    plt.savefig("FermiSurface_mod_orb{}.pdf".format(norb), format="pdf", dpi=500)
    #plt.show()

def plot_band_dispersion_along_kpath(eigenvalues, k_path_points, norb, points_per_segment=40, output_file="band_dispersion.pdf"):
    """
    k-pathに沿ったバンド分散をプロット（k点間を指定した点数で等間隔サンプリング）
    
    Parameters
    ----------
    eigenvalues : ndarray
        エネルギー値 (shape: (Lx, Ly, Lz, norb))
    k_path_points : list
        k-path上の点のリスト [(kx, ky, kz, label), ...]
    norb : int
        軌道数
    points_per_segment : int
        セグメントあたりのサンプリング点数（デフォルト: 40）
    output_file : str
        出力ファイル名
    """
    # k座標の範囲を定義（eigenvaluesは0-2πで格納されているため、0-2πの範囲で定義）
    kx_range = np.linspace(0, 2*np.pi, Lx, endpoint=False)
    ky_range = np.linspace(0, 2*np.pi, Ly, endpoint=False)
    kz_range = np.linspace(0, 2*np.pi, Lz, endpoint=False)
    
    # 各軌道のエネルギーを内挿して計算
    all_k_distances = []
    all_k_labels = []
    band_energies = []
    
    # 各軌道について計算
    for orb in range(norb):
        # RegularGridInterpolatorを作成（座標の順序を修正）
        energy_interpolator = RegularGridInterpolator(
            (kx_range, ky_range, kz_range), 
            eigenvalues[:, :, :, orb], 
            method='linear',
            bounds_error=False,
            fill_value=None
        )
        
        orb_energies = []
        orb_k_distances = []
        orb_k_labels = []
        
        # 各k-pathセグメントについて20点ずつサンプリング
        for i in range(len(k_path_points) - 1):
            k1 = k_path_points[i]
            k2 = k_path_points[i + 1]
            
            # 2点間を指定した点数で等分
            for j in range(points_per_segment):
                t = j / (points_per_segment - 1.0)  # 0から1の範囲
                
                # 線形補間でk座標を計算（-πからπの範囲）
                kx = k1[0] + t * (k2[0] - k1[0])
                ky = k1[1] + t * (k2[1] - k1[1])
                kz = k1[2] + t * (k2[2] - k1[2])
                
                # k座標を0-2πの範囲に変換（eigenvaluesの座標系に合わせる）
                # -π~π → 0~2π の変換
                kx_2pi = kx % (2*np.pi)
                ky_2pi = ky % (2*np.pi)
                kz_2pi = kz % (2*np.pi)
                
                # RegularGridInterpolatorでエネルギー値を補間
                energy = energy_interpolator([kx_2pi, ky_2pi, kz_2pi])[0]
                orb_energies.append(energy)
                
                # k-path距離を計算
                if i == 0 and j == 0:
                    # 最初の点
                    k_distance = 0.0
                    orb_k_distances.append(k_distance)
                    orb_k_labels.append(k1[3])  # 最初のラベル
                else:
                    # 前の点からの距離を加算
                    prev_kx = k1[0] + ((j-1) / (points_per_segment - 1.0)) * (k2[0] - k1[0]) if j > 0 else k1[0]
                    prev_ky = k1[1] + ((j-1) / (points_per_segment - 1.0)) * (k2[1] - k1[1]) if j > 0 else k1[1]
                    prev_kz = k1[2] + ((j-1) / (points_per_segment - 1.0)) * (k2[2] - k1[2]) if j > 0 else k1[2]
                    
                    dk = np.sqrt((kx - prev_kx)**2 + (ky - prev_ky)**2 + (kz - prev_kz)**2)
                    k_distance = orb_k_distances[-1] + dk
                    orb_k_distances.append(k_distance)
                    
                    # ラベルは最初と最後の点のみ
                    if j == 0:
                        orb_k_labels.append(k1[3])
                    elif j == points_per_segment - 1:
                        orb_k_labels.append(k2[3])
                    else:
                        orb_k_labels.append("")
        
        band_energies.append(orb_energies)
        all_k_distances = orb_k_distances  # 全ての軌道で同じk-path距離を使用
        all_k_labels = orb_k_labels
    
    # プロット
    plt.figure(figsize=(12, 8))
    
    # 各軌道のバンドをプロット
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    for orb in range(norb):
        color = colors[orb % len(colors)]
        plt.plot(all_k_distances, band_energies[orb], color=color, linewidth=1.5, 
                label=f'Orbital {orb}', alpha=0.8)
        # 点も表示
        plt.scatter(all_k_distances, band_energies[orb], color=color, s=10, alpha=0.6)
    
    # フェルミエネルギー線
    plt.axhline(y=0, color='black', linestyle='--', alpha=0.5, linewidth=1, label='E_F')
    
    # k-pointラベルを追加（空でないラベルのみ）
    for i, (dist, label) in enumerate(zip(all_k_distances, all_k_labels)):
        if label:  # 空でないラベルのみ
            plt.axvline(x=dist, color='gray', linestyle=':', alpha=0.3)
            plt.text(dist, plt.ylim()[1], label, ha='center', va='bottom', 
                    rotation=45, fontsize=10, fontweight='bold')
    
    plt.xlabel('k-path distance')
    plt.ylabel('Energy (eV)')
    plt.title(f'Band Dispersion along k-path ({points_per_segment} points per segment)')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 軸の範囲を調整
    plt.xlim(0, all_k_distances[-1])
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"バンド分散プロットを保存しました: {output_file}")
    print(f"総k-point数: {len(all_k_distances)}")
    print(f"セグメント数: {len(k_path_points) - 1}")
    print(f"セグメントあたりの点数: {points_per_segment}")

# k-pathの定義（band.inから取得したk-points、-1~1の範囲）
k_path_raw = [
    (0.0, 0.0, 0.0, 'GAMMA'),
    (0.0, 0.0, 0.5, 'Z'),
    (0.0, 0.5, 0.0, 'Y'),
    (0.0, -0.5, 0.0, 'Y_2'),
    (0.5, 0.0, 0.0, 'X'),
    (0.5, -0.5, 0.0, 'V_2'),
    (-0.5, 0.0, 0.5, 'U_2'),
    (0.0, -0.5, 0.5, 'T_2'),
    (-0.5, -0.5, 0.5, 'R_2')
]

# π倍して-π~πの範囲に変換
k_path_points = [(2*kx*np.pi, 2*ky*np.pi, 2*kz*np.pi, label) for kx, ky, kz, label in k_path_raw]

# バンド分散プロットを実行
print("k-pathに沿ったバンド分散をプロット中...")
plot_band_dispersion_along_kpath(eigenvalues, k_path_points, norb, points_per_segment=50)

#for i in range(norb):
Npx = 1000
Npy = 1000
for i in range(norb):
    eta = 1e-4
    # RegularGridInterpolatorを使用して2次元補間を実行
    energy_data = np.transpose(eig, (1, 0, 2, 3))[:,:,0, i]
    ene_interpolate = RegularGridInterpolator((ky_org, kx_org), energy_data, method='cubic')
    
    kx = np.linspace(-np.pi, np.pi, Npx, endpoint=False)
    ky = np.linspace(-np.pi, np.pi, Npy, endpoint=False)
    
    # メッシュグリッドを作成
    kx_mesh, ky_mesh = np.meshgrid(kx, ky, indexing='ij')
    points = np.column_stack((ky_mesh.flatten(), kx_mesh.flatten()))
    
    # 補間を実行
    fermi_values = ene_interpolate(points)
    fermi = eta**2 / (fermi_values**2 + eta**2)
    fermi = fermi.reshape(Npx, Npy)
    
    plot(fermi, i)
