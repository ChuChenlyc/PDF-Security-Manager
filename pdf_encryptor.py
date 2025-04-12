import os
import sys
import json
import shutil
import logging
import subprocess
import hashlib
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                           QVBoxLayout, QWidget, QFileDialog, QMessageBox,
                           QCheckBox, QGroupBox, QHBoxLayout, QRadioButton,
                           QLineEdit, QHBoxLayout, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class PDFEncryptor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF权限限制工具")
        self.setGeometry(100, 100, 800, 600)  # 增加窗口大小
        
        # 设置日志
        self.setup_logging()
        
        # 创建主窗口部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建布局
        self.layout = QVBoxLayout(self.central_widget)
        
        # 创建GUI元素
        self.create_widgets()
        
        # 加载配置
        self.config = self.load_config()
        
        # 设置接受拖放
        self.setAcceptDrops(True)
        
        # 设置初始状态
        self.update_options_state()
        
        logging.info("程序启动")
        
    def setup_logging(self):
        # 获取程序所在目录
        if getattr(sys, 'frozen', False):
            # 如果是exe文件
            application_path = os.path.dirname(sys.executable)
        else:
            # 如果是python脚本
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        # 创建logs目录（如果不存在）
        log_dir = os.path.join(application_path, "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 设置日志文件名（使用日期）
        log_file = os.path.join(log_dir, f"pdf_encryptor_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
    def create_widgets(self):
        # 文件选择按钮
        self.select_btn = QPushButton("选择PDF文件")
        self.select_btn.clicked.connect(self.select_file)
        self.layout.addWidget(self.select_btn)
        
        # 拖放区域
        self.drop_label = QLabel("拖放PDF文件到这里")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("""
            QLabel {
                background-color: lightgray;
                border: 2px dashed gray;
                padding: 20px;
                font-size: 16px;
            }
        """)
        self.drop_label.setMinimumHeight(200)
        self.layout.addWidget(self.drop_label)
        
        # 创建选项组
        self.create_options_group()
        
        # 权限说明标签
        self.permission_label = QLabel("将设置以下权限：\n- 允许打开文档（无需密码）\n- 限制文档编辑\n- 允许高分辨率打印\n- 不允许更改\n- 禁用复制功能")
        self.permission_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.permission_label)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)
        
        # 底部按钮区域
        bottom_layout = QHBoxLayout()
        
        # 查看日志按钮
        self.view_log_btn = QPushButton("查看日志")
        self.view_log_btn.clicked.connect(self.view_logs)
        bottom_layout.addWidget(self.view_log_btn)
        
        # 添加弹性空间
        bottom_layout.addStretch()
        
        self.layout.addLayout(bottom_layout)
        
    def create_options_group(self):
        # 创建选项组
        options_group = QGroupBox("处理选项")
        options_layout = QVBoxLayout()
        
        # 加密选项
        encryption_group = QGroupBox("加密选项")
        encryption_layout = QVBoxLayout()
        
        # 添加加密口令设置
        password_layout = QHBoxLayout()
        password_label = QLabel("加密口令：")
        self.password_btn = QPushButton("设置加密口令")
        self.password_btn.clicked.connect(self.set_password)
        self.password_status = QLabel("未设置")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_btn)
        password_layout.addWidget(self.password_status)
        encryption_layout.addLayout(password_layout)
        
        encryption_group.setLayout(encryption_layout)
        options_layout.addWidget(encryption_group)
        
        # 输出选项
        output_group = QGroupBox("输出选项")
        output_layout = QVBoxLayout()
        
        self.modify_original = QRadioButton("直接修改原文件")
        self.modify_original.setChecked(True)
        self.modify_original.toggled.connect(self.update_options_state)
        self.create_new_file = QRadioButton("创建新文件（添加后缀）")
        self.create_new_file.toggled.connect(self.update_options_state)
        
        # 添加后缀输入框
        suffix_layout = QHBoxLayout()
        suffix_label = QLabel("自定义后缀：")
        self.suffix_input = QLineEdit("_restricted")
        self.suffix_input.setEnabled(False)  # 初始状态为禁用
        suffix_layout.addWidget(suffix_label)
        suffix_layout.addWidget(self.suffix_input)
        
        output_layout.addWidget(self.modify_original)
        output_layout.addWidget(self.create_new_file)
        output_layout.addLayout(suffix_layout)
        output_group.setLayout(output_layout)
        options_layout.addWidget(output_group)
        
        # 备份选项
        backup_group = QGroupBox("备份选项")
        self.backup_group = backup_group  # 保存引用以便后续控制
        backup_layout = QVBoxLayout()
        
        # 是否创建备份
        self.create_backup_check = QCheckBox("创建备份文件")
        self.create_backup_check.setChecked(True)
        self.create_backup_check.stateChanged.connect(self.update_options_state)
        backup_layout.addWidget(self.create_backup_check)
        
        # 备份位置选项
        backup_location_group = QGroupBox("备份位置")
        self.backup_location_group = backup_location_group  # 保存引用以便后续控制
        backup_location_layout = QVBoxLayout()
        
        self.backup_same_dir = QRadioButton("保存在原文件目录")
        self.backup_same_dir.setChecked(True)
        self.backup_same_dir.toggled.connect(self.update_options_state)
        self.backup_custom_dir = QRadioButton("保存在指定目录")
        self.backup_custom_dir.toggled.connect(self.update_options_state)
        
        backup_location_layout.addWidget(self.backup_same_dir)
        backup_location_layout.addWidget(self.backup_custom_dir)
        backup_location_group.setLayout(backup_location_layout)
        backup_layout.addWidget(backup_location_group)
        
        # 自定义备份目录选择
        custom_dir_layout = QHBoxLayout()
        self.backup_dir_btn = QPushButton("选择备份目录")
        self.backup_dir_btn.clicked.connect(self.select_backup_dir)
        self.backup_dir_label = QLabel("未选择")
        custom_dir_layout.addWidget(self.backup_dir_btn)
        custom_dir_layout.addWidget(self.backup_dir_label)
        backup_layout.addLayout(custom_dir_layout)
        
        backup_group.setLayout(backup_layout)
        options_layout.addWidget(backup_group)
        
        options_group.setLayout(options_layout)
        self.layout.addWidget(options_group)
        
    def update_options_state(self):
        # 如果选择创建新文件，禁用所有备份选项
        if self.create_new_file.isChecked():
            self.backup_group.setEnabled(False)
            self.create_backup_check.setChecked(False)
            self.suffix_input.setEnabled(True)  # 启用后缀输入框
        else:
            self.backup_group.setEnabled(True)
            self.suffix_input.setEnabled(False)  # 禁用后缀输入框
            
        # 如果选择不创建备份，禁用备份位置选项
        if not self.create_backup_check.isChecked():
            self.backup_location_group.setEnabled(False)
            self.backup_dir_btn.setEnabled(False)
        else:
            self.backup_location_group.setEnabled(True)
            # 如果选择保存在原文件目录，禁用备份目录选择按钮
            if self.backup_same_dir.isChecked():
                self.backup_dir_btn.setEnabled(False)
            else:
                self.backup_dir_btn.setEnabled(True)
            
    def select_backup_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择备份目录",
            self.config.get("backup_directory", "")
        )
        if dir_path:
            self.config["backup_directory"] = dir_path
            self.save_config()
            self.backup_dir_label.setText(dir_path)
            self.backup_custom_dir.setChecked(True)
            
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        file_path = event.mimeData().urls()[0].toLocalFile()
        logging.info(f"拖放文件: {file_path}")
        if file_path.lower().endswith('.pdf'):
            self.process_file(file_path)
        else:
            error_msg = "请拖放PDF文件"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            
    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                # 恢复备份目录显示
                if "backup_directory" in config:
                    self.backup_dir_label.setText(config["backup_directory"])
                return config
        except FileNotFoundError:
            logging.info("未找到配置文件，使用默认配置")
            return {"last_directory": "", "backup_directory": ""}
            
    def save_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f)
            
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择PDF文件",
            self.config.get("last_directory", ""),
            "PDF文件 (*.pdf)"
        )
        if file_path:
            logging.info(f"选择文件: {file_path}")
            self.config["last_directory"] = os.path.dirname(file_path)
            self.save_config()
            self.process_file(file_path)
            
    def view_logs(self):
        # 获取程序所在目录
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        log_dir = os.path.join(application_path, "logs")
        if not os.path.exists(log_dir):
            QMessageBox.information(self, "提示", "暂无日志文件")
            return
            
        # 获取最新的日志文件
        log_files = [f for f in os.listdir(log_dir) if f.startswith("pdf_encryptor_") and f.endswith(".log")]
        if not log_files:
            QMessageBox.information(self, "提示", "暂无日志文件")
            return
            
        latest_log = max(log_files, key=lambda x: os.path.getctime(os.path.join(log_dir, x)))
        log_path = os.path.join(log_dir, latest_log)
        
        try:
            # 使用系统默认程序打开日志文件
            if sys.platform == 'win32':
                os.startfile(log_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', log_path])
            else:  # linux
                subprocess.call(['xdg-open', log_path])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开日志文件: {str(e)}")
            
    def set_password(self):
        # 使用输入对话框获取密码
        password, ok = QInputDialog.getText(
            self,
            "设置加密口令",
            "请输入加密口令（留空则使用默认口令）：",
            QLineEdit.Password
        )
        
        if ok:
            if password:
                # 对密码进行哈希处理
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                self.config["hashed_password"] = hashed_password
                self.password_status.setText("已设置")
                logging.info("用户设置了新的加密口令")
            else:
                # 清除密码
                if "hashed_password" in self.config:
                    del self.config["hashed_password"]
                self.password_status.setText("未设置")
                logging.info("用户清除了加密口令")
            
            self.save_config()
            
    def process_file(self, file_path):
        try:
            logging.info(f"开始处理文件: {file_path}")
            
            # 读取PDF文件
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            # 复制所有页面
            for page in reader.pages:
                writer.add_page(page)
                
            # 设置权限
            permissions = (
                1 << 2 |     # 允许打印
                1 << 11      # 允许高质量打印
            )
            
            # 获取加密口令
            owner_password = "6610906"  # 默认口令
            if "hashed_password" in self.config:
                # 使用用户设置的口令
                owner_password = self.config["hashed_password"]
            
            writer.encrypt(
                user_password="",  # 空密码，允许打开
                owner_password=owner_password,  # 所有者密码
                use_128bit=True,
                permissions_flag=permissions  # 设置指定权限
            )
            
            # 处理备份
            backup_path = None
            if self.create_backup_check.isChecked():
                if self.backup_same_dir.isChecked():
                    backup_path = file_path + ".bak"
                else:
                    # 使用自定义目录
                    backup_dir = self.config.get("backup_directory", "")
                    if backup_dir:
                        backup_filename = os.path.basename(file_path) + ".bak"
                        backup_path = os.path.join(backup_dir, backup_filename)
                    else:
                        QMessageBox.warning(self, "警告", "请先选择备份目录")
                        return
                
                shutil.copy2(file_path, backup_path)
                logging.info(f"创建备份文件: {backup_path}")
            
            # 处理输出
            if self.modify_original.isChecked():
                # 直接修改原文件
                output_path = file_path
            else:
                # 创建新文件，使用用户自定义的后缀
                base, ext = os.path.splitext(file_path)
                suffix = self.suffix_input.text().strip()
                if not suffix:
                    suffix = "_restricted"  # 默认后缀
                output_path = f"{base}{suffix}{ext}"
            
            # 保存文件
            with open(output_path, "wb") as f:
                writer.write(f)
                
            # 显示结果
            result_msg = "PDF权限设置完成！"
            if backup_path:
                result_msg += f"\n原文件已备份为: {backup_path}"
            if output_path != file_path:
                result_msg += f"\n新文件已保存为: {output_path}"
                
            logging.info(result_msg)
            QMessageBox.information(self, "成功", result_msg)
            self.status_label.setText(f"处理完成: {os.path.basename(output_path)}")
            
        except Exception as e:
            error_msg = f"处理过程中出现错误: {str(e)}"
            logging.error(error_msg, exc_info=True)
            QMessageBox.critical(self, "错误", error_msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if file_path.lower().endswith('.pdf'):
            window = PDFEncryptor()
            window.process_file(file_path)
            sys.exit()
    
    window = PDFEncryptor()
    window.show()
    sys.exit(app.exec_()) 