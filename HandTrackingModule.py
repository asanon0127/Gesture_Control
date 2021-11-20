import cv2
import mediapipe as mp
import time

class handDetector:
    def __init__(self, mode=False, maxHands=1, detectionCon=0.8, trackCon=0.8):
        #mpHands.Handsの引数
        self.mode = mode#False:信頼度によって検出と追跡を行う,True:ずっと行う
        self.maxHands = maxHands#ての数
        self.detectionCon = detectionCon#検出の信頼度:50%
        self.trackCon = trackCon #追跡の信頼度:50%
        #mediapipeのモジュールにアクセス
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        #手の21箇所にlandmarkを描画
        self.mpDraw = mp.solutions.drawing_utils
    #点と点を結ぶ線を描画
    def findHands(self, img, draw=True):
        #BGRをRGBに
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #動画像を引数に入れると手を検出してくれる
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img
    #各点に大きい丸を描画
    def findPosition(self, img, handNo=0, draw=True):
 
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            #id:21個の点の番号,lm:座標
            for id, lm in enumerate(myHand.landmark):
                #h:縦ピクセル,w:横ピクセル,c:チャンネル数
                h, w, c = img.shape
                #各指に丸を描画するための位置
                finx, finy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, finx, finy])
                if draw:
                    cv2.circle(img, (finx, finy), 15, (255, 80, 150), cv2.LINE_8)
        return lmList
def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)#webカメラ起動
    detector = handDetector()#インスタンス生成
    count = time.time()
    while True:
        success, img = cap.read()#webカメラを読み込む

        img = cv2.flip(img,1)#画像左右反転
        img = detector.findHands(img)#点と点を結ぶ線
        lmList = detector.findPosition(img)#点に大きい丸をつける
        
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, "fps:"+str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                        (255, 0, 255), 3)
            #もし画像をキャッチできていたら
        if success:
            cv2.imshow("Img", img)
        k = cv2.waitKey(1) & 0xff
        if k == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break

 
if __name__ == "__main__":
    main()