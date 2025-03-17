import os
import re
import sys
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from PIL import Image
import numpy as np

class ImageTrimmer:
    def __init__(self):
        self.directory = os.path.dirname(os.path.abspath(__file__))
        self.images = []
        self.current_img_index = 0
        self.current_img = None
        self.current_img_path = None
        self.fig = None
        self.ax = None
        self.y_min = None
        self.y_max = None
        self.x_min = None
        self.x_max = None
        self.is_trimming = False
        self.selector = None
    
    def load_images(self, pattern=r'formula_images_\d+\.png'):
        """指定されたパターンに一致する画像を読み込む"""
        print("画像ファイルを検索中...")
        
        for filename in sorted(os.listdir(self.directory)):
            if re.match(pattern, filename) and os.path.isfile(os.path.join(self.directory, filename)):
                self.images.append(filename)
        
        if not self.images:
            print("画像ファイルが見つかりませんでした。")
            return False
            
        print(f"{len(self.images)}個の画像ファイルを検出しました。")
        return True
    
    def load_specific_images(self, image_list):
        """指定されたリストの画像だけを読み込む"""
        print("指定された画像ファイルを検索中...")
        
        for filename in image_list:
            if os.path.exists(os.path.join(self.directory, filename)):
                self.images.append(filename)
        
        if not self.images:
            print("指定された画像ファイルが見つかりませんでした。")
            return False
            
        print(f"{len(self.images)}個の画像ファイルを検出しました。")
        return True
        
    def show_image(self):
        """現在の画像を表示"""
        if self.current_img_index >= len(self.images):
            print("すべての画像の処理が完了しました。")
            plt.close(self.fig)
            return False
        
        self.current_img_path = os.path.join(self.directory, self.images[self.current_img_index])
        img = Image.open(self.current_img_path)
        self.current_img = np.array(img)
        
        if self.fig is None:
            self.fig, self.ax = plt.subplots(figsize=(10, 8))
            plt.subplots_adjust(bottom=0.2)  # ボタン用のスペースを確保
        else:
            self.ax.clear()
        
        self.ax.imshow(self.current_img, cmap='gray')
        self.ax.set_title(f'画像 {self.current_img_index+1}/{len(self.images)}: {self.images[self.current_img_index]}')
        
        # RectangleSelector初期化
        self.selector = RectangleSelector(
            self.ax, self.on_select, useblit=True,
            button=[1], minspanx=5, minspany=5,
            spancoords='pixels', interactive=True
        )
        
        # ボタン配置
        ax_skip = plt.axes([0.3, 0.05, 0.1, 0.075])
        ax_save = plt.axes([0.45, 0.05, 0.1, 0.075])
        ax_next = plt.axes([0.6, 0.05, 0.1, 0.075])
        
        from matplotlib.widgets import Button
        self.btn_skip = Button(ax_skip, 'スキップ')
        self.btn_save = Button(ax_save, '保存')
        self.btn_next = Button(ax_next, '次へ')
        
        self.btn_skip.on_clicked(self.skip_image)
        self.btn_save.on_clicked(self.save_and_next)
        self.btn_next.on_clicked(self.next_image)
        
        plt.show()
        return True
    
    def on_select(self, eclick, erelease):
        """矩形選択時のコールバック"""
        self.is_trimming = True
        self.x_min, self.y_min = int(eclick.xdata), int(eclick.ydata)
        self.x_max, self.y_max = int(erelease.xdata), int(erelease.ydata)
        
        print(f"選択範囲: (left={self.x_min}, top={self.y_min}) - (right={self.x_max}, bottom={self.y_max})")
    
    def skip_image(self, event):
        """現在の画像をスキップ"""
        print(f"スキップ: {self.images[self.current_img_index]}")
        self.current_img_index += 1
        plt.close(self.fig)
        self.fig = None
        self.show_image()
    
    def save_and_next(self, event):
        """トリミングした画像を保存して次へ"""
        if not self.is_trimming:
            print("トリミング範囲が選択されていません。")
            return
        
        try:
            # PILで画像を開く
            img = Image.open(self.current_img_path)
            
            # トリミング
            cropped = img.crop((self.x_min, self.y_min, self.x_max, self.y_max))
            
            # 保存
            cropped.save(self.current_img_path)
            print(f"保存しました: {self.images[self.current_img_index]} (サイズ: {cropped.width}x{cropped.height})")
            
            # 次の画像へ
            self.current_img_index += 1
            plt.close(self.fig)
            self.fig = None
            self.is_trimming = False
            self.show_image()
            
        except Exception as e:
            print(f"エラー: {str(e)}")
    
    def next_image(self, event):
        """次の画像へ（保存せずに）"""
        if self.is_trimming:
            print("選択範囲は保存されません。")
        
        self.current_img_index += 1
        plt.close(self.fig)
        self.fig = None
        self.is_trimming = False
        self.show_image()
    
    def get_specific_images(self):
        """ファイルからトリミングしたい特定の画像リストを読み込む"""
        image_list = []
        
        try:
            target_file = os.path.join(self.directory, "trim_targets.txt")
            
            if not os.path.exists(target_file):
                print("トリミング対象リストが見つかりません。すべての画像を処理します。")
                return None
                
            with open(target_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # ファイル名を含む行を検出
                    match = re.search(r'formula_images_\d+\.png', line)
                    if match:
                        image_list.append(match.group(0))
            
            if not image_list:
                print("対象となる画像が見つかりませんでした。すべての画像を処理します。")
                return None
                
            print(f"{len(image_list)}個のターゲット画像を読み込みました。")
            return image_list
            
        except Exception as e:
            print(f"ターゲットファイル読み込み中にエラー: {str(e)}")
            return None

def main():
    trimmer = ImageTrimmer()
    
    # 特定の画像リストを取得
    specific_images = trimmer.get_specific_images()
    
    if specific_images:
        # 特定の画像だけを読み込む
        if not trimmer.load_specific_images(specific_images):
            print("処理を終了します。")
            return
    else:
        # すべての画像を読み込む
        if not trimmer.load_images():
            print("処理を終了します。")
            return
    
    # 最初の画像を表示
    trimmer.show_image()
    
    print("処理が完了しました。")

if __name__ == "__main__":
    main()