import os
import sys
sys.path.append('/home/pi/')
import togikai_drive
import togikai_ultrasonic
import signal
import RPi.GPIO as GPIO
import Adafruit_PCA9685
import time
import numpy as np

# GPIOピン番号の指示方法
GPIO.setmode(GPIO.BOARD)

# #超音波センサ初期設定
# # Triger -- Fr:15, FrLH:23, RrLH:27, FrRH:32, RrRH:36
# t_list=[15,23,27,20,5]
# GPIO.setup(t_list,GPIO.OUT,initial=GPIO.LOW)
# # Echo -- Fr:26, FrLH:24, RrLH:37, FrRH:31, RrRH:38
# e_list=[14,24,17,21,6]

#超音波センサ初期設定
# Triger -- Fr:15, FrLH:38, RrLH:16, FrRH:32, RrRH:36
t_list=[10,16,13,38,29]
GPIO.setup(t_list,GPIO.OUT,initial=GPIO.LOW)
# Echo -- Fr:26, FrLH:40, RrLH:18, FrRH:31, RrRH:38
e_list=[8,18,11,40,31]

GPIO.setup(e_list,GPIO.IN)

#PWM制御の初期設定
##モータドライバ:PCA9685のPWMのアドレスを設定
pwm = Adafruit_PCA9685.PCA9685(address=0x40)
##動作周波数を設定
pwm.set_pwm_freq(60)

#アライメント調整済みPWMパラメータ読み込み
PWM_PARAM = togikai_drive.ReadPWMPARAM(pwm)

#Gard 210523
#Steer Right
if PWM_PARAM[0][0] - PWM_PARAM[0][1] >= 100: #No change!
    PWM_PARAM[0][0] = PWM_PARAM[0][1] + 100  #No change!
    
#Steer Left
if PWM_PARAM[0][1] - PWM_PARAM[0][2] >= 100: #No change!
    PWM_PARAM[0][2] = PWM_PARAM[0][1] - 100  #No change!


#パラメータ
#前壁との最小距離
#Cshort = 30
Cshort = 20
#右左折判定基準
short = 70
#左右リアセンサー反応距離（追加）
Rshort = 30
#モーター出力
FORWARD_S = 100 #<=100
FORWARD_C = 80 #<=100
REVERSE = -60 #<=100
#Stear
LEFT = 99 #<=100
RIGHT = -99 #<=100
#データ記録用配列作成
d = np.zeros(6)
#操舵、駆動モーターの初期化
togikai_drive.Accel(PWM_PARAM,pwm,time,0)
togikai_drive.Steer(PWM_PARAM,pwm,time,0)

#一時停止（Enterを押すとプログラム実行開始）
print('Press any key to continue')
input()

#開始時間
start_time = time.time()

