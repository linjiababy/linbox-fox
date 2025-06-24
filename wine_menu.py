#该脚本只用于foxbox模拟器，盗者必究
import os
import sys
import subprocess
import tarfile
import shutil
import re
import py7zr  
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QListWidget, QScrollArea, QFrame, 
                            QMessageBox, QFileDialog, QInputDialog, QDialog, QDialogButtonBox,
                            QLineEdit, QSpinBox, QGridLayout, QProgressBar, QSizePolicy,
                            QCheckBox, QGroupBox, QButtonGroup, QTextEdit, QRadioButton)
from PyQt5.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont

class GLIBCManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WINE 管理器")
        self.setFixedSize(750, 480)
        self.center_window()
        
        self.glibc_path = "/data/data/com.termux/files/usr/glibc"
        self.usr_path = "/data/data/com.termux/files/usr"
        self.opt_path = os.path.join(self.glibc_path, "opt")
        self.conf_path = os.path.join(self.opt_path, "conf")
        self.wine_path_conf = os.path.join(self.conf_path, "wine_path.conf")
        self.icon_path = "/data/data/com.termux/files/usr/wine-png"
        self.cores_conf = os.path.join(self.conf_path, "cores.conf")
        self.dynarec_preset_conf = os.path.join(self.conf_path, "dynarec_preset.conf")
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.version_label = QLabel()
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                background-color: #add8e6;
                border-radius: 8px;
                min-height: 30px;
            }
        """)
        self.update_version_info()
        main_layout.addWidget(self.version_label)
        
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.left_container = QWidget()
        self.left_container.setFixedWidth(320)
        self.left_container.setStyleSheet("background: transparent;")
        
        container_layout = QHBoxLayout(self.left_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        menu_items = [
            ("启动Wine", "start.png", "start"),
            ("Wine管理", "wine.png", "wine"),
            ("高级选项", "advanced.png", "advanced"),
            ("卸载选项", "uninstall.png", "uninstall"),
            ("切换选项", "switch.png", "switch")
        ]

        menu_container = QWidget()
        menu_container.setFixedWidth(320)
        menu_container.setObjectName("menuContainer")
        menu_container.setStyleSheet("""
            QWidget#menuContainer {
                background: transparent;
                border: none;
            }
        """)

        menu_layout = QVBoxLayout(menu_container)
        menu_layout.setContentsMargins(5, 5, 5, 5)
        menu_layout.setSpacing(45)

        for text, icon_name, menu_type in menu_items:
            btn = QPushButton(text)
            btn.setFixedHeight(45)
            self.set_button_icon(btn, icon_name)
            btn.setStyleSheet(""" 
                QPushButton {
                    background: #D3D3D3;
                    color: #000000;
                    border: none;
                    border-radius: 10px;
                    font-size: 16px;
                    text-align: center;
                    padding-left: 0;
                }
                QPushButton:hover {
                    background: #C0C0C0;
                }
                QPushButton::icon {
                    margin-right: 8px;
                }
            """)
            btn.clicked.connect(lambda _, m=menu_type: self.show_sub_menu(m))
            menu_layout.addWidget(btn)

        menu_layout.addStretch()
        
        self.sub_menu = QWidget()
        self.sub_menu.setFixedWidth(160)
        self.sub_menu.setObjectName("submenuArea")
        self.sub_menu.setStyleSheet(""" 
            QWidget#submenuArea {
                background: #d3d3d3;
                border-radius: 10px;
                border: 2px solid #a0a0a0;
            }
        """)
        self.sub_menu.hide()
        
        self.sub_layout = QVBoxLayout(self.sub_menu)
        self.sub_layout.setContentsMargins(5, 5, 5, 5)
        self.sub_layout.setSpacing(5)
        
        container_layout.addWidget(menu_container)
        container_layout.addWidget(self.sub_menu)
        
        self.interaction_area = QFrame()
        self.interaction_area.setFixedWidth(400)
        self.interaction_area.setStyleSheet("""
            QFrame {
                background-color: #f8f8f8;
            }
            QListWidget {
                border: none;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #d0e3ff;
                color: black;
            }
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QCheckBox {
                spacing: 5px;
            }
            QTextEdit {
                border: none;
                background-color: transparent;
                font-size: 12px;
            }
        """)
        
        self.interaction_layout = QVBoxLayout(self.interaction_area)
        self.interaction_layout.setContentsMargins(0, 0, 0, 0)
        
        self.interaction_title = QLabel("请从左侧菜单选择功能")
        self.interaction_title.setAlignment(Qt.AlignCenter)
        self.interaction_title.setStyleSheet("font-size: 16px; padding: 10px;")
        self.interaction_layout.addWidget(self.interaction_title)
        
        self.interaction_content = QListWidget()
        self.interaction_content.setSelectionMode(QListWidget.SingleSelection)
        self.interaction_content.itemClicked.connect(self.handle_interaction_selection)
        self.interaction_layout.addWidget(self.interaction_content)
        
        content_layout.addWidget(self.left_container)
        content_layout.addWidget(self.interaction_area)
        
        main_layout.addWidget(content_widget)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(40)
        self.log_text.setStyleSheet("font-size: 11px;")
        self.log_text.hide()
        main_layout.addWidget(self.log_text)
       
        self.install_thread = None
        self.backup_thread = None
        self.restore_thread = None

    def set_button_icon(self, button, icon_name):
        icon_path = os.path.join(self.icon_path, icon_name)
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(30, 30))
    
    def center_window(self):
        frame = self.frameGeometry()
        center_point = QApplication.desktop().availableGeometry().center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())
    
    def update_version_info(self):
        wine_ver = self.get_wine_version()
        box64_ver = self.get_box64_version()
        box86_ver = self.get_box86_version()
        turnip_ver = self.get_turnip_version()
        dxvk_ver = self.get_dxvk_version()
        
        version_text = f"Wine: {wine_ver:<12} Box64: {box64_ver:<10} Box86: {box86_ver:<10}\nTurnip: {turnip_ver:<10} DXVK: {dxvk_ver:<10}"
        self.version_label.setText(version_text)
    
    def get_wine_version(self):
        if not os.path.exists(self.wine_path_conf):
            return "未安装"
        
        with open(self.wine_path_conf, 'r') as f:
            for line in f:
                if line.startswith("export WINE_PATH="):
                    wine_path = line.split('=')[1].strip().strip('"')
                    wine_dir = os.path.basename(wine_path)
                    if 'wine-' in wine_dir:
                        return wine_dir.split('wine-')[-1]
                    return wine_dir
        return "未安装"
    
    def get_box64_version(self):
        box64_path = os.path.join(self.glibc_path, "bin", "box64")
        if not os.path.exists(box64_path):
            return "未安装"
        
        try:
            env = os.environ.copy()
            env["LD_PRELOAD"] = ""
            env["PATH"] = f"{env.get('PATH', '')}:/data/data/com.termux/files/usr/glibc/bin"
            
            result = subprocess.run([box64_path, "--version"], 
                                  capture_output=True, 
                                  text=True,
                                  env=env)
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                version = re.search(r'(v|V)?[0-9]+([.-][0-9]+)+', version_line)
                return version.group(0) if version else "未知"
        except Exception as e:
            print(f"获取Box64版本出错: {e}")
        return "未知"
    
    def get_box86_version(self):
        box86_path = os.path.join(self.glibc_path, "bin", "box86")
        if not os.path.exists(box86_path):
            return "未安装"
        
        try:
            env = os.environ.copy()
            env["LD_PRELOAD"] = ""
            env["PATH"] = f"{env.get('PATH', '')}:/data/data/com.termux/files/usr/glibc/bin"
            
            result = subprocess.run([box86_path, "--version"], 
                                  capture_output=True, 
                                  text=True,
                                  env=env)
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                version = re.search(r'(v|V)?[0-9]+([.-][0-9]+)+', version_line)
                return version.group(0) if version else "未知"
        except Exception as e:
            print(f"获取Box86版本出错: {e}")
        return "未知"
    
    def get_turnip_version(self):
        last_selected = os.path.join(self.opt_path, "turnip", ".last_selected")
        if not os.path.exists(last_selected):
            return "未安装"
        
        try:
            with open(last_selected, 'r') as f:
                tz_file = f.read().strip()
                filename = os.path.basename(tz_file)
                version = re.search(r'(v|V)?[0-9]+([.-][0-9]+)+', filename)
                return version.group(0) if version else "未知"
        except Exception as e:
            print(f"获取Turnip版本出错: {e}")
        return "未知"
    
    def get_dxvk_version(self):
        last_selected = os.path.join(self.opt_path, "dxvk", ".last_selected")
        if not os.path.exists(last_selected):
            return "未安装"
        
        try:
            with open(last_selected, 'r') as f:
                dxvk_file = f.read().strip()
                filename = os.path.basename(dxvk_file)
                version = re.search(r'(v|V)?[0-9]+([.-][0-9]+)+', filename)
                if version:
                    return version.group(0)
                return "未知" if filename else "未安装"
        except Exception as e:
            print(f"获取DXVK版本出错: {e}")
        return "未知"
    
    def clear_interaction_area(self):
        for i in reversed(range(self.interaction_layout.count())): 
            widget = self.interaction_layout.itemAt(i).widget()
            if widget is not None and widget != self.interaction_title and widget != self.interaction_content:
                widget.setParent(None)
                self.interaction_layout.removeWidget(widget)
        
        self.interaction_content.show()
        self.interaction_content.clear()
        self.interaction_title.setText("请选择操作")
        self.progress_bar.hide()
        self.log_text.hide()
    
    def show_sub_menu(self, menu_type):
        self.left_container.findChild(QWidget, "menuContainer").setFixedWidth(160)
        
        self.clear_interaction_area()
        
        for i in reversed(range(self.sub_layout.count())): 
            widget = self.sub_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        if menu_type == "start":
            self.sub_menu_title = "启动选项"
            
            actions = [
                ("窗口启动", "start_window_mode"),
                ("全屏启动", "start_fullscreen_mode")
            ]
            
        elif menu_type == "wine":
            self.sub_menu_title = "Wine管理"
            
            actions = [
                ("安装 Wine", "install_wine"),
                ("切换版本", "select_wine"),
                ("卸载 Wine", "uninstall_wine")
            ]
            
        elif menu_type == "advanced":
            self.sub_menu_title = "高级选项"
            
            actions = [
                ("Dynarec设置", "dynarec_settings"),
                ("Cpu核心设置", "set_cpu_cores"),
                ("环境备份/恢复", "backup_restore"),
                ("重置Wine环境", "reset_wine_prefix")
            ]
            
        elif menu_type == "uninstall":
            self.sub_menu_title = "卸载选项"
            
            actions = [
                ("卸载 DXVK", "uninstall_dxvk"),
                ("卸载 Vkd3d", "uninstall_vkd3d"),
                ("卸载 Turnip", "uninstall_turnip"),
                ("卸载 Box64/86", "uninstall_box"),
                ("卸载所有组件", "uninstall_all")
            ]
            
        elif menu_type == "switch":
            self.sub_menu_title = "切换选项"
            
            actions = [
                ("语言切换", "switch_language"),
                ("Fps设置", "switch_fps"),
                ("Hud切换", "switch_hud"),
                ("Dxvk切换", "switch_dxvk"),
                ("Vkd3d补丁", "switch_vkd3d"),
                ("Turnip切换", "switch_turnip"),
                ("Box64/86切换", "switch_box")
            ]
        
        for text, action in actions:
            btn = QPushButton(text)
            btn.setFixedHeight(35)
            btn.setStyleSheet(""" 
                QPushButton {
                    background: #00CED1;
                    color: #000000;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    width: 100%;
                    text-align: center;
                }
                QPushButton:hover {
                    background: #20B2AA;
                }
            """)
            btn.clicked.connect(getattr(self, action))
            self.sub_layout.addWidget(btn)
        
        self.sub_menu.show()
        self.interaction_title.setText(f"{self.sub_menu_title} - 请选择操作")
    
    def handle_interaction_selection(self, item):
        if hasattr(self, 'current_interaction_handler'):
            self.current_interaction_handler(item.text())
    
    def start_window_mode(self):
        self.clear_interaction_area()
        self.interaction_title.setText("窗口启动 - 选择分辨率")
        
        resolutions = ["800x600", "1024x768", "1280x720", "1600x900", "1920x1080", "自定义"]
        self.interaction_content.addItems(resolutions)
        
        def handler(resolution):
            if resolution == "自定义":
                res, ok = QInputDialog.getText(self, "自定义分辨率", "请输入分辨率 (如: 800x600):")
                if ok and res:
                    self.execute_start_window(res)
            else:
                self.execute_start_window(resolution)
            self.hide()
        
        self.current_interaction_handler = handler
    
    def execute_start_window(self, resolution):
        if not self.validate_resolution(resolution):
            QMessageBox.warning(self, "错误", "分辨率格式不正确！")
            return
        
        cmd = f"ssh -p 8022 127.0.0.1 startonwine /data/data/com.termux/files/usr/glibc/opt/apps/wfm.exe --desktop='{resolution}' -b -5"
        subprocess.Popen(cmd, shell=True)
    
    def start_fullscreen_mode(self):
        try:
            cmd = [
                "ssh", "-p", "8022", "127.0.0.1", "startonwine",
                "/data/data/com.termux/files/usr/glibc/opt/apps/wfm.exe"
            ]
            
            subprocess.Popen(cmd)
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动失败: {str(e)}")
    
    def validate_resolution(self, resolution):
        return re.match(r'^\d+x\d+$', resolution) is not None
    
    def install_wine(self):
        self.clear_interaction_area()
        self.interaction_title.setText("安装Wine - 选择来源")
        
        options = ["从文件选择Wine压缩包", "输入下载链接", "从默认源安装"]
        self.interaction_content.addItems(options)
        
        def handler(option):
            if option == "从文件选择Wine压缩包":
                self.install_wine_from_file()
            elif option == "输入下载链接":
                self.install_wine_from_url()
            elif option == "从默认源安装":
                self.install_wine_from_default()
        
        self.current_interaction_handler = handler
    
    def install_wine_from_file(self):
        class InstallWineThread(QThread):
            finished = pyqtSignal(bool, str)
            progress = pyqtSignal(int)
            log_message = pyqtSignal(str)
            
            def __init__(self, file_path, glibc_path):
                super().__init__()
                self.file_path = file_path
                self.glibc_path = glibc_path
                self.canceled = False
            
            def run(self):
                try:
                    self.log_message.emit(f"开始解压文件: {os.path.basename(self.file_path)}")
                    
                    if self.file_path.endswith('.7z'):
                        self.extract_7z()
                    elif self.file_path.endswith('.tar.gz') or self.file_path.endswith('.tgz'):
                        self.extract_tar('r:gz')
                    elif self.file_path.endswith('.tar.xz'):
                        self.extract_tar('r:xz')
                    elif self.file_path.endswith('.tar'):
                        self.extract_tar('r:')
                    else:
                        self.finished.emit(False, "不支持的压缩格式，支持7z/tar.gz/tar.xz/tar")
                        return
                    
                    if self.canceled:
                        self.finished.emit(False, "安装已取消")
                        return
                    
                    self.finished.emit(True, f"Wine 安装成功！")
                    
                except Exception as e:
                    self.finished.emit(False, f"解压失败: {str(e)}")
            
            def extract_7z(self):
                with py7zr.SevenZipFile(self.file_path, mode='r') as archive:
                    top_dir = None
                    for name in archive.getnames():
                        parts = name.split('/')
                        if len(parts) > 0 and parts[0]:
                            top_dir = parts[0]
                            break
                    
                    if not top_dir:
                        raise ValueError("压缩包中没有找到顶层目录")
                    
                    dest_dir = os.path.join(self.glibc_path, top_dir)
                    
                    if os.path.exists(dest_dir):
                        self.log_message.emit(f"删除已存在的目录: {dest_dir}")
                        shutil.rmtree(dest_dir)
                    
                    self.log_message.emit(f"解压到目录: {dest_dir}")
                    
                    archive.extractall(path=self.glibc_path)
                  
                    self.set_file_permissions(dest_dir)
            
            def extract_tar(self, mode):
                with tarfile.open(self.file_path, mode) as tar:
                    members = tar.getmembers()
                    total_members = len(members)
                    extracted = 0
                    top_dir = None
                
                    for member in members:
                        parts = member.name.split('/')
                        if len(parts) > 0 and parts[0]:
                            top_dir = parts[0]
                            break
                    
                    if not top_dir:
                        raise ValueError("压缩包中没有找到顶层目录")
                    
                    dest_dir = os.path.join(self.glibc_path, top_dir)
                    
                    if os.path.exists(dest_dir):
                        self.log_message.emit(f"删除已存在的目录: {dest_dir}")
                        shutil.rmtree(dest_dir)
                    
                    self.log_message.emit(f"解压到目录: {dest_dir}")
                    
                    for member in members:
                        if self.canceled:
                            break
                        
                        tar.extract(member, self.glibc_path)
                        extracted += 1
                        progress = int((extracted / total_members) * 100)
                        self.progress.emit(progress)
                    
                    if self.canceled:
                        if os.path.exists(dest_dir):
                            shutil.rmtree(dest_dir)
                        return
                    
                    self.set_file_permissions(dest_dir)
            
            def set_file_permissions(self, dest_dir):
                self.log_message.emit("设置文件权限...")
                for root, dirs, files in os.walk(dest_dir):
                    for d in dirs:
                        os.chmod(os.path.join(root, d), 0o755)
                    for f in files:
                        os.chmod(os.path.join(root, f), 0o644)
                
                bin_path = os.path.join(dest_dir, "bin")
                if os.path.exists(bin_path):
                    for f in os.listdir(bin_path):
                        os.chmod(os.path.join(bin_path, f), 0o755)

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Wine压缩包", "", 
            "压缩文件 (*.7z *.tar.gz *.tar.xz *.tar *.tgz)"
        )
        
        if file_path:
            self.progress_bar.show()
            self.log_text.show()
            self.progress_bar.setValue(0)
            self.log_text.clear()
            
            self.install_thread = InstallWineThread(file_path, self.glibc_path)
            self.install_thread.finished.connect(self.on_install_finished)
            self.install_thread.progress.connect(self.progress_bar.setValue)
            self.install_thread.log_message.connect(self.log_text.append)
            self.install_thread.start()
    
    def on_install_finished(self, success, message):
        self.progress_bar.hide()
        
        if success:
            QMessageBox.information(self, "成功", message)
            self.update_version_info()
            self.select_wine()
        else:
            QMessageBox.critical(self, "错误", message)
    
    def install_wine_from_url(self):
        url, ok = QInputDialog.getText(
            self, "输入Wine下载链接", "请输入Wine压缩包的下载链接:"
        )
        
        if ok and url:
            self.progress_bar.show()
            QTimer.singleShot(2000, lambda: self._install_wine_from_url_actual(url))
    
    def _install_wine_from_url_actual(self, url):
        QMessageBox.information(self, "提示", "下载功能将在完整版中实现")
        self.progress_bar.hide()
    
    def install_wine_from_default(self):
        self.progress_bar.show()
        QTimer.singleShot(2000, lambda: self._install_wine_from_default_actual())
    
    def _install_wine_from_default_actual(self):
        QMessageBox.information(self, "提示", "默认源安装功能将在完整版中实现")
        self.progress_bar.hide()
    
    def select_wine(self):
        self.clear_interaction_area()
        self.interaction_title.setText("选择Wine版本")
        
        wine_dirs = []
        for item in os.listdir(self.glibc_path):
            if item.startswith("wine-"):
                wine_dirs.append(item)
        
        opt_wine_path = os.path.join(self.opt_path, "wine")
        if os.path.exists(opt_wine_path):
            for item in os.listdir(opt_wine_path):
                wine_dirs.append(os.path.join("opt/wine", item))
        
        if not wine_dirs:
            QMessageBox.information(self, "提示", "没有找到可用的Wine版本")
            return
        
        wine_dirs = self.sort_version_list(wine_dirs)
        
        self.interaction_content.addItems(wine_dirs)
        
        def handler(selected_wine):
            wine_path = os.path.join(self.glibc_path, selected_wine)
            
            with open(self.wine_path_conf, 'w') as f:
                f.write(f'export WINE_PATH="{wine_path}"\n')
                f.write(f'export WINEPREFIX="{wine_path}/.wine"\n')
            
            with open(os.path.join(self.conf_path, "wine_path1.conf"), 'w') as f:
                f.write(f'export WINE_PATH="{wine_path}"\n')
                f.write(f'export WINEPREFIX="{wine_path}/.wine"\n')
            
            QMessageBox.information(self, "成功", f"已切换到Wine版本: {selected_wine}")
            self.update_version_info()
            self.select_wine()
        
        self.current_interaction_handler = handler
    
    def uninstall_wine(self):
        self.clear_interaction_area()
        self.interaction_title.setText("卸载Wine - 选择版本")
        
        wine_dirs = []
        for item in os.listdir(self.glibc_path):
            if item.startswith("wine-"):
                wine_dirs.append(item)
        
        opt_wine_path = os.path.join(self.opt_path, "wine")
        if os.path.exists(opt_wine_path):
            for item in os.listdir(opt_wine_path):
                wine_dirs.append(os.path.join("opt/wine", item))
        
        if not wine_dirs:
            QMessageBox.information(self, "提示", "没有找到可用的Wine版本")
            return
        
        wine_dirs = self.sort_version_list(wine_dirs)
        
        self.interaction_content.addItems(wine_dirs)
        
        def handler(selected_wine):
            reply = QMessageBox.question(
                self, "确认卸载", 
                f"确定要卸载Wine版本: {selected_wine}吗？这将删除整个目录！",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                wine_path = os.path.join(self.glibc_path, selected_wine)
                try:
                    shutil.rmtree(wine_path)
                    QMessageBox.information(self, "成功", f"已卸载Wine版本: {selected_wine}")
                    self.update_version_info()
                    self.uninstall_wine()
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"卸载失败: {str(e)}")
        
        self.current_interaction_handler = handler

    def uninstall_dxvk(self):
        self.uninstall_component("DXVK", os.path.join(self.opt_path, "dxvk"))
        
    def uninstall_vkd3d(self):
        self.uninstall_component("Vkd3d", os.path.join(self.opt_path, "vkd3d"))        
        
    def uninstall_turnip(self):
        self.uninstall_component("Turnip", os.path.join(self.opt_path, "turnip"))        
    
    def uninstall_box(self):
        self.uninstall_component("Box64", os.path.join(self.opt_path, "box"))
    
    def uninstall_all(self):
        self.clear_interaction_area()
        self.interaction_title.setText("卸载所有组件")
        self.interaction_content.hide()
        
        confirm_widget = QWidget()
        confirm_layout = QVBoxLayout(confirm_widget)
        
        info_label = QLabel("确定要卸载所有组件吗？\n这将清除Box、Turnip和DXVK！")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 16px;")
        confirm_layout.addWidget(info_label)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(20)
        confirm_btn = QPushButton("确认卸载")
        confirm_btn.setFixedSize(100, 35)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background: #FF6347;
                color: white;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #FF4500;
            }
        """)
        confirm_btn.clicked.connect(self._uninstall_all_components)
        button_layout.addWidget(confirm_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #00CED1;
                color: black;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #20B2AA;
            }
        """)
        cancel_btn.clicked.connect(lambda: self.show_sub_menu("uninstall"))
        button_layout.addWidget(cancel_btn)
        
        confirm_layout.addWidget(button_widget, alignment=Qt.AlignCenter)
        
        self.interaction_layout.addWidget(confirm_widget)
    
    def _uninstall_all_components(self):
        try:
            for component, path in [
                ("Box64", os.path.join(self.opt_path, "box")),
                ("Turnip", os.path.join(self.opt_path, "tz")),
                ("DXVK", os.path.join(self.opt_path, "dxvk"))
            ]:
                if os.path.exists(path):
                    shutil.rmtree(path)
            
            QMessageBox.information(self, "成功", "已卸载所有组件")
            self.update_version_info()
            self.show_sub_menu("uninstall")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"卸载失败: {str(e)}")
    
    def uninstall_component(self, name, path):
        if not os.path.exists(path):
            QMessageBox.information(self, "提示", f"{name} 未安装")
            return
        
        self.clear_interaction_area()
        self.interaction_title.setText(f"卸载{name} - 选择版本")
        
        files = [f for f in os.listdir(path) if f != ".last_selected"]
        if not files:
            QMessageBox.information(self, "提示", f"没有可用的{name}版本")
            return
        
        files = self.sort_version_list(files)
        
        self.interaction_content.addItems(files)
        
        def handler(selected_file):
            reply = QMessageBox.question(
                self, f"确认卸载{name}", 
                f"确定要卸载{name}版本: {selected_file}吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    os.remove(os.path.join(path, selected_file))
                    QMessageBox.information(self, "成功", f"已卸载{name}版本: {selected_file}")
                    self.update_version_info()
                    getattr(self, f"uninstall_{name.lower()}")()
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"卸载失败: {str(e)}")
        
        self.current_interaction_handler = handler
    
    def switch_language(self):
        self.clear_interaction_area()
        self.interaction_title.setText("切换语言配置")
        
        lc_path = os.path.join(self.usr_path, "lc")
        if not os.path.exists(lc_path):
            QMessageBox.information(self, "提示", "语言配置目录不存在")
            return
        
        configs = [f for f in os.listdir(lc_path) if f.endswith(".conf")]
        if not configs:
            QMessageBox.information(self, "提示", "没有可用的语言配置")
            return
        
        configs = sorted(configs)
        
        self.interaction_content.addItems(configs)
        
        def handler(config):
            try:
                target_conf = os.path.join(self.opt_path, "locale.conf")
                shutil.copy(os.path.join(lc_path, config), target_conf)
                QMessageBox.information(self, "成功", f"已切换到语言配置: {config}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"切换失败: {str(e)}")
        
        self.current_interaction_handler = handler
    
    def switch_fps(self):
        self.clear_interaction_area()
        self.interaction_title.setText("切换FPS配置")
        
        fps_path = os.path.join(self.usr_path, "fps")
        if not os.path.exists(fps_path):
            QMessageBox.information(self, "提示", "FPS配置目录不存在")
            return
        
        configs = [f for f in os.listdir(fps_path) if f.endswith(".conf")]
        if not configs:
            QMessageBox.information(self, "提示", "没有可用的FPS配置")
            return
        
        configs = sorted(configs)
        
        self.interaction_content.addItems(configs)
        
        def handler(config):
            try:
                target_conf = os.path.join(self.conf_path, "dxvk.conf")
                shutil.copy(os.path.join(fps_path, config), target_conf)
                QMessageBox.information(self, "成功", f"已切换到FPS配置: {config}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"切换失败: {str(e)}")
        
        self.current_interaction_handler = handler
    
    def switch_hud(self):
        self.clear_interaction_area()
        self.interaction_title.setText("切换HUD配置")
        
        hud_path = os.path.join(self.usr_path, "hud")
        if not os.path.exists(hud_path):
            QMessageBox.information(self, "提示", "HUD目录不存在")
            return
        
        configs = [f for f in os.listdir(hud_path) if f.endswith(".conf")]
        if not configs:
            QMessageBox.information(self, "提示", "没有可用的HUD配置")
            return
        
        configs = sorted(configs)
        
        self.interaction_content.addItems(configs)
        
        def handler(config):
            try:
                target_conf = os.path.join(self.conf_path, "hud.conf")
                shutil.copy(os.path.join(hud_path, config), target_conf)
                QMessageBox.information(self, "成功", f"已切换到HUD配置: {config}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"切换失败: {str(e)}")
        
        self.current_interaction_handler = handler
    
    def switch_dxvk(self):
        self.clear_interaction_area()
        self.interaction_title.setText("切换DXVK版本")
        
        dxvk_path = os.path.join(self.opt_path, "dxvk")
        if not os.path.exists(dxvk_path):
            QMessageBox.information(self, "提示", "DXVK目录不存在")
            return
        
        versions = [f for f in os.listdir(dxvk_path) if f != ".last_selected"]
        if not versions:
            QMessageBox.information(self, "提示", "没有可用的DXVK版本")
            return
        
        versions = self.sort_version_list(versions)
        
        self.interaction_content.addItems(versions)
        
        def handler(version):
            if not os.path.exists(self.wine_path_conf):
                QMessageBox.warning(self, "错误", "找不到Wine路径配置")
                return
            
            wine_path = None
            with open(self.wine_path_conf, 'r') as f:
                for line in f:
                    if line.startswith("export WINE_PATH="):
                        wine_path = line.split('=')[1].strip().strip('"')
                        break
            
            if not wine_path or not os.path.exists(wine_path):
                QMessageBox.warning(self, "错误", "无效的Wine路径")
                return
            
            dxvk_file = os.path.join(dxvk_path, version)
            try:
                if dxvk_file.endswith('.7z'):
                    with py7zr.SevenZipFile(dxvk_file, mode='r') as archive:
                        archive.extractall(path=os.path.join(wine_path, ".wine", "drive_c", "windows"))
                elif dxvk_file.endswith('.tar.gz') or dxvk_file.endswith('.tgz'):
                    with tarfile.open(dxvk_file, 'r:gz') as tar:
                        tar.extractall(os.path.join(wine_path, ".wine", "drive_c", "windows"))
                elif dxvk_file.endswith('.tar.xz'):
                    with tarfile.open(dxvk_file, 'r:xz') as tar:
                        tar.extractall(os.path.join(wine_path, ".wine", "drive_c", "windows"))
                elif dxvk_file.endswith('.tar'):
                    with tarfile.open(dxvk_file, 'r:') as tar:
                        tar.extractall(os.path.join(wine_path, ".wine", "drive_c", "windows"))
                else:
                    QMessageBox.warning(self, "错误", "不支持的压缩格式")
                    return
                
                with open(os.path.join(dxvk_path, ".last_selected"), 'w') as f:
                    f.write(version)
                
                QMessageBox.information(self, "成功", f"已切换到DXVK版本: {version}")
                self.update_version_info()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"切换失败: {str(e)}")
        
        self.current_interaction_handler = handler
    
    def switch_vkd3d(self):
        self.clear_interaction_area()
        self.interaction_title.setText("切换VKD3D版本")
        
        vkd3d_path = os.path.join(self.opt_path, "vkd3d")
        if not os.path.exists(vkd3d_path):
            QMessageBox.information(self, "提示", "VKD3D目录不存在")
            return
        
        versions = [f for f in os.listdir(vkd3d_path) if f != ".last_selected"]
        if not versions:
            QMessageBox.information(self, "提示", "没有可用的VKD3D版本")
            return
        
        versions = self.sort_version_list(versions)
        
        self.interaction_content.addItems(versions)
        
        def handler(version):
            if not os.path.exists(self.wine_path_conf):
                QMessageBox.warning(self, "错误", "找不到Wine路径配置")
                return
            
            wine_path = None
            with open(self.wine_path_conf, 'r') as f:
                for line in f:
                    if line.startswith("export WINE_PATH="):
                        wine_path = line.split('=')[1].strip().strip('"')
                        break
            
            if not wine_path or not os.path.exists(wine_path):
                QMessageBox.warning(self, "错误", "无效的Wine路径")
                return
            
            vkd3d_file = os.path.join(vkd3d_path, version)
            try:
                if vkd3d_file.endswith('.7z'):
                    with py7zr.SevenZipFile(vkd3d_file, mode='r') as archive:
                        archive.extractall(path=os.path.join(wine_path, ".wine", "drive_c", "windows"))
                elif vkd3d_file.endswith('.tar.gz') or vkd3d_file.endswith('.tgz'):
                    with tarfile.open(vkd3d_file, 'r:gz') as tar:
                        tar.extractall(os.path.join(wine_path, ".wine", "drive_c", "windows"))
                elif vkd3d_file.endswith('.tar.xz'):
                    with tarfile.open(vkd3d_file, 'r:xz') as tar:
                        tar.extractall(os.path.join(wine_path, ".wine", "drive_c", "windows"))
                elif vkd3d_file.endswith('.tar'):
                    with tarfile.open(vkd3d_file, 'r:') as tar:
                        tar.extractall(os.path.join(wine_path, ".wine", "drive_c", "windows"))
                else:
                    QMessageBox.warning(self, "错误", "不支持的压缩格式")
                    return
                
                with open(os.path.join(vkd3d_path, ".last_selected"), 'w') as f:
                    f.write(version)
                
                QMessageBox.information(self, "成功", f"已切换到VKD3D版本: {version}")
                self.update_version_info()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"切换失败: {str(e)}")
        
        self.current_interaction_handler = handler
    
    def switch_turnip(self):
        self.clear_interaction_area()
        self.interaction_title.setText("切换Turnip版本")
        
        tz_path = os.path.join(self.opt_path, "turnip")
        if not os.path.exists(tz_path):
            QMessageBox.information(self, "提示", "Turnip目录不存在")
            return
        
        versions = [f for f in os.listdir(tz_path) if f != ".last_selected"]
        if not versions:
            QMessageBox.information(self, "提示", "没有可用的Turnip版本")
            return
        
        versions = self.sort_version_list(versions)
        
        self.interaction_content.addItems(versions)
        
        def handler(version):
            tz_file = os.path.join(tz_path, version)
            try:
                if tz_file.endswith('.7z'):
                    with py7zr.SevenZipFile(tz_file, mode='r') as archive:
                        archive.extractall(path=self.glibc_path)
                elif tz_file.endswith('.tar.gz') or tz_file.endswith('.tgz'):
                    with tarfile.open(tz_file, 'r:gz') as tar:
                        tar.extractall(self.glibc_path)
                elif tz_file.endswith('.tar.xz'):
                    with tarfile.open(tz_file, 'r:xz') as tar:
                        tar.extractall(self.glibc_path)
                elif tz_file.endswith('.tar'):
                    with tarfile.open(tz_file, 'r:') as tar:
                        tar.extractall(self.glibc_path)
                else:
                    QMessageBox.warning(self, "错误", "不支持的压缩格式")
                    return
                
                with open(os.path.join(tz_path, ".last_selected"), 'w') as f:
                    f.write(version)
                
                QMessageBox.information(self, "成功", f"已切换到Turnip版本: {version}")
                self.update_version_info()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"切换失败: {str(e)}")
        
        self.current_interaction_handler = handler
    
    def switch_box(self):
        self.clear_interaction_area()
        self.interaction_title.setText("切换Box64/86版本")
        
        box_path = os.path.join(self.opt_path, "box")
        if not os.path.exists(box_path):
            QMessageBox.information(self, "提示", "Box64/86目录不存在")
            return
        
        versions = os.listdir(box_path)
        if not versions:
            QMessageBox.information(self, "提示", "没有可用的Box64/86版本")
            return
        
        versions = self.sort_version_list(versions)
        
        self.interaction_content.addItems(versions)
        
        def handler(version):
            box_file = os.path.join(box_path, version)
            try:
                if box_file.endswith('.7z'):
                    with py7zr.SevenZipFile(box_file, mode='r') as archive:
                        archive.extractall(path=os.path.join(self.glibc_path, "bin"))
                elif box_file.endswith('.tar.gz') or box_file.endswith('.tgz'):
                    with tarfile.open(box_file, 'r:gz') as tar:
                        tar.extractall(os.path.join(self.glibc_path, "bin"))
                elif box_file.endswith('.tar.xz'):
                    with tarfile.open(box_file, 'r:xz') as tar:
                        tar.extractall(os.path.join(self.glibc_path, "bin"))
                elif box_file.endswith('.tar'):
                    with tarfile.open(box_file, 'r:') as tar:
                        tar.extractall(os.path.join(self.glibc_path, "bin"))
                else:
                    QMessageBox.warning(self, "错误", "不支持的压缩格式")
                    return
                
                box64_path = os.path.join(self.glibc_path, "bin", "box64")
                box86_path = os.path.join(self.glibc_path, "bin", "box86")
                
                os.chmod(box64_path, 0o755)
                if os.path.exists(box86_path):
                    os.chmod(box86_path, 0o755)
                
                QMessageBox.information(self, "成功", f"已切换到Box64版本: {version}")
                self.update_version_info()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"切换失败: {str(e)}")
        
        self.current_interaction_handler = handler
    
    def sort_version_list(self, file_list):
        def version_key(filename):
            version_part = re.search(r'(\d+(?:\.\d+)*)', filename)
            if version_part:
                version = version_part.group(1)
                return tuple(map(int, version.split('.')))
            return (0,)
        
        return sorted(file_list, key=version_key, reverse=True)
    
    def dynarec_settings(self):
        self.clear_interaction_area()
        self.interaction_title.setText("Dynarec设置 - 选择模式")
        
        options = ["完全自定义模式", "基于预设的配置器"]
        self.interaction_content.addItems(options)
        
        def handler(option):
            if option == "完全自定义模式":
                self.dynarec_custom_mode()
            else:
                self.dynarec_preset_mode()
        
        self.current_interaction_handler = handler
    
    def dynarec_custom_mode(self):
        self.clear_interaction_area()
        self.interaction_title.setText("Dynarec完全自定义模式")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll.setWidget(scroll_widget)
        
        grid = QGridLayout(scroll_widget)
        grid.setSpacing(10)
        
        default_options = [
            ("BOX64_DYNAREC_ALIGNED_ATOMICS", "1", "0-1"),
            ("BOX64_DYNAREC_BIGBLOCK", "2", "0-2"),
            ("BOX64_DYNAREC_FASTNAN", "1", "0-1"),
            ("BOX64_DYNAREC_SAFEFLAGS", "2", "0-2"),
            ("BOX64_DYNAREC_STRONGMEM", "3", "1-3"),
            ("BOX64_DYNAREC_WAIT", "1", "0-1"),
            ("BOX64_DYNAREC_X87DOUBLE", "1", "0-1"),
            ("BOX64_DYNAREC_CALLRET", "1", "0-1"),
            ("BOX64_DYNAREC_FASTROUND", "1", "0-1"),
            ("BOX64_IGNOREINT3", "1", "0-1"),
            ("BOX86_DYNAREC_ALIGNED_ATOMICS", "1", "0-1"),
            ("BOX86_DYNAREC_BIGBLOCK", "2", "0-2"),
            ("BOX86_DYNAREC_FASTNAN", "1", "0-1"),
            ("BOX86_DYNAREC_SAFEFLAGS", "2", "0-2"),
            ("BOX86_DYNAREC_STRONGMEM", "3", "1-3"),
            ("BOX86_DYNAREC_WAIT", "1", "0-1"),
            ("BOX86_DYNAREC_X87DOUBLE", "1", "0-1"),
            ("BOX86_DYNAREC_CALLRET", "1", "0-1"),
            ("BOX86_DYNAREC_FASTROUND", "1", "0-1"),
            ("BOX86_IGNOREINT3", "1", "0-1")
        ]
        
        self.dynarec_spinboxes = {}
        self.custom_vars = {}
        
        dynarec_envs_conf = os.path.join(self.opt_path, "dynarec_envs.conf")
        existing_vars = {}
        
        if os.path.exists(dynarec_envs_conf):
            try:
                with open(dynarec_envs_conf, 'r') as f:
                    for line in f:
                        if line.strip() and '=' in line:
                            var = line.split('=')[0].strip('["] ')
                            value = line.split('=')[1].strip().strip('"]')
                            existing_vars[var] = value
            except Exception as e:
                print(f"读取dynarec_envs.conf出错: {e}")
        
        row = 0
        for name, default, range_text in default_options:
            value = existing_vars.get(name, default)
            label = QLabel(f"{name} ({range_text}):")
            label.setStyleSheet("color: black;")
            spin = QSpinBox()
            spin.setMinimum(int(range_text.split('-')[0]))
            spin.setMaximum(int(range_text.split('-')[1]))
            spin.setValue(int(value))
            
            grid.addWidget(label, row, 0)
            grid.addWidget(spin, row, 1)
            self.dynarec_spinboxes[name] = spin
            row += 1
        
        for var, value in existing_vars.items():
            if var not in self.dynarec_spinboxes:
                label = QLabel(f"{var}:")
                label.setStyleSheet("color: black;")
                spin = QSpinBox()
                spin.setMinimum(0)
                spin.setMaximum(999)
                spin.setValue(int(value))
                
                grid.addWidget(label, row, 0)
                grid.addWidget(spin, row, 1)
                self.custom_vars[var] = spin
                row += 1
        
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)
        
        add_btn = QPushButton("添加变量")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        add_btn.clicked.connect(self.add_dynarec_var)
        
        del_btn = QPushButton("删除变量")
        del_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #d32f2f;
            }
        """)
        del_btn.clicked.connect(self.del_dynarec_var)
        
        reset_btn = QPushButton("重置默认")
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #FF9800;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #F57C00;
            }
        """)
        reset_btn.clicked.connect(self.reset_dynarec_default)
        
        save_btn = QPushButton("保存配置")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        save_btn.clicked.connect(self.save_dynarec_custom_config)
        
        back_btn = QPushButton("返回")
        back_btn.setStyleSheet("""
            QPushButton {
                background: #9E9E9E;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #757575;
            }
        """)
        back_btn.clicked.connect(lambda: self.show_sub_menu("advanced"))
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(del_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(back_btn)
        
        layout.addWidget(scroll)
        layout.addWidget(button_container)
        
        self.interaction_content.hide()
        
        self.interaction_layout.addWidget(container)
    
    def add_dynarec_var(self):
        var_name, ok = QInputDialog.getText(
            self, "添加变量", "请输入变量名:"
        )
        
        if ok and var_name:
            if var_name in self.dynarec_spinboxes or var_name in self.custom_vars:
                QMessageBox.warning(self, "错误", "变量已存在！")
                return
            
            max_value, ok = QInputDialog.getInt(
                self, "设置上限值", "请输入变量的上限值(纯数字):",
                min=1, max=999, value=1
            )
            
            if not ok:
                return
            
            scroll = self.interaction_layout.itemAt(1).widget().findChild(QScrollArea)
            scroll_widget = scroll.widget()
            grid = scroll_widget.layout()
            
            row = grid.rowCount()
            label = QLabel(f"{var_name} (0-{max_value}):")
            label.setStyleSheet("color: black;")
            spin = QSpinBox()
            spin.setMinimum(0)
            spin.setMaximum(max_value)
            spin.setValue(0)
            
            grid.addWidget(label, row, 0)
            grid.addWidget(spin, row, 1)
            self.custom_vars[var_name] = spin
    
    def del_dynarec_var(self):
        if not self.custom_vars:
            QMessageBox.warning(self, "错误", "没有可删除的自定义变量！")
            return
        
        var_name, ok = QInputDialog.getItem(
            self, "删除变量", "选择要删除的变量:",
            list(self.custom_vars.keys()), 0, False
        )
        
        if ok and var_name:
            scroll = self.interaction_layout.itemAt(1).widget().findChild(QScrollArea)
            scroll_widget = scroll.widget()
            grid = scroll_widget.layout()
            
            for i in range(grid.count()):
                widget = grid.itemAt(i).widget()
                if isinstance(widget, QLabel) and widget.text().startswith(var_name):
                    label = grid.itemAt(i).widget()
                    spin = grid.itemAt(i+1).widget()
                    
                    grid.removeWidget(label)
                    grid.removeWidget(spin)
                    
                    label.deleteLater()
                    spin.deleteLater()
                    
                    del self.custom_vars[var_name]
                    break
    
    def reset_dynarec_default(self):
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要重置为默认Dynarec配置吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            dynarec_envs_conf = os.path.join(self.opt_path, "dynarec_envs.conf")
            try:
                if os.path.exists(dynarec_envs_conf):
                    os.remove(dynarec_envs_conf)
                
                dynarec_conf_dir = os.path.join(self.conf_path, "dynarec")
                if os.path.exists(dynarec_conf_dir):
                    shutil.rmtree(dynarec_conf_dir)
                    os.makedirs(dynarec_conf_dir)
                
                dynarec_preset_conf = os.path.join(self.conf_path, "dynarec_preset.conf")
                with open(dynarec_preset_conf, 'w') as f:
                    f.write("export DYNAREC_SETTINGS_SCRIPT=1\n")
                    f.write("export DYNAREC_CURRENT_PRESET=none\n")
                
                QMessageBox.information(self, "成功", "已重置为默认Dynarec配置")
                self.dynarec_custom_mode()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"重置失败: {str(e)}")
    
    def save_dynarec_custom_config(self):
        config_name, ok = QInputDialog.getText(
            self, "保存配置", "请输入配置名称:"
        )
        
        if not ok or not config_name:
            return
        
        dynarec_envs_conf = os.path.join(self.opt_path, "dynarec_envs.conf")
        try:
            with open(dynarec_envs_conf, 'w') as f:
                for name, spin in self.dynarec_spinboxes.items():
                    f.write(f'["{name}"]={spin.value()}\n')
                
                for name, spin in self.custom_vars.items():
                    f.write(f'["{name}"]={spin.value()}\n')
            
            dynarec_conf_dir = os.path.join(self.conf_path, "dynarec")
            os.makedirs(dynarec_conf_dir, exist_ok=True)
            
            custom_conf = os.path.join(dynarec_conf_dir, "custom.conf")
            with open(custom_conf, 'w') as f:
                for name, spin in self.dynarec_spinboxes.items():
                    f.write(f"export {name}={spin.value()}\n")
                
                for name, spin in self.custom_vars.items():
                    f.write(f"export {name}={spin.value()}\n")
            
            dynarec_preset_conf = os.path.join(self.conf_path, "dynarec_preset.conf")
            with open(dynarec_preset_conf, 'w') as f:
                f.write("export DYNAREC_SETTINGS_SCRIPT=1\n")
                f.write(f'export DYNAREC_CURRENT_PRESET={config_name}\n')
            
            QMessageBox.information(self, "成功", f"Dynarec配置 {config_name} 已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
    
    def dynarec_preset_mode(self):
        self.clear_interaction_area()
        self.interaction_title.setText("Dynarec预设配置模式")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        
        self.last_preset_label = QLabel()
        self.last_preset_label.setAlignment(Qt.AlignCenter)
        self.last_preset_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
                background-color: #e6f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 5px;
                padding: 5px;
                margin-bottom: 5px;
                min-height: 50px;
            }
        """)
        self.load_last_preset()
        
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        input_label = QLabel("输入数字组合 (如: 1, 44, 1423):")
        input_label.setStyleSheet("font-size: 14px;")
        
        self.preset_input = QLineEdit()
        self.preset_input.setPlaceholderText("请输入数字组合")
        self.preset_input.textChanged.connect(self.validate_preset_input)
        
        save_btn = QPushButton("保存配置")
        save_btn.setFixedHeight(30)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_dynarec_preset_config)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.preset_input)
        input_layout.addWidget(save_btn)
        
        top_layout.addWidget(self.last_preset_label)
        top_layout.addWidget(input_widget)
        
        preset_info = QTextEdit()
        preset_info.setReadOnly(True)
        preset_info.setHtml("""
        <h3>预设说明:</h3>
        <p><b>1</b> - 最大兼容性 (非常慢)</p>
        <p><b>2</b> - 默认+兼容性</p>
        <p><b>3</b> - 默认 (SAFEFLAGS=1)</p>
        <p><b>4</b> - 性能 (SAFEFLAGS=0)</p>
        
        <h3>其他兼容性标志:</h3>
        <p><b>1</b> - FASTNAN=0</p>
        <p><b>2</b> - X87DOUBLE=1</p>
        <p><b>3</b> - STRONGMEM=1</p>
        <p><b>4</b> - SAFEFLAGS=2</p>
        <p><b>5</b> - CALLRET=1 (提高性能)</p>
        <p><b>6</b> - FASTROUND=0</p>
        <p><b>7</b> - STRONGMEM=3</p>
        <p><b>8</b> - BIGBLOCK=0 (修复某些游戏中的冻结问题)</p>
        <p><b>9</b> - IGNOREINT3=1</p>
        
        <h3>组合示例:</h3>
        <p><b>1</b> - 全部使用模式1</p>
        <p><b>44</b> - 全部使用模式4</p>
        <p><b>1423</b> - 依次使用模式1、4、2、3</p>
        <p><b>123456789</b> - 应用所有兼容性标志</p>
        """)
        preset_info.setFixedHeight(250)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        back_btn = QPushButton("返回")
        back_btn.setFixedSize(120, 35)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #d32f2f;
            }
        """)
        back_btn.clicked.connect(lambda: self.show_sub_menu("advanced"))
        
        button_layout.addStretch()
        button_layout.addWidget(back_btn)
        button_layout.addStretch()
        
        layout.addWidget(top_widget)
        layout.addWidget(preset_info)
        layout.addWidget(button_widget)
        
        self.interaction_content.hide()
        
        self.interaction_layout.addWidget(container)
    
    def load_last_preset(self):
        dynarec_preset_conf = os.path.join(self.conf_path, "dynarec_preset.conf")
        if os.path.exists(dynarec_preset_conf):
            try:
                with open(dynarec_preset_conf, 'r') as f:
                    for line in f:
                        if line.startswith("export DYNAREC_CURRENT_PRESET="):
                            preset = line.split('=')[1].strip().strip('"')
                            if preset != "none":
                                self.last_preset_label.setText(f"当前预设:\n{preset}")
                            else:
                                self.last_preset_label.setText("当前预设: 无")
                            break
            except Exception as e:
                print(f"加载预设配置出错: {e}")
    
    def validate_preset_input(self, text):
        valid_text = ''.join([c for c in text if c.isdigit()])
        if valid_text != text:
            self.preset_input.setText(valid_text)
    
    def save_dynarec_preset_config(self):
        preset_text = self.preset_input.text().strip()
        
        if len(preset_text) == 0:
            QMessageBox.warning(self, "错误", "请输入数字组合！")
            return
        
        presets = {
            "1": {
                "BOX64_DYNAREC_BIGBLOCK": "0",
                "BOX86_DYNAREC_BIGBLOCK": "0",
                "BOX64_DYNAREC_ALIGNED_ATOMICS": "1",
                "BOX86_DYNAREC_ALIGNED_ATOMICS": "1",
                "BOX64_DYNAREC_X87DOUBLE": "1",
                "BOX86_DYNAREC_X87DOUBLE": "1",
                "BOX64_DYNAREC_FASTNAN": "0",
                "BOX86_DYNAREC_FASTNAN": "0",
                "BOX64_DYNAREC_FASTROUND": "0",
                "BOX86_DYNAREC_FASTROUND": "0",
                "BOX64_DYNAREC_SAFEFLAGS": "2",
                "BOX86_DYNAREC_SAFEFLAGS": "2",
                "BOX64_DYNAREC_STRONGMEM": "3",
                "BOX86_DYNAREC_STRONGMEM": "3",
                "BOX64_DYNAREC_WAIT": "1",
                "BOX86_DYNAREC_WAIT": "1",
                "BOX64_DYNAREC_CALLRET": "0",
                "BOX86_DYNAREC_CALLRET": "0",
                "BOX64_IGNOREINT3": "1",
                "BOX86_IGNOREINT3": "1"
            },
            "2": {
                "BOX64_DYNAREC_BIGBLOCK": "2",
                "BOX86_DYNAREC_BIGBLOCK": "2",
                "BOX64_DYNAREC_ALIGNED_ATOMICS": "1",
                "BOX86_DYNAREC_ALIGNED_ATOMICS": "1",
                "BOX64_DYNAREC_X87DOUBLE": "1",
                "BOX86_DYNAREC_X87DOUBLE": "1",
                "BOX64_DYNAREC_FASTNAN": "0",
                "BOX86_DYNAREC_FASTNAN": "0",
                "BOX64_DYNAREC_FASTROUND": "1",
                "BOX86_DYNAREC_FASTROUND": "1",
                "BOX64_DYNAREC_SAFEFLAGS": "2",
                "BOX86_DYNAREC_SAFEFLAGS": "2",
                "BOX64_DYNAREC_STRONGMEM": "2",
                "BOX86_DYNAREC_STRONGMEM": "2",
                "BOX64_DYNAREC_WAIT": "1",
                "BOX86_DYNAREC_WAIT": "1",
                "BOX64_DYNAREC_CALLRET": "0",
                "BOX86_DYNAREC_CALLRET": "0",
                "BOX64_IGNOREINT3": "1",
                "BOX86_IGNOREINT3": "1"
            },
            "3": {
                "BOX64_DYNAREC_BIGBLOCK": "2",
                "BOX86_DYNAREC_BIGBLOCK": "2",
                "BOX64_DYNAREC_ALIGNED_ATOMICS": "1",
                "BOX86_DYNAREC_ALIGNED_ATOMICS": "1",
                "BOX64_DYNAREC_X87DOUBLE": "1",
                "BOX86_DYNAREC_X87DOUBLE": "1",
                "BOX64_DYNAREC_FASTNAN": "1",
                "BOX86_DYNAREC_FASTNAN": "1",
                "BOX64_DYNAREC_FASTROUND": "1",
                "BOX86_DYNAREC_FASTROUND": "1",
                "BOX64_DYNAREC_SAFEFLAGS": "1",
                "BOX86_DYNAREC_SAFEFLAGS": "1",
                "BOX64_DYNAREC_STRONGMEM": "1",
                "BOX86_DYNAREC_STRONGMEM": "1",
                "BOX64_DYNAREC_WAIT": "1",
                "BOX86_DYNAREC_WAIT": "1",
                "BOX64_DYNAREC_CALLRET": "0",
                "BOX86_DYNAREC_CALLRET": "0",
                "BOX64_IGNOREINT3": "1",
                "BOX86_IGNOREINT3": "1"
            },
            "4": {
                "BOX64_DYNAREC_BIGBLOCK": "2",
                "BOX86_DYNAREC_BIGBLOCK": "2",
                "BOX64_DYNAREC_ALIGNED_ATOMICS": "1",
                "BOX86_DYNAREC_ALIGNED_ATOMICS": "1",
                "BOX64_DYNAREC_X87DOUBLE": "1",
                "BOX86_DYNAREC_X87DOUBLE": "1",
                "BOX64_DYNAREC_FASTNAN": "1",
                "BOX86_DYNAREC_FASTNAN": "1",
                "BOX64_DYNAREC_FASTROUND": "1",
                "BOX86_DYNAREC_FASTROUND": "1",
                "BOX64_DYNAREC_SAFEFLAGS": "0",
                "BOX86_DYNAREC_SAFEFLAGS": "0",
                "BOX64_DYNAREC_STRONGMEM": "1",
                "BOX86_DYNAREC_STRONGMEM": "1",
                "BOX64_DYNAREC_WAIT": "1",
                "BOX86_DYNAREC_WAIT": "1",
                "BOX64_DYNAREC_CALLRET": "0",
                "BOX86_DYNAREC_CALLRET": "0",
                "BOX64_IGNOREINT3": "1",
                "BOX86_IGNOREINT3": "1"
            }
        }
        
        compatibility_flags = {
            "1": {"BOX64_DYNAREC_FASTNAN": "0", "BOX86_DYNAREC_FASTNAN": "0"},
            "2": {"BOX64_DYNAREC_X87DOUBLE": "1", "BOX86_DYNAREC_X87DOUBLE": "1"},
            "3": {"BOX64_DYNAREC_STRONGMEM": "1", "BOX86_DYNAREC_STRONGMEM": "1"},
            "4": {"BOX64_DYNAREC_SAFEFLAGS": "2", "BOX86_DYNAREC_SAFEFLAGS": "2"},
            "5": {"BOX64_DYNAREC_CALLRET": "1", "BOX86_DYNAREC_CALLRET": "1"},
            "6": {"BOX64_DYNAREC_FASTROUND": "0", "BOX86_DYNAREC_FASTROUND": "0"},
            "7": {"BOX64_DYNAREC_STRONGMEM": "3", "BOX86_DYNAREC_STRONGMEM": "3"},
            "8": {"BOX64_DYNAREC_BIGBLOCK": "0", "BOX86_DYNAREC_BIGBLOCK": "0"},
            "9": {"BOX64_IGNOREINT3": "1", "BOX86_IGNOREINT3": "1"}
        }
        
        try:
            dynarec_conf_dir = os.path.join(self.conf_path, "dynarec")
            os.makedirs(dynarec_conf_dir, exist_ok=True)
            
            custom_conf = os.path.join(dynarec_conf_dir, "custom.conf")
            with open(custom_conf, 'w') as f:
                for num in preset_text:
                    if num in presets:
                        for key, value in presets[num].items():
                            f.write(f"export {key}={value}\n")
                
                for num in preset_text:
                    if num in compatibility_flags:
                        for key, value in compatibility_flags[num].items():
                            f.write(f"export {key}={value}\n")
            
            dynarec_preset_conf = os.path.join(self.conf_path, "dynarec_preset.conf")
            with open(dynarec_preset_conf, 'w') as f:
                f.write("export DYNAREC_SETTINGS_SCRIPT=2\n")
                f.write(f'export DYNAREC_CURRENT_PRESET={preset_text}\n')
            
            QMessageBox.information(self, "成功", f"Dynarec预设配置已保存\n组合: {preset_text}")
            self.load_last_preset()
            self.preset_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
    
    def set_cpu_cores(self):
        self.clear_interaction_area()
        self.interaction_title.setText("设置CPU核心")
        
        self.interaction_content.hide()
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        self.current_cores_label = QLabel()
        self.current_cores_label.setAlignment(Qt.AlignCenter)
        self.current_cores_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
                background-color: #e6f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 5px;
                padding: 5px;
                margin-bottom: 5px;
                min-height: 50px;
            }
        """)
        self.update_current_cores_info()
        layout.addWidget(self.current_cores_label)
        
        core_group = QGroupBox("选择CPU核心 (0-7)")
        core_layout = QGridLayout()
        
        self.core_checks = []
        for i in range(8):
            check = QCheckBox(f"核心 {i}")
            check.setStyleSheet("""
                QCheckBox {
                    font-size: 14px;
                }
                QCheckBox:disabled {
                    color: #888888;
                }
            """)
            self.core_checks.append(check)
            core_layout.addWidget(check, i//4, i%4)
        
        core_group.setLayout(core_layout)
        
        mode_group = QGroupBox("选择核心模式")
        mode_layout = QVBoxLayout()
        
        self.mode_group = QButtonGroup()
        
        modes = [
            ("性能模式 (所有核心)", "0-7"),
            ("平衡模式 (4-7)", "4-7"),
            ("省电模式 (6-7)", "6-7"),
            ("自定义模式", "custom")
        ]
        
        for i, (text, value) in enumerate(modes):
            radio = QRadioButton(text)
            radio.setStyleSheet("QRadioButton { font-size: 14px; }")
            self.mode_group.addButton(radio, i)
            mode_layout.addWidget(radio)
        
        mode_group.setLayout(mode_layout)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(5)
        
        save_btn = QPushButton("保存设置")
        save_btn.setFixedSize(100, 35)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_cpu_cores)
        
        back_btn = QPushButton("返回")
        back_btn.setFixedSize(100, 35)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #d32f2f;
            }
        """)
        back_btn.clicked.connect(lambda: self.show_sub_menu("advanced"))
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(back_btn)

        layout.addWidget(core_group)
        layout.addWidget(mode_group)
        layout.addWidget(button_widget, alignment=Qt.AlignCenter)
        
        self.mode_group.buttonClicked[int].connect(self.update_core_selection)
        
        self.load_last_core_selection()
        
        self.interaction_layout.addWidget(container)

    def update_current_cores_info(self):
        if os.path.exists(self.cores_conf):
            try:
                with open(self.cores_conf, 'r') as f:
                    primary_cores = ""
                    secondary_cores = ""
                    current_mode = -1
                    
                    for line in f:
                        line = line.strip()
                        if line.startswith("export PRIMARY_CORES="):
                            primary_cores = line.split('=')[1]
                        elif line.startswith("export SECONDARY_CORES="):
                            secondary_cores = line.split('=')[1]
                        elif line.startswith("export CURRENT_MODE="):
                            current_mode_str = line.split('=')[1]
                            try:
                                current_mode = int(current_mode_str)
                            except ValueError:
                                current_mode = -1
                    
                    mode_names = ["性能模式 (0-7)", "平衡模式 (4-7)", "省电模式 (6-7)", "自定义模式"]
                    mode_text = mode_names[current_mode] if 0 <= current_mode < 4 else "未设置"
                    
                    info_text = f"当前模式: {mode_text}\n主核心: {primary_cores if primary_cores else '无'}\n辅助核心: {secondary_cores if secondary_cores else '无'}"
                    
                    self.current_cores_label.setText(info_text)
            except Exception as e:
                print(f"加载核心配置出错: {e}")
                self.current_cores_label.setText("当前核心分配: 未知")
        else:
            self.current_cores_label.setText("当前核心分配: 未设置")

    def load_last_core_selection(self):
        if os.path.exists(self.cores_conf):
            try:
                with open(self.cores_conf, 'r') as f:
                    primary_cores = []
                    current_mode = -1
                    
                    for line in f:
                        line = line.strip()
                        if line.startswith("export PRIMARY_CORES="):
                            primary_str = line.split('=')[1]
                            primary_cores = self.parse_core_range(primary_str)
                        elif line.startswith("export CURRENT_MODE="):
                            current_mode_str = line.split('=')[1]
                            try:
                                current_mode = int(current_mode_str)
                            except ValueError:
                                current_mode = -1
                    
                    for i, check in enumerate(self.core_checks):
                        check.setChecked(i in primary_cores)
                    
                    if current_mode == 0:
                        self.mode_group.button(0).setChecked(True)
                        self.lock_preset_cores(0)
                    elif current_mode == 1:
                        self.mode_group.button(1).setChecked(True)
                        self.lock_preset_cores(1)
                    elif current_mode == 2:
                        self.mode_group.button(2).setChecked(True)
                        self.lock_preset_cores(2)
                    else:
                        self.mode_group.button(3).setChecked(True)
                        for check in self.core_checks:
                            check.setEnabled(True)
            except Exception as e:
                print(f"加载核心配置出错: {e}")

    def parse_core_range(self, core_str):
        cores = []
        if not core_str:
            return cores
            
        for part in core_str.split(','):
            part = part.strip()
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    cores.extend(range(start, end+1))
                except ValueError:
                    continue
            else:
                try:
                    cores.append(int(part))
                except ValueError:
                    continue
        return sorted(cores)

    def update_core_selection(self, mode_id):
        if mode_id == 0:
            for i, check in enumerate(self.core_checks):
                check.setChecked(True)
                check.setEnabled(False)
        elif mode_id == 1:
            for i, check in enumerate(self.core_checks):
                check.setChecked(i >= 4)
                check.setEnabled(False)
        elif mode_id == 2:
            for i, check in enumerate(self.core_checks):
                check.setChecked(i >= 6)
                check.setEnabled(False)
        else:
            for check in self.core_checks:
                check.setEnabled(True)

    def lock_preset_cores(self, mode_id):
        if mode_id == 0:
            for check in self.core_checks:
                check.setEnabled(False)
        elif mode_id == 1:
            for check in self.core_checks:
                check.setEnabled(False)
        elif mode_id == 2:
            for check in self.core_checks:
                check.setEnabled(False)

    def save_cpu_cores(self):
        current_mode = self.mode_group.checkedId()
        if current_mode == -1:
            QMessageBox.warning(self, "错误", "请选择核心模式！")
            return
        
        selected_cores = [i for i, check in enumerate(self.core_checks) if check.isChecked()]
        
        if current_mode == 0:
            primary_str = "0-7"
            secondary_str = "0-0"
        elif current_mode == 1:
            primary_str = "4-7"
            secondary_str = "0-4"
        elif current_mode == 2:
            primary_str = "6-7"
            secondary_str = "0-6"
        else:
            if not selected_cores:
                QMessageBox.warning(self, "错误", "请至少选择一个CPU核心！")
                return
            
            primary_str = self.generate_core_range_str(selected_cores)
            
            first_primary = min(selected_cores)
            secondary_part1 = list(range(0, first_primary + 1))
            
            all_cores = set(range(8))
            unselected_cores = sorted(list(all_cores - set(selected_cores)))
            
            secondary_cores = sorted(list(set(secondary_part1 + unselected_cores)))
            secondary_str = self.generate_core_range_str(secondary_cores)
        
        try:
            with open(self.cores_conf, 'w') as f:
                f.write(f'export PRIMARY_CORES={primary_str}\n')
                f.write(f'export SECONDARY_CORES={secondary_str}\n')
                f.write(f'export CURRENT_MODE={current_mode}\n')
            
            self.update_current_cores_info()
            
            mode_names = ["性能模式 (0-7)", "平衡模式 (4-7)", "省电模式 (6-7)", "自定义模式"]
            mode_text = mode_names[current_mode]
            QMessageBox.information(
                self, "成功", 
                f"CPU核心设置已保存\n当前模式: {mode_text}\n主核心: {primary_str}\n辅助核心: {secondary_str}"
            )
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def generate_core_range_str(self, cores):
        if not cores:
            return ""
        
        cores = sorted(cores)
        ranges = []
        start = cores[0]
        prev = cores[0]
        
        for core in cores[1:]:
            if core == prev + 1:
                prev = core
            else:
                if start == prev:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{prev}")
                start = core
                prev = core
        
        if start == prev:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{prev}")
        
        return ",".join(ranges)
    
    def backup_restore(self):
        self.clear_interaction_area()
        self.interaction_title.setText("备份/恢复 - 选择操作")
        
        options = ["备份GLIBC环境", "恢复GLIBC环境"]
        self.interaction_content.addItems(options)
        
        def handler(option):
            if option == "备份GLIBC环境":
                self.backup_glibc()
            else:
                self.restore_glibc()
        
        self.current_interaction_handler = handler
    
    def backup_glibc(self):
        class BackupThread(QThread):
            finished = pyqtSignal(bool, str)
            progress = pyqtSignal(int)
            log_message = pyqtSignal(str)
            
            def __init__(self, source_path, target_path, format):
                super().__init__()
                self.source_path = source_path
                self.target_path = target_path
                self.format = format
                self.canceled = False
            
            def run(self):
                try:
                    self.log_message.emit(f"开始备份: {self.source_path}")
                    
                    if self.format == '7z':
                        self.backup_to_7z()
                    elif self.format == 'gz':
                        self.backup_to_tar('w:gz')
                    elif self.format == 'xz':
                        self.backup_to_tar('w:xz')
                    elif self.format == 'tar':
                        self.backup_to_tar('w:')
                    else:
                        self.finished.emit(False, f"不支持的压缩格式: {self.format}")
                        return
                    
                    if not self.canceled:
                        self.finished.emit(True, f"备份成功保存到: {self.target_path}")
                
                except Exception as e:
                    self.finished.emit(False, f"备份失败: {str(e)}")
            
            def backup_to_7z(self):
                with py7zr.SevenZipFile(self.target_path, mode='w') as archive:
                    total_files = 0
                    for root, dirs, files in os.walk(self.source_path):
                        total_files += len(files)
                    
                    if total_files == 0:
                        raise ValueError("没有找到要备份的文件")
                    
                    processed_files = 0
                    
                    for root, dirs, files in os.walk(self.source_path):
                        if self.canceled:
                            break
                        
                        for file in files:
                            if self.canceled:
                                break
                            
                            full_path = os.path.join(root, file)
                            arcname = os.path.relpath(full_path, start=os.path.dirname(self.source_path))
                            archive.write(full_path, arcname=arcname)
                            processed_files += 1
                            progress = int((processed_files / total_files) * 100)
                            self.progress.emit(progress)
                            self.log_message.emit(f"添加文件: {arcname}")
                
                if self.canceled and os.path.exists(self.target_path):
                    os.remove(self.target_path)
            
            def backup_to_tar(self, mode):
                with tarfile.open(self.target_path, mode) as tar:
                    total_files = 0
                    for root, dirs, files in os.walk(self.source_path):
                        total_files += len(files)
                    
                    if total_files == 0:
                        raise ValueError("没有找到要备份的文件")
                    
                    processed_files = 0
                    
                    for root, dirs, files in os.walk(self.source_path):
                        if self.canceled:
                            break
                        
                        for file in files:
                            if self.canceled:
                                break
                            
                            full_path = os.path.join(root, file)
                            arcname = os.path.relpath(full_path, start=os.path.dirname(self.source_path))
                            tar.add(full_path, arcname=arcname)
                            processed_files += 1
                            progress = int((processed_files / total_files) * 100)
                            self.progress.emit(progress)
                            self.log_message.emit(f"添加文件: {arcname}")
                
                if self.canceled and os.path.exists(self.target_path):
                    os.remove(self.target_path)

        self.progress_bar.show()
        self.log_text.show()
        self.progress_bar.setValue(0)
        self.log_text.clear()
        
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择备份保存目录", ""
        )
        
        if not dir_path:
            self.progress_bar.hide()
            self.log_text.hide()
            return
        
        name, ok = QInputDialog.getText(
            self, "输入备份名称", "请输入备份文件名称 (不含扩展名):",
            text="glibc_backup"
        )
        
        if not ok or not name:
            self.progress_bar.hide()
            self.log_text.hide()
            return
        
        format, ok = QInputDialog.getItem(
            self, "选择压缩格式", "请选择压缩格式:",
            ["7z", "gz", "xz", "tar"], 0, False
        )
        
        if not ok:
            self.progress_bar.hide()
            self.log_text.hide()
            return
        
        if format == '7z':
            ext = '.7z'
        elif format == 'gz':
            ext = '.tar.gz'
        elif format == 'xz':
            ext = '.tar.xz'
        else:
            ext = '.tar'
        
        target_path = os.path.join(dir_path, f"{name}{ext}")
        
        self.backup_thread = BackupThread(self.glibc_path, target_path, format)
        self.backup_thread.finished.connect(self.on_backup_finished)
        self.backup_thread.progress.connect(self.progress_bar.setValue)
        self.backup_thread.log_message.connect(self.log_text.append)
        self.backup_thread.start()
    
    def on_backup_finished(self, success, message):
        self.progress_bar.hide()
        
        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.critical(self, "错误", message)
    
    def restore_glibc(self):
        class RestoreThread(QThread):
            finished = pyqtSignal(bool, str)
            progress = pyqtSignal(int)
            log_message = pyqtSignal(str)
            
            def __init__(self, source_path, target_path):
                super().__init__()
                self.source_path = source_path
                self.target_path = target_path
                self.canceled = False
            
            def run(self):
                try:
                    self.log_message.emit(f"开始恢复: {self.source_path}")
                    
                    if self.source_path.endswith('.7z'):
                        self.extract_7z()
                    elif self.source_path.endswith('.tar.gz') or self.source_path.endswith('.tgz'):
                        self.extract_tar('r:gz')
                    elif self.source_path.endswith('.tar.xz'):
                        self.extract_tar('r:xz')
                    elif self.source_path.endswith('.tar'):
                        self.extract_tar('r:')
                    else:
                        self.finished.emit(False, "不支持的压缩格式，支持7z/tar.gz/tar.xz/tar")
                        return
                    
                    if not self.canceled:
                        self.finished.emit(True, f"成功恢复到: {self.target_path}")
                
                except Exception as e:
                    self.finished.emit(False, f"恢复失败: {str(e)}")
            
            def extract_7z(self):
                with py7zr.SevenZipFile(self.source_path, mode='r') as archive:
                    files = archive.getnames()
                    total_files = len(files)
                    
                    if total_files == 0:
                        raise ValueError("压缩包中没有文件")
                    
                    archive.extractall(path=self.target_path)
                    
                    for i, _ in enumerate(files):
                        if self.canceled:
                            break
                        progress = int((i + 1) / total_files * 100)
                        self.progress.emit(progress)
                        self.log_message.emit(f"解压文件: {files[i]}")
            
            def extract_tar(self, mode):
                with tarfile.open(self.source_path, mode) as tar:
                    members = tar.getmembers()
                    total_members = len(members)
                    
                    for i, member in enumerate(members):
                        if self.canceled:
                            break
                        
                        tar.extract(member, self.target_path)
                        progress = int((i + 1) / total_members * 100)
                        self.progress.emit(progress)
                        self.log_message.emit(f"解压: {member.name}")

        self.progress_bar.show()
        self.log_text.show()
        self.progress_bar.setValue(0)
        self.log_text.clear()
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择备份文件", "", 
            "备份文件 (*.7z *.tar.gz *.tar.xz *.tar)"
        )
        
        if not file_path:
            self.progress_bar.hide()
            self.log_text.hide()
            return
        
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择恢复目标目录", 
            "/data/data/com.termux/files"
        )
        
        if not dir_path:
            self.progress_bar.hide()
            self.log_text.hide()
            return
        
        self.restore_thread = RestoreThread(file_path, dir_path)
        self.restore_thread.finished.connect(self.on_restore_finished)
        self.restore_thread.progress.connect(self.progress_bar.setValue)
        self.restore_thread.log_message.connect(self.log_text.append)
        self.restore_thread.start()
    
    def on_restore_finished(self, success, message):
        self.progress_bar.hide()
        
        if success:
            QMessageBox.information(self, "成功", message)
            self.update_version_info()
        else:
            QMessageBox.critical(self, "错误", message)

    def reset_wine_prefix(self):
        self.clear_interaction_area()
        self.interaction_title.setText("重置Wine环境")
        
        if not os.path.exists(self.wine_path_conf):
            QMessageBox.warning(self, "错误", "找不到Wine路径配置")
            return
        
        wine_prefix = None
        with open(self.wine_path_conf, 'r') as f:
            for line in f:
                if line.startswith("export WINEPREFIX="):
                    wine_prefix = line.split('=')[1].strip().strip('"')
                    break
        
        if not wine_prefix:
            QMessageBox.warning(self, "错误", "无效的Wine前缀路径")
            return
        
        self.interaction_content.hide()
        
        confirm_widget = QWidget()
        confirm_layout = QVBoxLayout(confirm_widget)
        
        info_label = QLabel("确定要重置Wine环境吗？\n这将删除以下目录:")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 16px;")
        confirm_layout.addWidget(info_label)
        
        path_label = QLabel(wine_prefix)
        path_label.setAlignment(Qt.AlignCenter)
        path_label.setStyleSheet("font-size: 14px; color: #666;")
        confirm_layout.addWidget(path_label)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(20)
        
        confirm_btn = QPushButton("确认重置")
        confirm_btn.setFixedSize(100, 35)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background: #FF6347;
                color: white;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #FF4500;
            }
        """)
        confirm_btn.clicked.connect(lambda: self._reset_wine_prefix(wine_prefix))
        button_layout.addWidget(confirm_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #00CED1;
                color: black;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #20B2AA;
            }
        """)
        cancel_btn.clicked.connect(lambda: self.show_sub_menu("advanced"))
        button_layout.addWidget(cancel_btn)
        
        confirm_layout.addWidget(button_widget, alignment=Qt.AlignCenter)
        
        self.interaction_layout.addWidget(confirm_widget)
    
    def _reset_wine_prefix(self, wine_prefix):
        try:
            if os.path.exists(wine_prefix):
                shutil.rmtree(wine_prefix)
                QMessageBox.information(self, "成功", "Wine环境已重置")
            else:
                QMessageBox.information(self, "提示", "Wine环境不存在，无需重置")
            self.show_sub_menu("advanced")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"重置失败: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GLIBCManager()
    window.show()
    sys.exit(app.exec_())