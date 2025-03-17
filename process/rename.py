import os
import re
from PIL import Image
import sys

def rename_and_process_images():
    print("画像処理を開始します...")
    
    # カレントディレクトリ内のすべてのjpgファイルを取得
    directory = os.path.dirname(os.path.abspath(__file__))
    jpg_files = [f for f in os.listdir(directory) 
                if os.path.isfile(os.path.join(directory, f)) 
                and f.lower().endswith('.jpg') 
                and f != 'rename.py']
    
    if not jpg_files:
        print("JPG画像が見つかりませんでした。")
        return
    
    print(f"{len(jpg_files)}個のJPG画像を処理します。")
    
    # 数字部分を抽出してソート
    def extract_number(filename):
        match = re.search(r'(\d+)', filename)
        if match:
            return int(match.group(1))
        return 0
    
    # 数字の大きい順（降順）でソート
    jpg_files.sort(key=extract_number, reverse=True)
    
    # 目標サイズ - 長辺を500pxに制限
    target_size = 500
    
    # 各ファイルを処理
    processed_count = 0
    for index, old_filename in enumerate(jpg_files, 1):
        try:
            # 元のファイルパスと新しいファイルパス
            old_path = os.path.join(directory, old_filename)
            new_filename = f'formula_images_{index}.png'
            new_path = os.path.join(directory, new_filename)
            
            # 画像を開く
            img = Image.open(old_path)
            
            # 画像サイズを調整（比率維持）
            width, height = img.size
            ratio = min(target_size / width, target_size / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # リサイズと白黒変換
            img = img.resize((new_width, new_height), Image.LANCZOS)
            img = img.convert('L')  # RGBからグレースケールに変換
            
            # 新しいファイル名で保存（PNGフォーマット）
            img.save(new_path)
            
            # 古いファイルを削除
            os.remove(old_path)
            
            processed_count += 1
            
            # 進捗報告（10枚ごと）
            if index % 10 == 0 or index == len(jpg_files):
                print(f"処理完了: {index}/{len(jpg_files)} - {old_filename} -> {new_filename} "
                      f"サイズ: {width}x{height} -> {new_width}x{new_height}")
                
        except Exception as e:
            print(f"エラー: {old_filename} の処理中に問題が発生しました: {str(e)}")
    
    print(f"\n処理完了: {processed_count}個のファイルを処理しました。")

if __name__ == "__main__":
    rename_and_process_images()