#ここから走行用プログラム
try:
    while True:
        #Frセンサ距離
        Cdis = togikai_ultrasonic.Mesure(GPIO,time,10,8)
        #FrLHセンサ距離
        FLdis = togikai_ultrasonic.Mesure(GPIO,time,16,18)
        #FrRHセンサ距離
        FRdis = togikai_ultrasonic.Mesure(GPIO,time,13,11)
        #RrLHセンサ距離
        BLdis = togikai_ultrasonic.Mesure(GPIO,time,38,40)
        #RrRHセンサ距離
        BRdis = togikai_ultrasonic.Mesure(GPIO,time,29,31)

        if Cdis >= Cshort:
            if(BLdis > 77):
                togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
                togikai_drive.Steer(PWM_PARAM,pwm,time,LEFT)
                print('左です')
            # if(BLdis < 15  and  FLdis < 90):
            if((BLdis < 15  and  FLdis < 90) or (BLdis < 15  and  FRdis > 60)) :
                togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
                togikai_drive.Steer(PWM_PARAM,pwm,time,RIGHT)
                print('\033[92m' + '右です'+'\033[0m')
            elif FLdis -20 <= short and FRdis >= short:
               togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
               togikai_drive.Steer(PWM_PARAM,pwm,time,RIGHT) #original = "+"
               print('\033[92m'+"右旋回1"+'\033[0m')     
            # elif short < FLdis  -10  and FRdis < short: 
            elif short < FLdis  and FRdis < short: 
                #add
                if(Cdis>180):
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
                    togikai_drive.Steer(PWM_PARAM,pwm,time,0)
                    print('\033[94m'+"直進中前空き"+'\033[0m')
                else:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
                    togikai_drive.Steer(PWM_PARAM,pwm,time,LEFT) #original = "-"
                    print('\033[93m'+"左旋回1"+'\033[0m')
                #add-end
            #追加
            elif BLdis  <= Rshort and BRdis >= Rshort:
               togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
               togikai_drive.Steer(PWM_PARAM,pwm,time,RIGHT) #original = "+"
               print('\033[92m'+"右旋回2"+'\033[0m')     

            # elif BLdis  > Rshort and BRdis < Rshort:
            elif BLdis + 10 > Rshort and BRdis < Rshort:
               togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
               togikai_drive.Steer(PWM_PARAM,pwm,time,LEFT) #original = "-"
               print('\033[93m'+"左旋回2"+'\033[0m')
            #追加ここまで
            elif FLdis < short and FRdis < short:
                # if (FLdis - FRdis)>: 10
                if (FLdis - FRdis)> 15: 
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
                    togikai_drive.Steer(PWM_PARAM,pwm,time,LEFT) #original = "-"
                    print('\033[93m'+"左旋回3"+'\033[0m')   
                elif(FRdis - FLdis) > 10:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
                    togikai_drive.Steer(PWM_PARAM,pwm,time,RIGHT) #original = "+"
                    print('\033[92m'+"右旋回3"+'\033[0m')                
                else:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
                    togikai_drive.Steer(PWM_PARAM,pwm,time,0)
                    print('\033[94m'+"直進中1"+'\033[0m')
            else:
                if(Cdis > 200):
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_S)
                    togikai_drive.Steer(PWM_PARAM,pwm,time,0)
                    print('\033[94m'+"速い直進"+'\033[0m')
                else:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_S)
                    togikai_drive.Steer(PWM_PARAM,pwm,time,0)
                    print('\033[94m'+"直進中2"+'\033[0m')     
        elif time.time()-start_time < 1:
            pass
        else:
            togikai_drive.Accel(PWM_PARAM,pwm,time,REVERSE)
            #togikai_drive.Accel(PWM_PARAM,pwm,time,0) #Stop if something is in front of you
            togikai_drive.Steer(PWM_PARAM,pwm,time,0)
            time.sleep(0.1)
            togikai_drive.Accel(PWM_PARAM,pwm,time,0)
            togikai_drive.Steer(PWM_PARAM,pwm,time,0)
            GPIO.cleanup()
            d = np.vstack([d,[time.time()-start_time, Cdis, FRdis, FLdis, BRdis, BLdis]])
            np.savetxt('/home/pi/code/record_data.csv', d, fmt='%.3e')
            print('Stop!')
            break
        #距離データを配列に記録
        d = np.vstack([d,[time.time()-start_time, Cdis, FRdis, FLdis, BRdis, BLdis]])
        #距離を表示
        print('BL:{0:.1f} , FL:{1:.1f} , C:{2:.1f}, FR:{3:.1f} , BR:{4:.1f}'.format(BLdis,FLdis,Cdis,FRdis,BRdis))
        # time.sleep(0.05)
        time.sleep(0.03)

except KeyboardInterrupt:
    print('stop!')
    np.savetxt('/home/pi/code/record_data.csv', d, fmt='%.3e')
    togikai_drive.Accel(PWM_PARAM,pwm,time,0)
    togikai_drive.Steer(PWM_PARAM,pwm,time,0)
    GPIO.cleanup()
