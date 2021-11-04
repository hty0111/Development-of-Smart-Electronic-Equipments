import socket

print("客户端开启")
# 套接字接口
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 设置ip和端口
host = '192.168.43.192'
# host = 'localhost'
port = 9000

try:
    mySocket.connect((host, port))  # 连接到服务器
    print("连接到服务器")
except KeyboardInterrupt:
    print('连接不成功')

while True:
    # 接收消息
    res_msg = mySocket.recv(2048).decode()
    print(res_msg)
