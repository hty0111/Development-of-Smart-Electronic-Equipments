from PySide2.QtWidgets import QApplication, QTextBrowser, QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
from threading import Thread, Lock
from PySide2.QtCore import Signal, QObject
from time import sleep
import socket


class MySignals(QObject):
    text_print = Signal(QTextBrowser, str)


print_ms = MySignals()


class MySignals(QObject):
    show_boom_warrning = Signal()
    show_fire_warrning = Signal()
    show_smog_warrning = Signal()


warn_ms = MySignals()
block = Lock()
flag = 0

class Stats:

    def __init__(self):
        qtmp = QFile("main.ui")
        qtmp.open(QFile.ReadOnly)
        qtmp.close()
        self.ui = QUiLoader().load(qtmp)

        self.ui.pushButton.clicked.connect(self.showLabState)

        print_ms.text_print.connect(self.printToGui)
        warn_ms.show_fire_warrning.connect(self.fire_warrning)
        warn_ms.show_boom_warrning.connect(self.boom_warrning)
        warn_ms.show_smog_warrning.connect(self.smog_warrning)

    def printToGui(self, fb, text):
        fb.append(str(text))
        fb.ensureCursorVisible()

    def showLabState(self):
        def threadFunc():   # 接口函数
            print_ms.text_print.emit(self.ui.infoBox1, "客户端开启")
            # 套接字接口
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 设置ip和端口
            host = '192.168.43.192'
            # host = 'localhost'
            port = 9000
            try:
                mySocket.connect((host, port))  # 连接到服务器
                print_ms.text_print.emit(self.ui.infoBox1, "连接到服务器")
            except KeyboardInterrupt:
                print_ms.text_print.emit(self.ui.infoBox1, "连接不成功")

            while True:
                # 接收消息
                msg = mySocket.recv(2048).decode()
                humidity = int(msg[0:2])
                temperature = int(msg[2:4])
                is_smog = int(msg[4])
                is_boom = int(msg[5])
                is_fire = int(msg[6])
                if not is_boom and not is_fire and not is_smog:
                    print_ms.text_print.emit(self.ui.infoBox1, "Humidity: "+str(humidity)+"%   Temperature: "+str(temperature)
                                             +"°C   The lab is safe.")
                else:
                    block.acquire()
                    if is_boom == 1:
                        warn_ms.show_boom_warrning.emit()
                    elif is_fire == 1:
                        warn_ms.show_fire_warrning.emit()
                    elif is_smog == 1:
                        warn_ms.show_smog_warrning.emit()
                    block.release()

                sleep(0.1)

        self.thread = Thread(target=threadFunc)
        self.thread.start()

    def task2(self):
        def threadFunc():
            print_ms.text_print.emit(self.ui.infoBox2, '输出内容')

        thread = Thread(target=threadFunc)
        thread.start()

    def fire_warrning(self):
        QMessageBox.about(self.ui, '警告', f'''发生火灾！\n''')
    def boom_warrning(self):
        QMessageBox.about(self.ui, '警告', f'''发生爆炸！\n''')
    def smog_warrning(self):
        QMessageBox.about(self.ui, '警告', f'''有毒气体泄露！\n''')


if __name__ == '__main__':
    app = QApplication([])
    stats1 = Stats()
    stats1.ui.show()
    app.exec_()