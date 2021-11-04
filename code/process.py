from PySide2.QtWidgets import QApplication, QTextBrowser
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
from threading import Thread
from PySide2.QtCore import Signal, QObject
from time import sleep

# 自定义信号源对象类型，一定要继承自 QObject
class MySignals(QObject):
    # 定义一种信号，两个参数on 类型分别是： QTextBrowser 和 字符串
    # 调用 emit方法 发信号时，传入参数 必须是这里指定的 参数类型
    text_print = Signal(QTextBrowser, str)

    # 还可以定义其他种类的信号
    update_table = Signal(str)


# 实例化
global_ms = MySignals()


class Stats:

    def __init__(self):
        qtmp = QFile("main.ui")
        qtmp.open(QFile.ReadOnly)
        qtmp.close()
        self.ui = QUiLoader().load(qtmp)

        self.ui.pushButton.clicked.connect(self.showLabState)
        # 自定义信号的处理函数
        global_ms.text_print.connect(self.printToGui)

    def printToGui(self, fb, text):
        fb.append(str(text))
        fb.ensureCursorVisible()

    def showLabState(self):
        def threadFunc():
            # 通过Signal 的 emit 触发执行 主线程里面的处理函数
            # emit参数和定义Signal的数量、类型必须一致
            for i in range(1, 101):
                global_ms.text_print.emit(self.ui.infoBox1, str(i))
                sleep(0.5)

        self.thread = Thread(target=threadFunc)
        self.thread.start()

    def task2(self):
        def threadFunc():
            global_ms.text_print.emit(self.ui.infoBox2, '输出内容')

        thread = Thread(target=threadFunc)
        thread.start()

if __name__ == '__main__':
    app = QApplication([])
    stats1 = Stats()
    stats1.ui.show()
    app.exec_()