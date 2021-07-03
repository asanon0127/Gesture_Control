# -*- coding:utf8 -*-
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def draw_txt(background, word, f_path, t_size , t_color, t_cood,t_pad):
    # フォント設定
    font = ImageFont.truetype(f_path, t_size)
    # テキスト入力用クラス宣言
    draw = ImageDraw.Draw(background)
    # 背景に書き込み
    cnt = 0
    for y in range(t_cood[0], background.size[1]-t_cood[0], t_size+t_pad[0]):
        for x in range(t_cood[1], background_size[0]-t_cood[1], t_size+t_pad[1]):
            if len(word) > cnt:
                draw.text((x,y), word[cnt], font=font, fill=t_color)
            else:
                break
            cnt += 1
    return background


if __name__ == "__main__":
    # 背景作成
    background_size = (320,240)
    background_color = (0,0,0,255)
    background = Image.new('RGBA', background_size, background_color)
    #テキスト指定
    word = str(np.genfromtxt('word.txt', delimiter=',', dtype=np.str))
    font_path = '/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc'
    text_size = 20
    text_color = (180,180,180,255)
    #y,x
    text_coordinate = (20,20)
    text_padding = (10,0)
    draw_img = draw_txt(background, word, font_path, text_size, text_color, text_coordinate, text_padding)
    #画像指定
    draw_img.show()
    #画像保存
    save_path = './text.png'
    draw_img.save(save_path)