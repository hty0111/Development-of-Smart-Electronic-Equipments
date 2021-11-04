import RPi.GPIO as GPIO

CHANNEL = 16    # 初始化引脚，将16号引脚设置为输入下拉
GPIO.setmode(GPIO.BCM)      # 选择引脚系统
GPIO.setup(CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# 带有异常处理的主程序
try:
    while True:     # 执行一个while死循环
        status = GPIO.input(CHANNEL)  # 检测16号引脚口的输入高低电平状态
        if status:  # 如果为高电平，说明MQ-2正常
            print("yes")
        else:    # 如果为低电平，说明MQ-2检测到有害气体
            print("dangerous")
except KeyboardInterrupt:   # 异常处理
    GPIO.cleanup()  # 清理运行完成后的残余

