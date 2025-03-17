import os
import re
from PIL import Image
import numpy as np
import cv2

def fill_contours():
    """
    ディレクトリ内のformula_images_XXX.png画像を処理し、
    非常に細い隙間のみを黒で塗りつぶす（文字の内部は保護）
    """
    print("細隙間の塗りつぶし処理を開始します...")
    
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
    
    # 各画像を処理
    success_count = 0
    for filename in sorted(target_files):
        try:
            file_path = os.path.join(directory, filename)
            
            # 画像を開く
            img = Image.open(file_path)
            
            # グレースケールに変換
            if img.mode != 'L':
                img = img.convert('L')
            
            # NumPy配列に変換
            img_array = np.array(img)
            
            # バイナリ画像に変換（既にバイナリならスキップ）
            if np.unique(img_array).size > 2:
                _, img_array = cv2.threshold(img_array, 127, 255, cv2.THRESH_BINARY)
            
            # 処理前の画像をコピー
            original = img_array.copy()
            
            # 輪郭の検出（階層情報を含む）
            contours, hierarchy = cv2.findContours(
                ~img_array,  # 黒と白を反転（黒い輪郭を白として検出）
                cv2.RETR_CCOMP,  # 階層構造のある輪郭を検出
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # 階層情報がない場合はスキップ
            if hierarchy is None or len(contours) == 0:
                print(f"スキップ: {filename} - 適切な輪郭が見つかりませんでした")
                continue
                
            # 結果用の画像を作成
            result_img = img_array.copy()
            
            # 各輪郭を処理
            filled_count = 0
            skipped_count = 0
            
            # 輪郭を塗りつぶし
            for i, contour in enumerate(contours):
                # 輪郭の階層情報を取得
                # hierarchy[i][3] が -1 でないなら、この輪郭は別の輪郭の中にある（穴の可能性）
                is_hole = hierarchy[0][i][3] != -1
                
                if is_hole:
                    # 輪郭の大きさと形状を分析
                    x, y, w, h = cv2.boundingRect(contour)
                    area = cv2.contourArea(contour)
                    
                    # 非常に細い隙間かどうかを判定
                    is_thin_gap = (w <= 5 and h <= 5) or (w <= 3 or h <= 3)
                    
                    # 細長い隙間のみ塗りつぶし対象とする
                    aspect_ratio = max(w, h) / (min(w, h) if min(w, h) > 0 else 1)
                    is_elongated = aspect_ratio > 3.0  # 細長い形状
                    
                    # A, P, B, R, D などの文字の内部は保護する
                    # - 大きすぎる穴は文字の内部と見なす
                    # - ある程度の大きさで、アスペクト比が正方形に近いものも保護
                    is_character_interior = (area > 100) or (area > 50 and aspect_ratio < 2.0)
                    
                    if is_thin_gap and not is_character_interior:
                        # 非常に細い隙間のみを塗りつぶす
                        cv2.drawContours(result_img, [contour], 0, 0, -1)
                        filled_count += 1
                    else:
                        skipped_count += 1
            
            # 変化があった場合のみ保存
            if not np.array_equal(original, result_img):
                # PILイメージに戻す
                result = Image.fromarray(result_img)
                # 元のファイル名で保存
                result.save(file_path)
                success_count += 1
                
                # 情報表示
                print(f"{filename}: {filled_count}個の細隙間を塗りつぶし、{skipped_count}個の領域を保護")
            else:
                print(f"{filename}: 変化なし")
                
        except Exception as e:
            print(f"エラー: {filename} の処理中に問題が発生しました: {str(e)}")
    
    print(f"\n処理完了: {success_count}/{len(target_files)} 個のファイルを処理しました。")

if __name__ == "__main__":
    fill_contours()