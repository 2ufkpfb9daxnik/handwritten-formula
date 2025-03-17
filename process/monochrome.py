import os
import re
from PIL import Image, ImageEnhance
import numpy as np
import cv2

def binarize_images():
    """
    ディレクトリ内のすべてのformula_images_XXX.png画像を
    2値化（白黒バイナリ画像に変換）する
    急激なコントラスト変化がある部分（線）だけを検出して黒くする
    """
    print("画像の2値化処理を開始します...")
    
    # カレントディレクトリ
    directory = os.path.dirname(os.path.abspath(__file__))
    
    # 対象となるファイルを検索（formula_images_XXX.png）
    pattern = re.compile(r'formula_images_\d+\.png')
    target_files = []
    
    for filename in os.listdir(directory):
        if pattern.match(filename) and os.path.isfile(os.path.join(directory, filename)):
            target_files.append(filename)
    
    if not target_files:
        print("対象となるファイルが見つかりませんでした。")
        return
    
    print(f"{len(target_files)}個のファイルを処理します。")
    
    # 各画像を2値化処理
    success_count = 0
    for filename in sorted(target_files):
        try:
            file_path = os.path.join(directory, filename)
            
            # 画像を開く
            img = Image.open(file_path)
            
            # コントラストを強調
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)  # コントラストを強める
            
            # グレースケールに変換
            if img.mode != 'L':
                img = img.convert('L')
            
            # NumPy配列に変換（OpenCV用）
            img_array = np.array(img)
            
            # ガウシアンブラーでノイズを軽減
            blurred = cv2.GaussianBlur(img_array, (5, 5), 0)
            
            # エッジ検出（Sobelフィルタ使用）
            sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
            
            # 勾配の大きさを計算
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
            
            # 勾配値を0-255の範囲にスケーリング
            gradient_magnitude = cv2.normalize(gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            
            # 閾値の調整（エッジの強さに基づいて）
            edge_threshold = 30  # この値を調整：低いと多くの線が検出され、高いと少なくなる
            
            # エッジ部分を黒、その他を白にする（反転して処理）
            binary_img = np.where(gradient_magnitude > edge_threshold, 0, 255).astype(np.uint8)
            
            # モルフォロジー演算で線を滑らかに（オプション）
            kernel = np.ones((2, 2), np.uint8)
            binary_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)
            
            # PILイメージに戻す
            result = Image.fromarray(binary_img)
            
            # 元のファイル名で保存
            result.save(file_path)
            
            success_count += 1
            
            # 進捗表示（20ファイルごと）
            if success_count % 20 == 0 or success_count == len(target_files):
                print(f"進捗: {success_count}/{len(target_files)} 処理完了 (エッジ閾値: {edge_threshold})")
                
        except Exception as e:
            print(f"エラー: {filename} の処理中に問題が発生しました: {str(e)}")
    
    print(f"\n処理完了: {success_count}/{len(target_files)} 個のファイルを2値化しました。")

if __name__ == "__main__":
    binarize_images()