import RPi.GPIO as GPIO  # 导入库，并进行别名的设置
import time
import socket
import serial

# 建立TCP连接
print("Server open.")
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 设置IP和端口
host = '10.192.139.196'
port = 9000
# bind绑定该端口
mySocket.bind((host, port))
mySocket.listen(10)
# 接收客户端连接
client, address = mySocket.accept()
print("新连接")
print("IP is %s" % address[0])
print("port is %d\n" % address[1])

# 温度
DHTPIN = 17
GPIO.setmode(GPIO.BCM)
MAX_UNCHANGE_COUNT = 100
STATE_INIT_PULL_DOWN = 1
STATE_INIT_PULL_UP = 2
STATE_DATA_FIRST_PULL_DOWN = 3
STATE_DATA_PULL_UP = 4
STATE_DATA_PULL_DOWN = 5

# 有毒气体
CHANNEL = 16  # 确定引脚口。按照真实的位置确定
GPIO.setup(CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# 初始化引脚，将16号引脚设置为输入下拉电阻，因为在初始化的时候不确定的的引电平，因此这样设置是用来保证精准

# 声音
GPIO.setwarnings(False)
GPIO.setup(4, GPIO.IN)

# 火焰
pin_fire = 24
GPIO.setup(pin_fire, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# 蜂鸣器
BuzzerPin = 27
GPIO.setup(BuzzerPin, GPIO.OUT)


def read_dht11_dat():
    GPIO.setup(DHTPIN, GPIO.OUT)
    GPIO.output(DHTPIN, GPIO.HIGH)
    time.sleep(0.05)
    GPIO.output(DHTPIN, GPIO.LOW)
    time.sleep(0.02)
    GPIO.setup(DHTPIN, GPIO.IN, GPIO.PUD_UP)

    unchanged_count = 0
    last = -1
    data = []
    while True:
        current = GPIO.input(DHTPIN)
        data.append(current)
        if last != current:
            unchanged_count = 0
            last = current
        else:
            unchanged_count += 1
            if unchanged_count > MAX_UNCHANGE_COUNT:
                break

    state = STATE_INIT_PULL_DOWN

    lengths = []
    current_length = 0

    for current in data:
        current_length += 1

        if state == STATE_INIT_PULL_DOWN:
            if current == GPIO.LOW:
                state = STATE_INIT_PULL_UP
            else:
                continue
        if state == STATE_INIT_PULL_UP:
            if current == GPIO.HIGH:
                state = STATE_DATA_FIRST_PULL_DOWN
            else:
                continue
        if state == STATE_DATA_FIRST_PULL_DOWN:
            if current == GPIO.LOW:
                state = STATE_DATA_PULL_UP
            else:
                continue
        if state == STATE_DATA_PULL_UP:
            if current == GPIO.HIGH:
                current_length = 0
                state = STATE_DATA_PULL_DOWN
            else:
                continue
        if state == STATE_DATA_PULL_DOWN:
            if current == GPIO.LOW:
                lengths.append(current_length)
                state = STATE_DATA_PULL_UP
            else:
                continue

    if len(lengths) != 40:
        return 0, 0

    shortest_pull_up = min(lengths)
    longest_pull_up = max(lengths)
    halfway = (longest_pull_up + shortest_pull_up) / 2
    bits = []
    the_bytes = []
    byte = 0

    for length in lengths:
        bit = 0
        if length > halfway:
            bit = 1
        bits.append(bit)
    # print ("bits: %s, length: %d" % (bits, len(bits)) )
    for i in range(0, len(bits)):
        byte = byte << 1
        if bits[i]:
            byte = byte | 1
        else:
            byte = byte | 0
        if (i + 1) % 8 == 0:
            the_bytes.append(byte)
            byte = 0

    checksum = (the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3]) & 0xFF
    if the_bytes[4] != checksum:
        return 0, 0
dddddddddddddddddddddddddddddddddddd
    return the_bytes[0], the_bytes[2]


def main():
    while True:
        send_msg = ''


        # 温度
        result = read_dht11_dat()
        humidity, temperature = result

        if result == (0, 0):
            continue
        # client.send(('Humidity: ' + str(humidity)).encode())
        send_msg = str(humidity) + str(temperature)
        # print(send_msg)
        # client.send(f'{humidity}'.encode())
        # client.send(('Temperature: ' + str(temperature)).encode())
        # client.send(f'{temperature}'.encode())
        # client.send(send_msg.encode())
        if temperature > 100:
            tem_flag = 1
        else:
            tem_flag = 0

        # path = "/dev/ttAMA0"  # 路径
        # baud_rate = 115200  # 波特率
        # com = serial.Serial(path, baud_rate)
        # send_msg = com.write("1234")

        # 有毒气体
        status = GPIO.input(CHANNEL)
        if status:  # 如果为高电平，说明MQ-2正常，并打印“OK”
            # client.send('\nNormal gas\n'.encode())
            send_msg += '0'
            # client.send('0'.encode())
            gas_flag = 0
        else:       # 如果为低电平，说明MQ-2检测到有害气体，并打印“dangerous”
            # client.send('\nDangerous gas\n'.encode())
            send_msg += '1'
            # client.send('1'.encode())
            gas_flag = 1

        # 声音
        if GPIO.input(4):
            # client.send('Normal voice\n'.encode())
            send_msg += '0'
            # client.send('0'.encode())
            voice_flag = 0
        else:
            # client.send('Loud voice\n'.encode())
            send_msg += '1'
            # client.send('1'.encode())
            voice_flag = 1

        # 火焰
        status = GPIO.input(pin_fire)
        if status:
            # client.send('No fire\n'.encode())
            send_msg += '0'
            # client.send('0'.encode())
            fire_flag = 0
        else:
            # client.send('Fire!!!!\n'.encode())
            send_msg += '1'
            # client.send('1'.encode())
            fire_flag = 1

        client.send(send_msg.encode())
        if tem_flag or gas_flag or voice_flag or fire_flag:
            GPIO.output(BuzzerPin, GPIO.HIGH)
        else:
            GPIO.output(BuzzerPin, GPIO.LOW)


def destroy():
    GPIO.output(BuzzerPin, GPIO.LOW)
    GPIO.cleanup()


if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError:
        destroy()


