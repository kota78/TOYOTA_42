import os
import sys
sys.path.append('/home/pi/togikai/togikai_function/')
import togikai_drive
import togikai_ultrasonic
import signal
import RPi.GPIO as GPIO
import Adafruit_PCA9685
import time
import numpy as np

# GPIOピン番号の指示方法
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BOARD)

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

#モーター出力
FORWARD_S = 70 #<=100
FORWARD_C = 70 #<=100
REVERSE = -60 #<=100
#Stear
LEFT = 90 #<=100
RIGHT = -90 #<=100
#操舵、駆動モーターの初期化
togikai_drive.Accel(PWM_PARAM,pwm,time,0)
togikai_drive.Steer(PWM_PARAM,pwm,time,0)

#一時停止（Enterを押すとプログラム実行開始）
print('Press any key to continue')
input()

#ここから走行用プログラム
while True:
	x = input()
        
	if x == 'd':
           togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
           togikai_drive.Steer(PWM_PARAM,pwm,time,RIGHT) #original = "+"
           comment = "右旋回"
	elif x == 'a':
           togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
           togikai_drive.Steer(PWM_PARAM,pwm,time,LEFT) #original = "-"
           comment = "左旋回"
	elif x == 'w':
            togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_S)
            togikai_drive.Steer(PWM_PARAM,pwm,time,0)
            comment = "直進中"
	else:
			comment = "停止"
			togikai_drive.Accel(PWM_PARAM,pwm,time,0)
			togikai_drive.Steer(PWM_PARAM,pwm,time,0)
			GPIO.cleanup()
			break
	time.sleep(0.05)
