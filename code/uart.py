import serial

path = "/dev/ttAMA0"    # 路径
baud_rate = 115200      # 波特率
com = serial.Serial(path, baud_rate)
send_msg = com.write("1234")

