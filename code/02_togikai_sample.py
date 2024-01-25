import os
import sys
sys.path.append('/home/pi')
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
Rlong=60
#減速する基準
Dshort = 70
#モーター出力
FORWARD_S = 70 #<=100
FORWARD_C = 30 #<=100
REVERSE = -60 #<=100
#Stear
LEFT = 90 #<=100
RIGHT = -90 #<=100
SLEFT = 30
SRIGHT = -30
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
        FRdis = togikai_ultrasonic.Mesure(GPIO,time,10,8)
        #FrLHセンサ距離
        LHdis = togikai_ultrasonic.Mesure(GPIO,time,16,18)
        #FrRHセンサ距離
        RHdis = togikai_ultrasonic.Mesure(GPIO,time,13,11)
        #RrLHセンサ距離
        RLHdis = togikai_ultrasonic.Mesure(GPIO,time,38,40)
        #RrRHセンサ距離
        RRHdis = togikai_ultrasonic.Mesure(GPIO,time,29,31)

        if FRdis >= Cshort:
            #前がDshortより近づいたらduty比を変更
            if(FRdis<70):
                FORWARD_C = 70
                print('\033[92m'+"slow"+'\033[0m')     
            elif(70 <= FRdis and FRdis <170):
                FORWARD_C = 70
                print('\033[92m'+"normal"+'\033[0m')     
            else:
                FORWARD_C = 70
                print('\033[92m'+"fast"+'\033[0m')     
            if LHdis -20 <= short and RHdis >= short:
               togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
               togikai_drive.Steer(PWM_PARAM,pwm,time,SRIGHT) #original = "+"
               print('\033[92m'+"右旋回1"+'\033[0m')     
            elif LHdis > short and RHdis < short:
               togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
               togikai_drive.Steer(PWM_PARAM,pwm,time,SLEFT) #original = "-"
               print('\033[93m'+"左旋回1"+'\033[0m')
            #追加
            #左が近づいたら
            elif RLHdis  <= Rshort and RRHdis >= Rshort:
               togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
               togikai_drive.Steer(PWM_PARAM,pwm,time,RIGHT) #original = "+"
               print('\033[92m'+"右旋回2"+'\033[0m')   
            #左が遠ざかったら
           # elif RLHdis  >= Rlong and RRHdis >= Rshort:
            #   togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
             #  togikai_drive.Steer(PWM_PARAM,pwm,time,SLEFT) #original = "+"
              # print('\033[92m'+"ちょい左旋回"+'\033[0m')   
            #右が近づいたら
            elif RLHdis > Rshort and RRHdis < Rshort:
               togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
               togikai_drive.Steer(PWM_PARAM,pwm,time,LEFT) #original = "-"
               print('\033[93m'+"左旋回2"+'\033[0m')
            #追加ここまで
            elif LHdis < short and RHdis < short:
                if (LHdis - RHdis)>10:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
                    togikai_drive.Steer(PWM_PARAM,pwm,time,LEFT) #original = "-"
                    print('\033[93m'+"左旋回3"+'\033[0m')   
                elif(RHdis - LHdis) > 10:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
                    togikai_drive.Steer(PWM_PARAM,pwm,time,RIGHT) #original = "+"
                    print('\033[92m'+"右旋回3"+'\033[0m')                
                else:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
                    togikai_drive.Steer(PWM_PARAM,pwm,time,0)
                    print('\033[94m'+"直進中1"+'\033[0m')
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
            d = np.vstack([d,[time.time()-start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis]])
            np.savetxt('/home/pi/code/record_data.csv', d, fmt='%.3e')
            print('Stop!')
            break
        #距離データを配列に記録
        d = np.vstack([d,[time.time()-start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis]])
        #距離を表示
        print('Fr:{0:.1f} , FrRH:{1:.1f} , FrLH:{2:.1f}, RrRH:{3:.1f} , RrLH:{4:.1f}'.format(FRdis,RHdis,LHdis,RRHdis,RLHdis))
        # time.sleep(0.05)
        time.sleep(0.05)

except KeyboardInterrupt:
    print('stop!')
    np.savetxt('/home/pi/code/record_data.csv', d, fmt='%.3e')
    togikai_drive.Accel(PWM_PARAM,pwm,time,0)
    togikai_drive.Steer(PWM_PARAM,pwm,time,0)
    GPIO.cleanup()
