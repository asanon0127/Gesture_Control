from typing import ContextManager
import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image, ImageDraw, ImageFont
import serial

class Rimote_Controler:
    def __init__(self):
        #fps
        self.pTime = 0.0
        self.cTime = 0.0
        #受信時のフィードバック用
        self.stateP = 0
        self.stateT = 0
        self.stateN = 0
        #loading_design
        self.pretime = 0

        self.lockP = 0
        self.lockC = 0
        self.LockTime = 0
        #指間の長さ
        self.length = 0         #親指と中指
        self.length1 = 0        #親指と人差し指の間隔
        self.length2 = 0        #人差し指と中指
        #mode_name
        self.coment = "(send)"
        self.word = "no"
        #チャンネル
        self.count = 1
        #サークル操作しているフラグ
        self.vol = 0
        #power on or off　()
        self.touch = 1          #赤外線受信=0or送信=2
        self.mode = 0           #TV=1,エアコン=2,電気=3
        self.air_mode = 0       #cool=1,hot=2
        #textに格納されている赤外線データを一時的に保持
        self.apper = 0
        #各種フラグ
        self.flag = 0           #スライド操作
        self.kiri = True        #モードが切り替わった時に処理を1度だけさせるため
        self.state = 0          #受信フィードバック用

        self.LockTime = 0.0

        self.startSlide = 0   
    def position(self,lmList):                          #手の位置の詳細
        self.x1,self.y1 = wCam - lmList[4][1],lmList[4][2]      #親指
        self.x2,self.y2 = wCam - lmList[8][1],lmList[8][2]      #人差し指
        self.x3,self.y3 = wCam - lmList[12][1],lmList[12][2]    #中指
        self.x6,self.y6 = wCam - lmList[16][1],lmList[16][2]    #薬指
        self.x7,self.y7 = wCam - lmList[20][1],lmList[20][2]    #小指
        self.x4,self.y4 = wCam - lmList[0][1],lmList[0][2]      #手の下中央
        self.x5,self.y5 = wCam - lmList[5][1],lmList[5][2]      #人差し指の付け根
        self.cx1,self.cy1 = (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2
        self.cx2,self.cy2 = (self.x2 + self.x3) // 2, (self.y2 + self.y3) // 2  #人差し指と中指の間
        self.cx3,self.cy3 = (self.x3 + self.x1) // 2, (self.y3 + self.y1) // 2  #中指と親指の間
        self.Xindex,self.Yindex = wCam-lmList[5][1],lmList[5][2]
        self.Xmiddle,self.Ymiddle = wCam-lmList[9][1],lmList[9][2]
        self.Xpinky,self.Ypinky = wCam-lmList[17][1],lmList[17][2]
        #2乗和の平方根
        self.length = math.hypot(self.x3 - self.x1,self.y3 - self.y1)           #中指と親指の距離
        self.length1 = math.hypot(self.x2 - self.x1,self.y2 - self.y1)          #親指と人差し指の距離
        self.length2 = math.hypot(self.x3 - self.x2,self.y3 - self.y2)          #中指と人差し指の距離
        self.length3 = math.hypot(self.x6 - self.x1,self.y6 - self.y1)
        self.Whand = math.hypot(self.Xpinky-self.Xindex,self.Ypinky-self.Yindex)
        self.Hhand = math.hypot(self.x4-self.Xmiddle,self.y4-self.Ymiddle)
        #手の垂直線上(スライド操作に使う)
        self.centerX2,self.centerY2 = self.x5,self.y5-int(220*z)                       #人差し指の垂直線上(サークル操作に使う)
        self.aveW,self.aveH = 130.0,190.0
        #指5本の先端に円を描画
        cv2.circle(img,(self.x1,self.y1),int(8*z),(0,140,0),cv2.LINE_8)
        cv2.circle(img,(self.x2,self.y2),int(8*z),(0,140,0),cv2.LINE_8)
        cv2.circle(img,(self.x3,self.y3),int(8*z),(0,140,0),cv2.LINE_8)
        cv2.circle(img,(self.x6,self.y6),int(8*z),(0,140,0),cv2.LINE_8)
        cv2.circle(img,(self.x7,self.y7),int(8*z),(0,140,0),cv2.LINE_8)
        #サークル操作
        if self.length <= 50*z and self.y7 >= self.Ypinky:
            self.angle2 = math.degrees(math.atan2(self.y2 - (self.y5-int(130*z)),self.x2 - self.x5) - math.atan2(self.centerY2 - (self.y5-int(130*z)),self.centerX2 - self.x5))
            cv2.circle(img,(self.x5,self.y5-int(130*z)),int(10*z),(0,0,255),cv2.FILLED)
            cv2.circle(img,(self.x2,self.y2),int(10*z),(0,0,255),cv2.FILLED)
            cv2.circle(img,(self.x5,self.y5-int(130*z)),int(70*z),(60,200,60),cv2.LINE_8)
            cv2.circle(img,(self.cx3,self.cy3),10,(0,0,255),cv2.FILLED)
        
        if self.y2 <= self.y5 and self.y7 <= self.Ypinky and self.length <= int(60*z) and self.length3 <= int(50*z):
            self.lock = 0
            if self.lockP == 0:
                self.lockP = time.time()
            self.lockC = time.time()
            self.LockTime = self.lockC - self.lockP
            self.lock += int(15*Rimocon_cntroler.LockTime)
            if OnOff == 1:
                cv2.circle(img,(wCam//6,620),self.lock,(0,0,250),cv2.FILLED)
            if OnOff == 0:
                cv2.circle(img,(wCam//6,620),self.lock,(0,250,0),cv2.FILLED)
        else:
            self.lockP = 0
            self.lockC = 0 
            self.LockTime = 0
    def chossing_Option(self,img,lmList,choX,choY):     #
        meter = 350
        Cmeter = 0
        #TVへの送信
        self.value_control()
        if self.touch == 0:
            self.coment = "_S"
        elif self.touch == 2:
            self.coment = "_R"
        if self.mode == 1:
            for i in posY:
                for j in posX:
                    #finger_counterから送られてくる番号の座標がposX[0],psoY[0]でまだ切り替えていなかったら
                    if self.kiri != SEPA and choX == posX[0] and choY == posY[0]:
                        self.kiri = not self.kiri                                   #切り替えた合図
                        #電源ボタンの色を変える
                        cv2.rectangle(img, (wCam//2-100,303), (wCam//2+100,353), (0,40,100),thickness=-1)
                        cv2.putText(img, "ON", (wCam//2-20,335), cv2.FONT_HERSHEY_PLAIN, 2,white, 3)
                        self.state = 1
                        self.word = "LOOK_TV!"
                        self.redline(0)
                        break
                    elif i == posY[0]:
                        if finger.tmp == 0:
                            meter -= int(25*finger.countingTime)
                        cv2.rectangle(img, (wCam//2-100,303), (wCam//2+100,353), (0,40,100),thickness=-1)
                        cv2.rectangle(img, (wCam//2-100,300), (wCam//2+100,350), (50,91,200),thickness=-1)
                        cv2.rectangle(img, (wCam//2-100,meter), (wCam//2+100,350), (100,150,255),thickness=-1)
                        cv2.putText(img, "ON", (wCam//2-20,335), cv2.FONT_HERSHEY_PLAIN, 2,white, 3)
                    if i == posY[0]:
                        break
                    #finger_counterから送られてくる番号の座標がposX,psoYと等しく,まだ切り替えていなかったら
                    if j == choX and i == choY and self.kiri != SEPA:
                        self.kiri = not self.kiri                                   #切り替えた合図
                        #チャンネルボタンの色を変える
                        cv2.circle(img,(j+3,i+3),20,(0,40,100),cv2.FILLED)
                        cv2.putText(img, str(self.count), (j-7, i+13), cv2.FONT_HERSHEY_PLAIN, 2,white, 3)
                        self.state = 1
                        self.word = str(self.count)+"CHANNEL"
                        self.redline(self.count)
                        self.count += 1
                    else:
                        cv2.circle(img,(j+2,i+2),20,(0,40,100),cv2.FILLED)
                        cv2.circle(img,(j,i),20,(50,91,200),cv2.FILLED)
                        if finger.tmp == self.count:
                            Cmeter += int(10*finger.countingTime)
                            cv2.circle(img, (j,i),Cmeter,(100,150,255),thickness=-1)
                        cv2.putText(img, str(self.count), (j-10, i+10), cv2.FONT_HERSHEY_PLAIN, 2,white, 3)
                        self.count += 1
        self.count = 1
    def value_control(self):                            #サークル操作を使うための関数
        if len(lmList) != 0:
            if self.length <= 50*z and self.y7 >= self.Ypinky:                                                       #親指と中指の距離
                self.vol = 1
                cv2.circle(img,(self.cx3,self.cy3),int(10*z),(0,0,255),cv2.FILLED)             #人差し指にプロット
                self.position(lmList)                                                   #全指の位置                                         
                vollume_volntroler.change_vol(self.angle2)                                #ボリュームを変える関数
            if self.length > 50*z:                                                        #指を話したら終了の合図
                self.vol = 0 
    def change_mode(self,img,lmList,choX,choY,SEPA):
        if OnOff == 1:
            if self.mode == 1:
                self.chossing_Option(img,lmList,choX,choY)                       #TV or air or Light
            if self.mode == 2:
                self.air_change_mode(img,lmList)
            elif self.mode == 3:
                if self.kiri != SEPA and choX == posX[0] and choY == posY[0]:
                    self.kiri = not self.kiri
                    self.state = 1
                    self.word = "LOOK_LIGHT!"
                    self.redline(10)
                # elif ser.in_waiting>0:
                #     self.apper = ser.readline().strip().decode('UTF-8')
                #     if self.apper == 't':
                #         self.state = 1
                #         self.word = "turn_on!"
                #         print("True")
                #         self.redline(10)
                #         print("Tですよ")
            self.value_control()
    def air_change_mode(self,img,lmList):
        if self.kiri != SEPA and choX == posX[1] and choY == posY[2]:
                self.kiri = not self.kiri
                self.state = 1
                self.word = "AIRCON_OFF"
                self.redline(21)
        if self.air_mode == 1:
            #もし手が0を示していたら冷房のオンオフを切り替える____________________________________
            if self.kiri != SEPA and choX == posX[0] and choY == posY[0]:
                self.kiri = not self.kiri
                self.state = 1
                self.word = "AIRCON_ON"
                self.redline(13)
            self.value_control()
        elif self.air_mode == 2:
            #もし手が0を示していたら暖房のオンオフを切り替える____________________________________
            if self.kiri != SEPA and choX == posX[0] and choY == posY[0]:
                self.kiri = not self.kiri
                self.state = 1
                self.word = "AIRCON_ON"
                self.redline(14)
            self.value_control()
    def fpslevel(self):                                 #一秒間に何フレームのデータを送れるか
        self.cTime = time.time()
        self.fps = 1/(self.cTime-self.pTime)
        self.pTime = self.cTime
        cv2.putText(img,f'FPS: {int(self.fps)}',(wCam-150,40),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),3)
    def slide(self,lmList):
        if self.startSlide == 1:
            self.Xstartpos,self.Ystartpos = self.cx2,self.cy2
            self.startSlide = 2
        cv2.circle(img,(self.cx2,self.cy2),10,(0,0,255),cv2.FILLED)
        sa = self.cx2 - self.Xstartpos
        if sa >= 0:
            Design.moveR = int(sa//20*(1/z))
        elif sa < 0:
            Design.moveL = int(-sa//20*(1/z))
        Design.move = int(sa//30*(1/z))
        if sa >= 250*z:
            self.flag = 1
        if -sa >= 250*z:
            self.flag = 2
        if self.flag == 1:
            if self.touch != 1 and self.mode == 0:
                if vollume_volntroler.desCnt==0:
                    print("10")
                    self.mode = 1
                elif vollume_volntroler.desCnt==1:   
                    print("11")                  
                    self.mode=2
                    self.air_mode = 1
                elif vollume_volntroler.desCnt==2: 
                    print("12")                    
                    self.mode=2
                    self.air_mode = 2
                elif vollume_volntroler.desCnt==3:
                    print("13")
                    self.mode=3
            elif self.touch != 1 and self.mode == 2 and self.air_mode <= 1:
                self.air_mode += 1
            elif self.mode == 3:
                print("6")
                self.mode = 0
                self.air_mode = 0
            elif self.touch != 1 and self.mode <= 2:
                print("7")
                self.mode += 1
                if self.mode == 2:
                    self.air_mode = 1
                else:
                    self.air_mode = 0
            elif self.touch < 2 and self.air_mode == 0:
                print("8")
                self.touch += 1
                self.mode = 0
                self.air_mode = 0
            self.flag = 0
            Design.moveR = 0
            Design.moveL = 0
            Design.move = 0
            self.Xstartpos = self.cx2+(100*z)
        elif self.flag == 2:
            print("左へ")
            if self.air_mode == 2 and self.touch != 1 and self.mode == 2:
                self.air_mode -= 1
                print("1")
            elif self.mode == 3:
                self.mode -= 1
                self.air_mode = 2
            elif self.air_mode == 1:
                print("2")
                self.air_mode = 0
                self.mode = 1
            elif self.mode >= 1:
                print("3")
                self.mode -= 1
                self.air_mode = 0
            elif self.touch >= 1:
                print("4")
                self.touch -= 1
                self.mode = 0
                self.air_mode = 0
            elif self.touch == 0:
                print("5")
                self.touch += 1
            self.flag = 0
            Design.moveR = 0
            Design.moveL = 0
            Design.move = 0
            self.Xstartpos = self.cx2-(100*z)
    def redline(self,count):
        print("data番号:"+str(count))
        self.infreadNumber=count
        if self.touch == 0:
            # ser.write(str.encode(data[count]))
            print(data[count])
            self.feedback()
            print("okey")
        if self.touch == 2:
            if self.pretime == 0:
                self.pretime = 1
            closeTimeP = time.time()
            cv2.rectangle(img,(0,0),(wCam,hCam),(0,0,0),cv2.FILLED)
            cv2.circle(img,(wCam//2,hCam//2+100),250,(0,200,100),cv2.FILLED)
            cv2.circle(img,(wCam//2,hCam//2+100),250,white,10,lineType=cv2.LINE_8)
            cv2.putText(img, str("loading"), (wCam//2-200, hCam//2+150), cv2.FONT_HERSHEY_PLAIN,
                    7, (0, 0, 0), 14)
            cv2.putText(img, str("loading"), (wCam//2-200, hCam//2+150), cv2.FONT_HERSHEY_PLAIN,
                    7, (255, 0, 0), 10)
            # if self.pretime == 2:
            #     place = data[count]
            #     ser.write(str.encode('r'))
            #     while(True):
            #         self.pretime = 0
            #         closeTimeN = time.time()
            #         if closeTimeN - closeTimeP == 5.0:
            #             closeTimeN = 0
            #             closeTimeP = 0
            #             break
            #         if ser.in_waiting>0:
            #             data[count] = 0
            #             data[count] = ser.readline().strip().decode('UTF-8')
            #             print(data[count])
            #             if len(data[count]) >= 10:
            #                 print(data[count])
            #                 cv2.rectangle(img,(0,0),(wCam,hCam),(0,0,0),cv2.FILLED)
            #                 cv2.circle(img,(wCam//2,hCam//2+100),250,(200,0,100),cv2.FILLED)
            #                 cv2.circle(img,(wCam//2,hCam//2+100),250,(0,0,0),10,lineType=cv2.LINE_8)
            #                 self.state = 1
            #                 self.word = "RECEIVE!"
            #                 break
            #             if data[count] == 'NG':
            #                 self.state = 1
            #                 data[count] = place
            #                 self.word = "NOT FOUND!"
            #                 break
            #             elif data[count] == "PO":
            #                 print("no power")
            #                 self.state = 1
            #                 data[count] = place
            #                 self.word = "NO POWER"
            #                 break
    def feedback(self):
        if self.state == 1:
            if self.stateP == 0:
                self.stateP = time.time()
            self.stateN = time.time()
            self.stateT = self.stateN - self.stateP
            cv2.putText(img, self.word, (50, hCam//4), cv2.FONT_HERSHEY_COMPLEX,
                                    4, white,7,cv2.LINE_AA)
            cv2.putText(img, self.word, (50, hCam//4), cv2.FONT_HERSHEY_COMPLEX,
                                    4, (30, 30, 255),6,cv2.LINE_AA)

            if self.stateT >= 2.0:
                self.state = 0
                self.stateT,self.stateN,self.stateP = 0,0,0

class design_draw:
    def __init__(self):
        self.moji = (20,80,255)                          #文字(オレンジ)
        self.color = (80,150,200)                        #(ブラウン)
        self.railcolor = (80,150,200)                    #レール(モカ)
        self.BrownShape = (100,160,200)                  #円の影(モカ)
        self.BrownFront = (140,200,240)                  #円の表(ベージュ)
        #画面のモード表示用ボックス
        self.box_sx = wCam//2 - 170
        self.box_ex = wCam//2 + 170
        self.box_sy = 550
        self.box_ey = 660
        #スライドに対応した図の移動
        self.moveL = 0
        self.moveR = 0
        self.move = 0
        self.meter = 0
        self.meter1 = 0
    def select(self):
        cv2.rectangle(img,(self.box_sx,self.box_sy),(self.box_ex,self.box_ey),white,-1)
        cv2.rectangle(img,(self.box_sx,self.box_sy),(self.box_ex,self.box_ey),(100,100,100),3)
        cv2.putText(img, "infrared", (self.box_sx+70, ((self.box_sy+self.box_ey+15)//2)), cv2.FONT_HERSHEY_PLAIN, 3,white, 5)
        cv2.putText(img, "infrared", (self.box_sx+70, ((self.box_sy+self.box_ey+15)//2)), cv2.FONT_HERSHEY_PLAIN, 3,self.moji, 3)

        cv2.rectangle(img,(wCam//4,30),(3*wCam//4,370),self.railcolor,-1)
        cv2.circle(img,(wCam//4,200),170,self.railcolor,-1,cv2.FILLED)
        cv2.circle(img,(3*wCam//4,200),170,self.railcolor,-1,cv2.FILLED)

        cv2.circle(img,(wCam//4,200),150,self.BrownShape,-1,cv2.FILLED)
        cv2.putText(img, str("Send"), (wCam//4-103,160), cv2.FONT_HERSHEY_PLAIN, 4,
                        white, 7)
        cv2.putText(img, str("Send"), (wCam//4-103, 160), cv2.FONT_HERSHEY_PLAIN, 4,
                        self.moji, 5)
        cv2.circle(img,((3*wCam)//4,200),150,self.BrownShape,-1,cv2.FILLED)
        cv2.putText(img, str("Receive"), (3*wCam//4-103, 160), cv2.FONT_HERSHEY_PLAIN, 4,
                        white, 7)
        cv2.putText(img, str("Receive"), (3*wCam//4-103,160), cv2.FONT_HERSHEY_PLAIN, 4,
                        self.moji, 5)
        cv2.circle(img,(wCam//2+23*self.move,200),170,self.BrownShape,-1,cv2.FILLED)
        cv2.circle(img,(wCam//2+23*self.move,180),170,self.BrownFront,-1,cv2.FILLED)
    def chose_option(self):
        self.page("chose")
        self.back("BACK!")
        cv2.rectangle(img,(4*wCam//5+10*self.moveR,370),(wCam,530),self.railcolor,-1)

        if vollume_volntroler.desCnt==0:
            cv2.circle(img,(4*wCam//5+10*self.moveR,450),80,self.BrownShape,-1,cv2.FILLED)
            cv2.circle(img,(4*wCam//5+10*self.moveR,430),80,self.BrownFront,-1,cv2.FILLED)
            cv2.putText(img, str("TV"), (4*wCam//5-50+10*self.moveR,450), cv2.FONT_HERSHEY_PLAIN, 3,white, 5)
            cv2.putText(img, str("TV"), (4*wCam//5-50+10*self.moveR,450), cv2.FONT_HERSHEY_PLAIN, 3, self.moji, 3)
            cv2.circle(img,(wCam//6+10,180),140,self.BrownShape,-1,cv2.FILLED)
            cv2.putText(img, str("TV"), (wCam//6-100,180), cv2.FONT_HERSHEY_PLAIN, 3,(50,200,50), 3)
        else:
            cv2.circle(img,(wCam//6,200),140,self.BrownShape,-1,cv2.FILLED)
            cv2.circle(img,(wCam//6+10,180),140,self.BrownFront,-1,cv2.FILLED)
            cv2.putText(img, str("TV"), (wCam//6-100,180), cv2.FONT_HERSHEY_PLAIN, 3,white, 5)
            cv2.putText(img, str("TV"), (wCam//6-100,180), cv2.FONT_HERSHEY_PLAIN, 3,self.moji, 3)
        
        if vollume_volntroler.desCnt == 1:
            cv2.circle(img,(4*wCam//5+10*self.moveR,450),80,self.BrownShape,-1,cv2.FILLED)
            cv2.circle(img,(4*wCam//5+10*self.moveR,430),80,self.BrownFront,-1,cv2.FILLED)
            cv2.putText(img, str("AIR_C"), (4*wCam//5-80+10*self.moveR,450), cv2.FONT_HERSHEY_PLAIN, 3,white, 5)
            cv2.putText(img, str("AIR_C"), (4*wCam//5-80+10*self.moveR,450), cv2.FONT_HERSHEY_PLAIN, 3,self.moji, 3)
            cv2.circle(img,(2*wCam//5-10,300),130,self.BrownShape,-1,cv2.FILLED)
            cv2.putText(img, str("AIR_C"), (wCam//2-250,300), cv2.FONT_HERSHEY_PLAIN, 3,(50,200,50), 3)
        else:
            cv2.circle(img,(2*wCam//5-10,320),130,self.BrownShape,-1,cv2.FILLED)
            cv2.circle(img,(2*wCam//5-10,300),130,self.BrownFront,-1,cv2.FILLED)
            cv2.putText(img, str("AIR_C"), (wCam//2-250,300), cv2.FONT_HERSHEY_PLAIN, 3,white, 5)
            cv2.putText(img, str("AIR_C"), (wCam//2-250,300), cv2.FONT_HERSHEY_PLAIN, 3,self.moji, 3)
        
        if vollume_volntroler.desCnt == 2:
            cv2.circle(img,(4*wCam//5+10*self.moveR,450),80,self.BrownShape,-1,cv2.FILLED)
            cv2.circle(img,(4*wCam//5+10*self.moveR,430),80,self.BrownFront,-1,cv2.FILLED)
            cv2.putText(img, str("AIR_H"), (4*wCam//5-80+10*self.moveR,450), cv2.FONT_HERSHEY_PLAIN, 3,white, 5)
            cv2.putText(img, str("AIR_H"), (4*wCam//5-80+10*self.moveR,450), cv2.FONT_HERSHEY_PLAIN, 3,self.moji, 3)
            cv2.circle(img,(3*wCam//5+10,300),130,self.BrownShape,-1,cv2.FILLED)
            cv2.putText(img, str("AIR_H"), (wCam//2+50,300), cv2.FONT_HERSHEY_PLAIN, 3,(50,200,50), 3)
        else:
            cv2.circle(img,(3*wCam//5+10,320),130,self.BrownShape,-1,cv2.FILLED)
            cv2.circle(img,(3*wCam//5+10,300),130,self.BrownFront,-1,cv2.FILLED)
            cv2.putText(img, str("AIR_H"), (wCam//2+50,300), cv2.FONT_HERSHEY_PLAIN, 3,white, 5)
            cv2.putText(img, str("AIR_H"), (wCam//2+50,300), cv2.FONT_HERSHEY_PLAIN, 3,
                            self.moji, 3)

        if vollume_volntroler.desCnt == 3:
            cv2.circle(img,(4*wCam//5+10*self.moveR,450),80,self.BrownShape,-1,cv2.FILLED)
            cv2.circle(img,(4*wCam//5+10*self.moveR,430),80,self.BrownFront,-1,cv2.FILLED)
            cv2.putText(img, str("LIGHT"), (4*wCam//5-80+10*self.moveR,450), cv2.FONT_HERSHEY_PLAIN, 3,white, 5)
            cv2.putText(img, str("LIGHT"), (4*wCam//5-80+10*self.moveR,450), cv2.FONT_HERSHEY_PLAIN, 3,self.moji, 3)
            cv2.circle(img,(5*wCam//6,180),140,self.BrownShape,-1,cv2.FILLED)
            cv2.putText(img, str("LIGHT"), (wCam-wCam//6-120,180), cv2.FONT_HERSHEY_PLAIN, 3,(50,200,50), 3)
        else:
            cv2.circle(img,(5*wCam//6+10,200),140,self.BrownShape,-1,cv2.FILLED)
            cv2.circle(img,(5*wCam//6,180),140,self.BrownFront,-1,cv2.FILLED)
            cv2.putText(img, str("LIGHT"), (wCam-wCam//6-120,180), cv2.FONT_HERSHEY_PLAIN, 3,white, 5)
            cv2.putText(img, str("LIGHT"), (wCam-wCam//6-120,180), cv2.FONT_HERSHEY_PLAIN, 3,self.moji, 3)
    def TV(self):
        self.page("TV!")
        self.back("HOME")
        self.next("COOL")
    def cool(self):
        self.page("COOL")
        posGY,posGX = 390,wCam//2-50
        self.meter = 480
        self.meter1 = 330
        push = cv2.imread(image_path+"gu-.jpg")
        h2, w2, c2 = push.shape
        img[posGY:posGY+h2, posGX:posGX+w2] = push
        push1 = cv2.imread(image_path+"pa-.jpg")
        h2, w2, c2 = push1.shape
        img[posGY-150:posGY-150+h2, posGX:posGX+w2] = push1

        if finger.tmp == 0:
            self.meter -= int(45*finger.countingTime)
        if finger.tmp == 5:
            self.meter1 -= int(45*finger.countingTime)

        self.back("TV!",)
        self.next("HOT",)

        cv2.rectangle(img,(wCam//2+55,posGY),(wCam//2+65,480),(100,100,100),-1)
        cv2.rectangle(img,(wCam//2+55,self.meter),(wCam//2+65,480),(0,0,255),-1)
        cv2.putText(img, str("ON"), (wCam//2+35, 370), cv2.FONT_HERSHEY_PLAIN, 2,
                    (255, 255, 255), 2)
        cv2.rectangle(img,(wCam//2+55,posGY-150),(wCam//2+65,330),(100,100,100),-1)
        cv2.rectangle(img,(wCam//2+55,self.meter1),(wCam//2+65,330),(0,0,255),-1)
        cv2.putText(img, str("OFF"), (wCam//2+35, 220), cv2.FONT_HERSHEY_PLAIN, 2,
                    (255, 255, 255), 2)
    def hot(self):
        self.page("HEAT")
        posGY,posGX = 390,wCam//2-50
        self.meter = 480
        self.meter1 = 330
        push = cv2.imread(image_path+"gu-.jpg")
        h2, w2, c2 = push.shape
        img[posGY:posGY+h2, posGX:posGX+w2] = push
        push1 = cv2.imread(image_path+"pa-.jpg")
        h2, w2, c2 = push1.shape
        img[posGY-150:posGY-150+h2, posGX:posGX+w2] = push1

        if finger.tmp == 0:
            self.meter -= int(45*finger.countingTime)
        if finger.tmp == 5:
            self.meter1 -= int(45*finger.countingTime)

        self.back("COOL!")
        self.next("LIGHT!")

        cv2.rectangle(img,(wCam//2+55,posGY),(wCam//2+65,480),(100,100,100),-1)
        cv2.rectangle(img,(wCam//2+55,self.meter),(wCam//2+65,480),(0,0,255),-1)
        cv2.putText(img, str("ON"), (wCam//2+35, 370), cv2.FONT_HERSHEY_PLAIN, 2,
                    (255, 255, 255), 2)
        cv2.rectangle(img,(wCam//2+55,posGY-150),(wCam//2+65,330),(100,100,100),-1)
        cv2.rectangle(img,(wCam//2+55,self.meter1),(wCam//2+65,330),(0,0,255),-1)
        cv2.putText(img, str("OFF"), (wCam//2+35, 220), cv2.FONT_HERSHEY_PLAIN, 2,
                    (255, 255, 255), 2)
    def Light(self):
        self.page("LIGHT")
        posGY,posGX = 390,wCam//2-50
        self.meter = 480
        self.meter1 = 330
        push = cv2.imread(image_path+"gu-.jpg")
        h2, w2, c2 = push.shape
        img[posGY:posGY+h2, posGX:posGX+w2] = push
        push1 = cv2.imread(image_path+"pa-.jpg")
        h2, w2, c2 = push1.shape
        img[posGY-150:posGY-150+h2, posGX:posGX+w2] = push1

        if finger.tmp == 0:
            self.meter -= int(45*finger.countingTime)
        if finger.tmp == 5:
            self.meter1 -= int(45*finger.countingTime)
        self.back("HOT!")
        self.next("HOME!")

        cv2.rectangle(img,(wCam//2+55,posGY),(wCam//2+65,480),(100,100,100),-1)
        cv2.rectangle(img,(wCam//2+55,self.meter),(wCam//2+65,480),(0,0,255),-1)
        cv2.putText(img, str("ON"), (wCam//2+35, 370), cv2.FONT_HERSHEY_PLAIN, 2,
                    (255, 255, 255), 2)
        cv2.rectangle(img,(wCam//2+55,posGY-150),(wCam//2+65,330),(100,100,100),-1)
        cv2.rectangle(img,(wCam//2+55,self.meter1),(wCam//2+65,330),(0,0,255),-1)
        cv2.putText(img, str("OFF"), (wCam//2+35, 220), cv2.FONT_HERSHEY_PLAIN, 2,
                    (255, 255, 255), 2)
    def back(self,name):
        cv2.rectangle(img,(0,370),(wCam//5-20-10*self.moveL,530),self.railcolor,-1)
        # cv2.circle(img,(wCam//5-20-10*self.moveL,450),80,railcolor,-1,cv2.FILLED)
        cv2.circle(img,(wCam//5-20-10*self.moveL,450),80,self.BrownShape,-1,cv2.FILLED)
        cv2.circle(img,(wCam//5-20-10*self.moveL,430),80,self.BrownFront,-1,cv2.FILLED)
        cv2.putText(img, name, (wCam//5-85-10*self.moveL,450), cv2.FONT_HERSHEY_PLAIN, 3,
                        white, 5)
        cv2.putText(img, name, (wCam//5-85-10*self.moveL,450), cv2.FONT_HERSHEY_PLAIN, 3,
                        self.moji, 3)
    def next(self,name):
        cv2.rectangle(img,(4*wCam//5+10*self.moveR,370),(wCam,530),self.railcolor,-1)
        cv2.circle(img,(4*wCam//5+10*self.moveR,450),80,self.BrownShape,-1,cv2.FILLED)
        cv2.circle(img,(4*wCam//5+10*self.moveR,430),80,self.BrownFront,-1,cv2.FILLED)
        cv2.putText(img, name, (4*wCam//5-70+10*self.moveR,450), cv2.FONT_HERSHEY_PLAIN, 3,
                        white, 5)
        cv2.putText(img, name, (4*wCam//5-70+10*self.moveR,450), cv2.FONT_HERSHEY_PLAIN, 3,
                        self.moji, 3)
    def page(self,screenName):
        cv2.rectangle(img,(self.box_sx,self.box_sy),(self.box_ex,self.box_ey),white,-1)
        cv2.rectangle(img,(self.box_sx,self.box_sy),(self.box_ex,self.box_ey),(100,100,100),3)
        cv2.putText(img, screenName+Rimocon_cntroler.coment, (self.box_sx+50, ((self.box_sy+self.box_ey+15)//2)), cv2.FONT_HERSHEY_PLAIN, 3,white, 5)
        cv2.putText(img, screenName+Rimocon_cntroler.coment, (self.box_sx+50, ((self.box_sy+self.box_ey+15)//2)), cv2.FONT_HERSHEY_PLAIN, 3,self.moji, 3)

class finger_Detection():
    def __init__(self):
        self.countingTime = 0.0
        self.keepingTime = 0.0
        self.nowingTime = 0.0
        self.tmp = 0
        self.chox = 0
        self.choy = 0
        self.sepa = False
        self.count_number = 0
 
        self.tipIds = [4, 8, 12, 16, 20]  
    def counter(self,img,lmList,choX,choY):
        if Rimocon_cntroler.mode == 0:# and Rimocon_cntroler.air_chose == 0:
            self.chox,self.choy = 0,0
        if Rimocon_cntroler.air_mode == 0:# and Rimocon_cntroler.air_chose == 0:
            self.chox,self.choy = 0,0
        fingers = []
        #0か1か6か判定
        if lmList[self.tipIds[0]][1] > lmList[self.tipIds[0] - 1][1]:#親指が出ているか
            if lmList[self.tipIds[4]][2] > lmList[self.tipIds[4] - 2][2]:#小指がしまってあるか
                for id in range(0,6):
                    fingers.append(1)
            else:
                fingers.append(1)
        else:
            fingers.append(0)
        # 4 Fingers
        for id in range(1, 5):
            if lmList[self.tipIds[id]][2] < lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)      
        totalFingers = fingers.count(1)
        #指の数により番号をかえる
        self.count_number = 0
        for i in posY:
            for j in posX:
                if i == posY[0] and j == posX[1]:
                    self.count_number = 1
                    break
                if totalFingers == self.count_number:
                    if self.keepingTime == 0.0:
                        self.keepingTime = time.time()
                    self.nowingTime = time.time()
                    self.countingTime = self.nowingTime - self.keepingTime
                    if self.tmp != self.count_number or Rimocon_cntroler.length<=50*z:
                        self.nowingTime = 0
                        self.keepingTime = 0
                        self.countingTime = 0
                    if self.countingTime >= 2.0:
                        self.chox = j
                        self.choy = i
                        self.keepingTime = self.nowingTime
                        self.countingTime = 0
                        self.sepa = not self.sepa
                        print(self.chox,self.choy)
                    self.tmp = self.count_number
                self.count_number += 1
                if i == 200:
                    break

        cv2.circle(img, (1200, 700), 150, (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(totalFingers), (1120, 700), cv2.FONT_HERSHEY_PLAIN,
                    10, (255, 0, 0), 25)
        return self.chox,self.choy,self.sepa

class vollume():
    def __init__(self):
        self.flag = 0
        self.x1,self.y1 = 0,0
        self.x2,self.y2 = 0,0
        self.centerX2,self.centerY2 = 0,0
        self.count = [0]*4
        self.value = 0
        self.desCnt = 0
    def change_vol(self,angle2):
        if Rimocon_cntroler.mode != 0:
            cv2.circle(img, (wCam//2,700), 120, (0, 255, 0),cv2.FILLED)
            if Rimocon_cntroler.mode == 1:
                cv2.putText(img, str(self.count[Rimocon_cntroler.mode-1]), (wCam//2-40, 700), cv2.FONT_HERSHEY_PLAIN,
                            10, (255, 0, 0), 15)
            elif Rimocon_cntroler.mode == 2:
                cv2.putText(img, str(self.count[Rimocon_cntroler.air_mode]), (wCam//2-40, 700), cv2.FONT_HERSHEY_PLAIN,
                            10, (255, 0, 0), 15)
            elif Rimocon_cntroler.mode == 3:
                cv2.putText(img, str(self.count[Rimocon_cntroler.mode]), (wCam//2-40, 700), cv2.FONT_HERSHEY_PLAIN,
                            10, (255, 0, 0), 15)
        if self.flag == 0 and angle2 <= -30 and angle2 >= -90:
            print(angle2)
            self.flag = 1
        if self.flag == 1 and angle2 >= 0 and angle2 <= 60:
            print(angle2)
            self.flag = 2
        if self.flag == 2 and angle2 >= 90 and angle2 >= 150:
            print(angle2)
            self.flag = 3
        if self.flag == 3 and  angle2 >=  180 and angle2 <= 240:
            print(angle2)
            print("UP")
            if Rimocon_cntroler.mode == 0:
                self.desCnt += 1
            if self.desCnt == 4:
                self.desCnt = 0
            if Rimocon_cntroler.air_mode == 1:#coolモードだったら
                self.value = 15
            elif Rimocon_cntroler.air_mode == 2:#hotモードだったら
                self.value = 16
            elif Rimocon_cntroler.mode == 1:#テレビだったら
                self.value = 19
            elif Rimocon_cntroler.mode == 3: #電気だったら
                self.value = 11
            if Rimocon_cntroler.mode == 1:
                if self.count[Rimocon_cntroler.mode-1]<=4:
                    Rimocon_cntroler.redline(self.value)
                    self.count[Rimocon_cntroler.mode-1]+=1
                    Rimocon_cntroler.state = 1
                    Rimocon_cntroler.word = "UP"
                else:
                    Rimocon_cntroler.state = 1
                    Rimocon_cntroler.word = "CAN'T UP"
            elif Rimocon_cntroler.mode == 2:
                if self.count[Rimocon_cntroler.air_mode]<=4:
                    Rimocon_cntroler.redline(self.value)
                    self.count[Rimocon_cntroler.air_mode]+=1
                    Rimocon_cntroler.state = 1
                    Rimocon_cntroler.word = "UP"
                else:
                    Rimocon_cntroler.state = 1
                    Rimocon_cntroler.word = "CAN'T UP"
            elif Rimocon_cntroler.mode == 3:
                if self.count[Rimocon_cntroler.mode]<=4:
                    Rimocon_cntroler.redline(self.value)
                    self.count[Rimocon_cntroler.mode]+=1
                    Rimocon_cntroler.state = 1
                    Rimocon_cntroler.word = "UP"
                else:
                    Rimocon_cntroler.state = 1
                    Rimocon_cntroler.word = "CAN'T UP"
            print(self.value)
            print(Rimocon_cntroler.mode)
            self.flag = 0

        if self.flag == 0 and  angle2 >= 30 and angle2 <= 90:
            print(angle2)
            self.flag = 5 
        if self.flag == 5 and angle2 <= 0 and angle2 >= -60:
            print(angle2)
            self.flag = 6
        if self.flag == 6 and angle2 >= 210 and angle2 <= 270:
            print(angle2)
            self.flag =  7
        if self.flag == 7 and angle2 >= 120 and angle2 <= 180:
            print(angle2)
            print("DOWN")
            if Rimocon_cntroler.mode == 0:
                self.desCnt -= 1
            if self.desCnt == -1:
                self.desCnt = 3
            if Rimocon_cntroler.air_mode == 1:
                self.value = 17
            elif Rimocon_cntroler.air_mode == 2:
                self.value = 18
            elif Rimocon_cntroler.mode == 1:
                self.value = 20
            elif Rimocon_cntroler.mode == 3:
                self.value = 12
            print(self.value)
            if Rimocon_cntroler.mode == 1:
                if self.count[Rimocon_cntroler.mode-1]>=-4:
                    Rimocon_cntroler.redline(self.value)
                    self.count[Rimocon_cntroler.mode-1]-=1
                    Rimocon_cntroler.state = 1
                    Rimocon_cntroler.word = "DOWN"
                else:
                    Rimocon_cntroler.state = 1
                    Rimocon_cntroler.word = "CAN'T DOWN"
            elif Rimocon_cntroler.mode == 2:
                if self.count[Rimocon_cntroler.air_mode]>=-4:
                    Rimocon_cntroler.redline(self.value)
                    self.count[Rimocon_cntroler.air_mode]-=1
                    Rimocon_cntroler.state = 1
                    Rimocon_cntroler.word = "DOWN"
                else:
                    Rimocon_cntroler.state = 1
                    Rimocon_cntroler.word = "CAN'T DOWN"
            elif Rimocon_cntroler.mode == 3:
                if self.count[Rimocon_cntroler.mode]>=-4:
                    Rimocon_cntroler.redline(self.value)
                    self.count[Rimocon_cntroler.mode]-=1
                    Rimocon_cntroler.state = 1
                    Rimocon_cntroler.word = "DOWN"
                else:
                    Rimocon_cntroler.state = 1
                    Rimocon_cntroler.word = "CAN'T DOWN"
            self.flag = 0

        if self.flag == 1 and angle2 >= 225 and angle2 <= 240:
            self.flag = 0
        if self.flag == 2 and angle2 <= -20 and angle2 >= -45:
            self.flag = 0
        if self.flag == 3 and angle2 >= 45 and angle2 <= 70:
            self.flag = 0

        if self.flag == 5 and angle2 >= 110 and angle2 >= 135:
            self.flag = 0
        if self.flag == 6 and angle2 >= 20 and angle2 <= 45:
            self.flag  = 0 
        if self.flag == 7 and angle2 <= -45 and angle2 >= -70:
            self.flag = 0

path = "/Users/asanoryo/Desktop/ard/Gesture_Control/test.txt"
image_path = "/Users/asanoryo/Desktop/ard/Gesture_Control/FingerImages/"

with open(path,mode="r") as f1:
    i = 0
    data = f1.readlines()
    for datam in data:
        data[i] = datam.strip()
        i+=1
    print(i-1)

wCam,hCam = 1280, 720
cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

posX = [wCam//2-60,wCam//2,wCam//2+60]
posY = [300,400,460,520]
choX,choY,SEPA = 0,0,False
aposX, aposY = 950,100
y = 0
count = 1
z1,z2,z = 0,0,0
OnOff = 1

# ser = serial.Serial('/dev/cu.usbmodem14201', 57600, timeout=6.0)

white = (255,255,255)
HandDetector = htm.handDetector()               #手認識
finger = finger_Detection()                     #手数字
vollume_volntroler = vollume()                  #サイクルシステム
Rimocon_cntroler = Rimote_Controler()           #リモコン
Design = design_draw()                          #デザイン(TV,AIR,LIGHT)

while True:
    # time.sleep(1e-2)
    #loading_mode
    if Rimocon_cntroler.pretime == 1:
        Rimocon_cntroler.pretime += 1
        Rimocon_cntroler.redline(Rimocon_cntroler.infreadNumber)
    success,img = cap.read()
    img = HandDetector.findHands(img)#21個の点と点を結ぶ線を描画
    img = cv2.flip(img,1)
    if success == False:
        cap.release()
        cv2.destroyAllWindows()
        break
    if OnOff == 1:
        cv2.rectangle(img,(0,0),(wCam,hCam),(170,220,255),thickness=-1)
        if Rimocon_cntroler.touch == 1:
            Design.select()
        elif Rimocon_cntroler.mode == 0:
            Design.chose_option()
        elif Rimocon_cntroler.mode == 1:
            Design.TV()
        elif Rimocon_cntroler.mode == 2 and Rimocon_cntroler.air_mode == 1:
            Design.cool()
        elif Rimocon_cntroler.mode == 2 and Rimocon_cntroler.air_mode == 2:
            Design.hot()
        elif Rimocon_cntroler.mode  == 3:
            Design.Light()
        cv2.circle(img,(wCam//6,620),45,(0,250,0),cv2.FILLED)
        absolute = cv2.imread(image_path + "kitune.jpg")
        h,w,c = absolute.shape
        img[560:560+h,30:30+w] = absolute
    else:
        cv2.rectangle(img,(0,0),(wCam,hCam),(0,0,0),thickness=-1)
        cv2.circle(img,(wCam//6,620),45,(0,0,250),cv2.FILLED)
        absolute = cv2.imread(image_path + "black.jpg")
        h,w,c = absolute.shape
        img[560:560+h,30:30+w] = absolute

    lmList = HandDetector.findPosition(img,draw = False)#21個の点の場所を認識

    if len(lmList) != 0:
        Rimocon_cntroler.position(lmList)
        if Rimocon_cntroler.LockTime > 3.0:
                Rimocon_cntroler.LockTime = 0
                Rimocon_cntroler.lockP = 0
                Rimocon_cntroler.lockC = 0 
                OnOff = not OnOff
        #手の画面からの距離をaveW,aveH（基本値)と比べた時の割合.遠ければ小,近ければ大
        z1 = Rimocon_cntroler.Whand/Rimocon_cntroler.aveW
        z2 = Rimocon_cntroler.Hhand/Rimocon_cntroler.aveH
        z = (z1+z2)/2
        if OnOff == 1:
            #ショートカット(ホーム画面):親指と人差し指がくっついていて,かつ中指からの距離が150離れていれば
            if Rimocon_cntroler.length1 <= 40*z and math.hypot(Rimocon_cntroler.cx1 - Rimocon_cntroler.x3,Rimocon_cntroler.cy1 - Rimocon_cntroler.y3) >= int(150*z):
                    Rimocon_cntroler.touch = 1
                    Rimocon_cntroler.mode = 0
                    Rimocon_cntroler.air_mode = 0
                    choX = 0
                    choY = 0
                    cv2.circle(img,(Rimocon_cntroler.cx1,Rimocon_cntroler.cy1),20,(0,0,255),cv2.FILLED)
            if Rimocon_cntroler.y3 <= Rimocon_cntroler.y5 and Rimocon_cntroler.length2 <= 60*z:
                finger.countingTime = 0
                finger.keepingTime = 0
                finger.nowingTime = 0
                Rimocon_cntroler.vol = 0
                if Rimocon_cntroler.startSlide == 0:
                    Rimocon_cntroler.startSlide = 1
                Rimocon_cntroler.slide(lmList)
            elif Rimocon_cntroler.vol != 1:
                choX,choY,SEPA = finger.counter(img,lmList,choX,choY)
                cv2.circle(img,(Rimocon_cntroler.cx1,Rimocon_cntroler.cy1),5,(0,0,255),cv2.FILLED)
                cv2.circle(img,(Rimocon_cntroler.cx2,Rimocon_cntroler.cy2),5,(0,0,255),cv2.FILLED)
                cv2.circle(img,(Rimocon_cntroler.cx3,Rimocon_cntroler.cy3),5,(0,0,255),cv2.FILLED)
                Design.moveR = 0
                Design.moveL = 0
                Design.move = 0
                Rimocon_cntroler.flag = 0
                Rimocon_cntroler.startSlide = 0
    else:
        finger.nowingTime = 0
        finger.keepingTime = 0
        finger.countingTime = 0
        
    Rimocon_cntroler.change_mode(img,lmList,choX,choY,SEPA)
    Rimocon_cntroler.kiri = SEPA
    Rimocon_cntroler.feedback()
    Rimocon_cntroler.fpslevel()
    
    if Rimocon_cntroler.touch == 2:
        count = 0
    if Rimocon_cntroler.touch != 2 and count == 0:
        count = 1
        with open(path,mode='w') as f:
            for i in data:
                f.write("{}".format(i))
                f.write("\n")

    cv2.imshow("Image",img)
    k = cv2.waitKey(2) & 0xff
    if k == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break
# ser.close()