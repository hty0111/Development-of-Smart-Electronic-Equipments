import RPi.GPIO as GPIO
import time
import socket

print("Server open.")
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#设置IP和端口
host = '192.168.43.183'
port = 7000
#bind绑定该端口
mySocket.bind((host, port))
mySocket.listen(10)
# 接收客户端连接
client, address = mySocket.accept()
print("新连接")
print("IP is %s" % address[0])
print("port is %d\n" % address[1])

DHTPIN = 17

GPIO.setmode(GPIO.BCM)

MAX_UNCHANGE_COUNT = 100

STATE_INIT_PULL_DOWN = 1
STATE_INIT_PULL_UP = 2
STATE_DATA_FIRST_PULL_DOWN = 3
STATE_DATA_PULL_UP = 4
STATE_DATA_PULL_DOWN = 5


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

	return the_bytes[0], the_bytes[2]


def main():
	while True:
		result = read_dht11_dat()
		humidity, temperature = result
		time.sleep(1)

		# 发送消息
		if result == (0, 0):
			continue

		client.send(('humidity: ' + str(humidity)).encode())
		client.send(('temperature: ' + str(temperature)).encode())


def destroy():
	GPIO.cleanup()


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		destroy()


