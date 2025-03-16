import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTextEdit, QLineEdit, QGroupBox, QFormLayout, QMessageBox, QMenuBar, QMenu, QAction,
    QDialog, QDialogButtonBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo


class SerialDebugTool(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.serial = QSerialPort()

    def init_ui(self):
        self.setWindowTitle("串口调试工具_long")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: rgb(200,200,210);")

        # 创建菜单栏
        menubar = QMenuBar(self)
        
        # 创建编辑菜单
        edit_menu = menubar.addMenu("编辑")
        
        # 添加串口设置动作
        settings_action = QAction("串口设置", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        edit_menu.addAction(settings_action)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setMenuBar(menubar)

        # 串口选择部分
        self.port_combo = QComboBox()
        self.refresh_button = QPushButton("刷新串口")
        self.refresh_button.clicked.connect(self.refresh_ports)

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("选择串口:"))
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(self.refresh_button)
        main_layout.addLayout(port_layout)

        # 打开/关闭串口按钮
        self.open_button = QPushButton("打开串口")
        self.open_button.clicked.connect(self.toggle_serial)
        main_layout.addWidget(self.open_button)

        # 发送数据部分
        self.send_input = QLineEdit()
        self.send_button = QPushButton("发送数据")
        self.send_button.clicked.connect(self.send_data)

        # 新增快捷发送按钮
        self.quick_send_button = QPushButton("快捷发送")
        self.quick_send_button.clicked.connect(self.quick_send)
        self.quick_send_button.setContextMenuPolicy(3)  # 启用右键菜单
        self.quick_send_button.customContextMenuRequested.connect(self.edit_quick_send_text)
        self.quick_send_text = "Hello"  # 默认发送文本

        send_layout = QHBoxLayout()
        send_layout.addWidget(self.send_input)
        send_layout.addWidget(self.send_button)
        send_layout.addWidget(self.quick_send_button)
        main_layout.addLayout(send_layout)

        # 接收数据显示部分
        self.receive_text = QTextEdit()
        self.receive_text.setReadOnly(True)
        main_layout.addWidget(self.receive_text)

        # 定时器用于读取串口数据
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_data)

        self.setLayout(main_layout)
        self.refresh_ports()

    def refresh_ports(self):
        """刷新可用串口列表"""
        self.port_combo.clear()
        ports = QSerialPortInfo.availablePorts()
        for port in ports:
            self.port_combo.addItem(port.portName())

    def toggle_serial(self):
        """打开或关闭串口"""
        if self.serial.isOpen():
            self.serial.close()
            self.open_button.setText("打开串口")
            self.timer.stop()
            self.receive_text.append("串口已关闭")
        else:
            port_name = self.port_combo.currentText()
            if not port_name:
                QMessageBox.warning(self, "错误", "请选择一个串口")
                return

            self.serial.setPortName(port_name)
            self.serial.setBaudRate(self.baudrate)
            self.serial.setDataBits(self.data_bits)
            if self.stop_bits == 1:
                self.serial.setStopBits(QSerialPort.OneStop)
            elif self.stop_bits == 1.5:
                self.serial.setStopBits(QSerialPort.OneAndHalfStop)
            elif self.stop_bits == 2:
                self.serial.setStopBits(QSerialPort.TwoStop)
            self.serial.setParity({
                "无": QSerialPort.NoParity,
                "奇校验": QSerialPort.OddParity,
                "偶校验": QSerialPort.EvenParity
            }[self.parity])
            self.serial.setFlowControl({
                "无": QSerialPort.NoFlowControl,
                "硬件": QSerialPort.HardwareControl,
                "软件": QSerialPort.SoftwareControl
            }[self.flow_control])

            if self.serial.open(QSerialPort.ReadWrite):
                self.open_button.setText("关闭串口")
                self.timer.start(100)  # 每100ms读取一次数据
                self.receive_text.append(f"串口 {port_name} 已打开")
            else:
                QMessageBox.critical(self, "错误", "无法打开串口")

    def send_data(self):
        """发送数据"""
        if not self.serial.isOpen():
            QMessageBox.warning(self, "错误", "请先打开串口")
            return

        data = self.send_input.text()
        if data:
            self.serial.write(data.encode())
            self.receive_text.append(f"发送: {data}")

    def read_data(self):
        """读取串口数据"""
        if self.serial.bytesAvailable():
            data = self.serial.readAll()
            self.receive_text.append(f"接收: {data.data().decode()}")

    def closeEvent(self, event):
        """关闭窗口时关闭串口"""
        if self.serial.isOpen():
            self.serial.close()
        event.accept()

    def quick_send(self):
        """快捷发送"""
        if not self.serial.isOpen():
            QMessageBox.warning(self, "错误", "请先打开串口")
            return
        self.serial.write(self.quick_send_text.encode())
        self.receive_text.append(f"快捷发送: {self.quick_send_text}")

    def edit_quick_send_text(self):
        """编辑快捷发送文本"""
        self.edit_window = EditTextWindow(self.quick_send_text, self)
        self.edit_window.show()

    def update_quick_send_text(self, new_text):
        """更新快捷发送文本"""
        self.quick_send_text = new_text

    def __init__(self):
        super().__init__()
        self.serial = QSerialPort()
        # 初始化默认串口参数
        self.baudrate = 9600
        self.data_bits = 8
        self.stop_bits = 1
        self.parity = "无"
        self.flow_control = "无"
        self.init_ui()

    def show_settings_dialog(self):
        """显示串口设置对话框"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("串口设置")
            dialog.setModal(True)
            
            layout = QFormLayout()
            
            # 波特率
            baudrate_combo = QComboBox()
            baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
            baudrate_combo.setCurrentText(str(self.baudrate))
            layout.addRow("波特率:", baudrate_combo)
            
            # 数据位
            data_bits_combo = QComboBox()
            data_bits_combo.addItems(["5", "6", "7", "8"])
            data_bits_combo.setCurrentText(str(self.data_bits))
            layout.addRow("数据位:", data_bits_combo)
            
            # 停止位
            stop_bits_combo = QComboBox()
            stop_bits_combo.addItems(["1", "1.5", "2"])
            stop_bits_combo.setCurrentText(str(self.stop_bits))
            layout.addRow("停止位:", stop_bits_combo)
            
            # 校验位
            parity_combo = QComboBox()
            parity_combo.addItems(["无", "奇校验", "偶校验"])
            parity_combo.setCurrentText(self.parity)
            layout.addRow("校验位:", parity_combo)
            
            # 流控制
            flow_control_combo = QComboBox()
            flow_control_combo.addItems(["无", "硬件", "软件"])
            flow_control_combo.setCurrentText(self.flow_control)
            layout.addRow("流控制:", flow_control_combo)
            
            # 添加确定和取消按钮
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted:
                # 保存设置
                self.baudrate = int(baudrate_combo.currentText())
                self.data_bits = int(data_bits_combo.currentText())
                self.stop_bits = float(stop_bits_combo.currentText())
                self.parity = parity_combo.currentText()
                self.flow_control = flow_control_combo.currentText()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开设置对话框时发生错误: {str(e)}")


class EditTextWindow(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui(text)

    def init_ui(self, text):
        self.setWindowTitle("编辑快捷发送文本")
        self.setGeometry(200, 200, 300, 100)

        layout = QVBoxLayout()

        self.text_edit = QLineEdit(text)
        layout.addWidget(self.text_edit)

        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_text)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_text(self):
        new_text = self.text_edit.text()
        if new_text:
            self.parent.update_quick_send_text(new_text)
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tool = SerialDebugTool()
    tool.show()
    sys.exit(app.exec_())
