import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

def pil2cv(imgPIL):
    imgCV_RGB = np.array(imgPIL, dtype = np.uint8)
    imgCV_BGR = np.array(imgPIL)[:, :, ::-1]
    return imgCV_BGR

def cv2pil(imgCV):
    imgCV_RGB = imgCV[:, :, ::-1]
    imgPIL = Image.fromarray(imgCV_RGB)
    return imgPIL

def cv2_putText_1(img, text, org, fontFace, fontScale, color):
    x, y = org
    b, g, r = color
    colorRGB = (r, g, b)
    imgPIL = cv2pil(img)
    draw = ImageDraw.Draw(imgPIL)
    fontPIL = ImageFont.truetype(font = fontFace, size = fontScale)
    draw.text(xy = (x,y), text = text, fill = colorRGB, font = fontPIL)
    """
    後でここに追加する
    """
    imgCV = pil2cv(imgPIL)
    return imgCV

def main():
    img = np.full((200,400,3), (160,160,160), dtype=np.uint8)

    # 普通にcv2.putText()でテキストを描写する
    text = "OpenCV"
    x, y = 50, 100
    fontCV = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    colorBGR = (255,0,0)
    thickness = 1

    cv2.putText(img = img,
                text = text,
                org = (x,y),
                fontFace = fontCV,
                fontScale = fontScale,
                color = colorBGR,
                thickness = thickness)
    """
    後でここに追加する
    """

    # 独自関数で日本語テキストを描写する
    text = "日本語も\n可能なり"
    x, y = 200,100
    fontPIL = "Dflgs9.TTC" # DF麗雅宋
    size = 40
    colorBGR = (255,0,0) # cv2.putText()と同じく、BGRの順で定義

    img = cv2_putText_1(img = img,
                        text = text,
                        org = (x,y),
                        fontFace = fontPIL,
                        fontScale = size,
                        color = colorBGR)

    cv2.imshow("cv2_japanese_test", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()