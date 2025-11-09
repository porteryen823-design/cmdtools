# -*- coding: utf-8 -*-
"""
主視窗程式
整合所有功能模組的主要 GUI 介面
"""

import os
import sys
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLineEdit, QPushButton, QLabel,
    QMessageBox, QStatusBar, QProgressBar, QDialog,
    QApplication, QFrame, QSplitter, QSystemTrayIcon, QMenu, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt5.QtGui import QIcon, QFont

from .database import DatabaseManager
from .table_widget import TableTabWidget
from .dialogs import EditRecordDialog, ExportDialog, ConfirmDialog


class MainWindow(QMainWindow):
    """主視窗類"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = None
        self.search_timer = QTimer()  # 初始化搜尋計時器
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._do_global_search)
        self.current_search_text = ""
        
        # 初始化日誌記錄器
        self.init_logger()
        
        # 初始化托盤圖標
        self.init_tray_icon()
        
        self.init_ui()
        self.init_database()
    
    def init_tray_icon(self):
        """初始化托盤圖標"""
        # 創建托盤圖標
        self.tray_icon = QSystemTrayIcon(self)
        
        # 嘗試設置圖標，如果圖標文件不存在則使用默認圖標
        icon_path = os.path.join(os.getcwd(), "cmdtools_icon.ico")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # 使用默認圖標（如果找不到自定義圖標）
            self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        
        # 設置托盤圖標可見
        self.tray_icon.setVisible(True)
        
        # 創建托盤右鍵菜單
        self.create_tray_menu()
        
        # 連接托盤圖標點擊事件（雙擊可還原窗口）
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
    
    def create_tray_menu(self):
        """創建托盤菜單"""
        menu = QMenu()
        
        # 還原視窗動作
        restore_action = menu.addAction("還原視窗")
        restore_action.triggered.connect(self.showNormal)
        
        # 退出動作
        exit_action = menu.addAction("退出")
        exit_action.triggered.connect(self.close)
        
        # 設置托盤圖標的右鍵菜單
        self.tray_icon.setContextMenu(menu)
    
    def on_tray_icon_activated(self, reason):
        """處理托盤圖標點擊事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            # 雙擊托盤圖標還原視窗
            self.showNormal()
            self.activateWindow()
    
    def changeEvent(self, event):
        """處理窗口狀態變化"""
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() == Qt.WindowMinimized:
                # 窗口最小化時隱藏到托盤
                self.hide()
        super().changeEvent(event)
    
    def init_logger(self):
        """初始化日誌記錄器"""
        # 創建日誌目錄（如果不存在）
        log_dir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 設置日誌文件名（使用當前日期）
        log_file = os.path.join(log_dir, f"app_log_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 配置日誌記錄器
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # 同時輸出到控制台
            ]
        )
        
        # 創建自定義的日誌記錄器
        self.logger = logging.getLogger('CmdTools')
    
    def log_operation(self, operation, table_type, seq_no=None, data=None):
        """記錄操作日誌"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {operation} {table_type}"
        
        if seq_no is not None:
            log_message += f" (SeqNo: {seq_no})"
        
        if data:
            # 對於敏感數據（如密碼），不記錄實際值
            safe_data = {k: v if k.lower() != 'password' and k.lower() != 'pwd' else '***'
                         for k, v in data.items()}
            log_message += f" - Data: {safe_data}"
        
        self.logger.info(log_message)
    
    def init_ui(self):
        """初始化使用者介面"""
        self.setWindowTitle("我的工具程式 - 命令工具和提示工具管理系統 --給老人家 & 記憶力衰退使用")
        self.setGeometry(100, 100, 1200, 800)
        
        # 設定字體
        font = QFont("Microsoft JhengHei", 9)
        self.setFont(font)
        
        # 創建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 創建主佈局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 創建工具列區域
        self.create_toolbar(main_layout)
        
        # 創建分頁區域
        self.create_tabs(main_layout)
        
        # 創建狀態列
        self.create_statusbar()
        
        # 設定樣式
        self.set_stylesheet()
    
    def create_toolbar(self, layout):
        """創建工具列"""
        # 全域搜尋區域
        search_frame = QFrame()
        search_frame.setFrameStyle(QFrame.Box)
        search_frame.setStyleSheet("QFrame { background-color: #f0f0f0; padding: 5px; }")
        
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 5, 10, 5)
        
        # 全域搜尋標籤
        search_label = QLabel("全域搜尋:")
        search_label.setStyleSheet("font-weight: bold; color: #2E8B57;")
        search_layout.addWidget(search_label)
        
        # 全域搜尋輸入框
        self.global_search_input = QLineEdit()
        self.global_search_input.setPlaceholderText("在所有欄位中搜尋...")
        self.global_search_input.setMinimumWidth(200)
        self.global_search_input.textChanged.connect(self.on_global_search_changed)
        search_layout.addWidget(self.global_search_input)
        
        # 全域搜尋按鈕
        self.global_search_btn = QPushButton("搜尋")
        self.global_search_btn.clicked.connect(self.on_global_search_clicked)
        search_layout.addWidget(self.global_search_btn)
        
        # 全域清除按鈕
        self.global_clear_btn = QPushButton("清除")
        self.global_clear_btn.clicked.connect(self.on_global_clear_clicked)
        search_layout.addWidget(self.global_clear_btn)
        
        search_layout.addStretch()
        
        layout.addWidget(search_frame)
    
    def create_tabs(self, layout):
        """創建分頁區域"""
        # 創建分頁控制
        self.tab_widget = QTabWidget()
        
        # 創建命令工具分頁
        self.cmd_tab = TableTabWidget(table_type="cmd")
        self.cmd_tab.set_data_callback(self.on_data_operation)
        self.tab_widget.addTab(self.cmd_tab, "命令工具")
        
        # 創建提示工具分頁
        self.prompt_tab = TableTabWidget(table_type="prompt")
        self.prompt_tab.set_data_callback(self.on_data_operation)
        self.tab_widget.addTab(self.prompt_tab, "提示工具")
        
        # 創建 Windows 程式分頁
        self.win_program_tab = TableTabWidget(table_type="winprogram")
        self.win_program_tab.set_data_callback(self.on_data_operation)
        self.tab_widget.addTab(self.win_program_tab, "Windows 程式")
        
        # 創建網站分頁
        self.web_site_tab = TableTabWidget(table_type="website")
        self.web_site_tab.set_data_callback(self.on_data_operation)
        self.tab_widget.addTab(self.web_site_tab, "網站管理")
        
        # 連接分頁切換事件
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        layout.addWidget(self.tab_widget)
        
        # 創建操作按鈕區域
        self.create_action_buttons(layout)
    
    def create_action_buttons(self, layout):
        """創建操作按鈕區域"""
        button_frame = QFrame()
        button_frame.setFrameStyle(QFrame.Box)
        button_frame.setStyleSheet("QFrame { background-color: #f8f8f8; padding: 10px; }")
        
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(10, 5, 10, 5)
        
        # 新增按鈕
        self.add_btn = QPushButton("新增")
        self.add_btn.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; padding: 8px 16px; 
                         border: none; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
        """)
        self.add_btn.clicked.connect(self.on_add_record)
        button_layout.addWidget(self.add_btn)
        
        # 編輯按鈕
        self.edit_btn = QPushButton("編輯")
        self.edit_btn.setStyleSheet("""
            QPushButton { background-color: #2196F3; color: white; padding: 8px 16px; 
                         border: none; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:pressed { background-color: #0d47a1; }
        """)
        self.edit_btn.clicked.connect(self.on_edit_record)
        button_layout.addWidget(self.edit_btn)
        
        # 刪除按鈕
        self.delete_btn = QPushButton("刪除")
        self.delete_btn.setStyleSheet("""
            QPushButton { background-color: #f44336; color: white; padding: 8px 16px; 
                         border: none; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #d32f2f; }
            QPushButton:pressed { background-color: #b71c1c; }
        """)
        self.delete_btn.clicked.connect(self.on_delete_record)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addSpacing(20)
        
        # 匯出按鈕
        self.export_btn = QPushButton("匯出")
        self.export_btn.setStyleSheet("""
            QPushButton { background-color: #FF9800; color: white; padding: 8px 16px; 
                         border: none; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #F57C00; }
            QPushButton:pressed { background-color: #E65100; }
        """)
        self.export_btn.clicked.connect(self.on_export_data)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addSpacing(20)
        
        # 刷新按鈕
        self.refresh_btn = QPushButton("刷新資料")
        self.refresh_btn.setStyleSheet("""
            QPushButton { background-color: #9C27B0; color: white; padding: 8px 16px; 
                         border: none; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #7B1FA2; }
            QPushButton:pressed { background-color: #4A148C; }
        """)
        self.refresh_btn.clicked.connect(self.on_refresh_data)
        button_layout.addWidget(self.refresh_btn)
        
        # 更新資料庫按鈕
        self.update_db_btn = QPushButton("更新資料庫")
        self.update_db_btn.setStyleSheet("""
            QPushButton { background-color: #607D8B; color: white; padding: 8px 16px;
                         border: none; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #455A64; }
            QPushButton:pressed { background-color: #263238; }
        """)
        self.update_db_btn.clicked.connect(self.on_update_database)
        button_layout.addWidget(self.update_db_btn)
        
        button_layout.addSpacing(20)
        
        # 匯出整個資料庫按鈕
        self.export_all_btn = QPushButton("匯出整個資料庫")
        self.export_all_btn.setStyleSheet("""
            QPushButton { background-color: #9C27B0; color: white; padding: 8px 16px;
                         border: none; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #7B1FA2; }
            QPushButton:pressed { background-color: #4A148C; }
        """)
        self.export_all_btn.clicked.connect(self.on_export_all_database)
        button_layout.addWidget(self.export_all_btn)
        
        # 從JSON檔匯入按鈕
        self.import_btn = QPushButton("從JSON檔匯入")
        self.import_btn.setStyleSheet("""
            QPushButton { background-color: #E91E63; color: white; padding: 8px 16px;
                         border: none; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #C2185B; }
            QPushButton:pressed { background-color: #880E4F; }
        """)
        self.import_btn.clicked.connect(self.on_import_database)
        button_layout.addWidget(self.import_btn)
        
        button_layout.addStretch()
        
        layout.addWidget(button_frame)
    
    def create_statusbar(self):
        """創建狀態列"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 連線狀態標籤
        self.connection_label = QLabel("連線狀態: 準備中...")
        self.status_bar.addWidget(self.connection_label)
        
        # 資料統計標籤
        self.data_label = QLabel("資料載入中...")
        self.status_bar.addWidget(self.data_label)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def set_stylesheet(self):
        """設定樣式表"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e1e1e1;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin: 5px 0px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2E8B57;
            }
        """)
    
    def init_database(self):
        """初始化資料庫連線"""
        try:
            self.update_status("正在連線資料庫...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 不確定進度
            
            # 延遲執行連線，讓 UI 先顯示
            QTimer.singleShot(100, self.connect_database)
            
        except Exception as e:
            self.show_error_message(f"初始化資料庫失敗: {e}")
    
    def connect_database(self):
        """連線資料庫"""
        try:
            self.db_manager = DatabaseManager()
            
            if self.db_manager.connect():
                self.update_connection_status("已連線", True)
                self.load_all_data()
            else:
                self.update_connection_status("連線失敗", False)
                self.show_error_message("無法連線到資料庫，請檢查連線設定")
                
        except Exception as e:
            self.update_connection_status("連線錯誤", False)
            self.show_error_message(f"資料庫連線錯誤: {e}")
        finally:
            self.progress_bar.setVisible(False)
    
    def load_all_data(self):
        """載入所有資料"""
        if not self.db_manager:
            return
        
        try:
            self.update_status("正在載入資料...")
            
            # 載入資料
            success, message = self.db_manager.load_all_data()
            
            if success:
                # 設定資料到表格
                self.cmd_tab.set_data(self.db_manager.cmd_tools_data)
                self.prompt_tab.set_data(self.db_manager.prompt_tools_data)
                self.win_program_tab.set_data(self.db_manager.win_program_data)
                self.web_site_tab.set_data(self.db_manager.web_site_data)
                
                self.update_status("資料載入完成")
                self.update_data_status()
                
                QMessageBox.information(self, "載入成功", message)
            else:
                self.show_error_message(message)
                
        except Exception as e:
            self.show_error_message(f"載入資料時發生錯誤: {e}")
    
    def on_global_search_changed(self, text):
        """全域搜尋文字變化"""
        self.current_search_text = text
        # 延遲搜尋，避免頻繁查詢
        self.search_timer.stop()
        self.search_timer.start(500)  # 500ms 延遲
    
    def _do_global_search(self):
        """執行全域搜尋（由計時器觸發）"""
        self.apply_global_search(self.current_search_text)
    
    def apply_global_search(self, keyword):
        """套用全域搜尋"""
        if self.cmd_tab:
            self.cmd_tab.apply_global_filter(keyword)
        if self.prompt_tab:
            self.prompt_tab.apply_global_filter(keyword)
        if self.win_program_tab:
            self.win_program_tab.apply_global_filter(keyword)
        if self.web_site_tab:
            self.web_site_tab.apply_global_filter(keyword)
        
        self.update_data_status()
    
    def on_global_search_clicked(self):
        """全域搜尋按鈕點擊"""
        keyword = self.global_search_input.text()
        self.apply_global_search(keyword)
    
    def on_global_clear_clicked(self):
        """全域清除按鈕點擊"""
        self.global_search_input.clear()
        self.apply_global_search("")
        
        # 清除各分頁的篩選
        if self.cmd_tab:
            self.cmd_tab.clear_all_filters()
        if self.prompt_tab:
            self.prompt_tab.clear_all_filters()
        if self.win_program_tab:
            self.win_program_tab.clear_all_filters()
        if self.web_site_tab:
            self.web_site_tab.clear_all_filters()
    
    def on_tab_changed(self, index):
        """分頁切換事件"""
        self.update_data_status()
    
    def on_data_operation(self, operation, table_type, record=None):
        """處理資料操作"""
        if operation == 'edit':
            if record and record.get('iSeqNo'):
                self.open_edit_dialog(table_type, record)
    
    def on_add_record(self):
        """新增記錄"""
        current_tab = self.get_current_tab_type()
        if not current_tab:
            return
        
        dialog = EditRecordDialog(parent=self, table_type=current_tab, is_edit=False)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            # 記錄日誌
            self.log_operation("新增", current_tab, data=data)
            self.execute_add_record(current_tab, data)
    
    def on_edit_record(self):
        """編輯記錄"""
        current_tab = self.get_current_tab_type()
        if not current_tab:
            return
        
        record = self.get_current_tab_record()
        if not record:
            QMessageBox.warning(self, "警告", "請先選擇要編輯的記錄")
            return
        
        # 記錄日誌
        self.log_operation("編輯", current_tab, seq_no=record.get('iSeqNo'))
        self.open_edit_dialog(current_tab, record)
    
    def open_edit_dialog(self, table_type, record):
        """開啟編輯對話框"""
        dialog = EditRecordDialog(
            parent=self, 
            table_type=table_type, 
            record=record, 
            is_edit=True
        )
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self.execute_update_record(table_type, record.get('iSeqNo'), data)
    
    def on_delete_record(self):
        """刪除記錄"""
        current_tab = self.get_current_tab_type()
        if not current_tab:
            return
        
        record = self.get_current_tab_record()
        if not record:
            QMessageBox.warning(self, "警告", "請先選擇要刪除的記錄")
            return
        
        # 記錄日誌
        self.log_operation("刪除", current_tab, seq_no=record.get('iSeqNo'), data=record)
        
        # 確認刪除
        confirm_dialog = ConfirmDialog(
            self,
            "確認刪除",
            f"確定要刪除序號 {record.get('iSeqNo')} 的記錄嗎？"
        )
        
        if confirm_dialog.exec_() == QDialog.Accepted:
            self.execute_delete_record(current_tab, record.get('iSeqNo'))
    
    def on_export_data(self):
        """匯出資料"""
        current_tab = self.get_current_tab_type()
        if not current_tab:
            return
        
        dialog = ExportDialog(parent=self, table_type=current_tab)
        if dialog.exec_() == QDialog.Accepted:
            settings = dialog.get_export_settings()
            self.execute_export(current_tab, settings)
    
    def on_refresh_data(self):
        """刷新資料"""
        if self.db_manager:
            self.load_all_data()
    
    def on_update_database(self):
        """更新資料庫"""
        if self.db_manager:
            self.load_all_data()
    
    def on_export_all_database(self):
        """匯出整個資料庫"""
        if not self.db_manager:
            return
        
        # 從匯出對話框獲取文件路徑
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "匯出整個資料庫",
            f"cmdtools_database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON 檔案 (*.json);;所有檔案 (*)"
        )
        
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
            self.execute_export_all_database(file_path)
    
    def on_import_database(self):
        """從JSON檔匯入資料庫"""
        if not self.db_manager:
            return
        
        # 打開檔案選擇對話框
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇要匯入的JSON檔案",
            "",
            "JSON 檔案 (*.json);;所有檔案 (*)"
        )
        
        if file_path:
            self.execute_import_database(file_path)
    
    def execute_export_all_database(self, file_path):
        """執行匯出整個資料庫"""
        try:
            self.update_status("正在匯出整個資料庫...")
            
            # 記錄日誌
            self.log_operation("匯出整個資料庫", "all", data={'file_path': file_path})
            
            # 執行匯出
            success, message = self.db_manager.export_all_database(file_path)
            
            if success:
                QMessageBox.information(
                    self,
                    "匯出成功",
                    f"整個資料庫已成功匯出至:\n{file_path}"
                )
                self.update_status("資料庫匯出完成")
            else:
                self.show_error_message(message)
                
        except Exception as e:
            self.show_error_message(f"匯出整個資料庫時發生錯誤: {e}")
    
    def execute_import_database(self, file_path):
        """執行從JSON檔匯入資料庫"""
        try:
            self.update_status("正在匯入資料庫...")
            
            # 記錄日誌
            self.log_operation("從JSON檔匯入資料庫", "all", data={'file_path': file_path})
            
            # 執行匯入
            success, message = self.db_manager.import_from_json_file(file_path)
            
            if success:
                QMessageBox.information(
                    self,
                    "匯入成功",
                    message
                )
                # 重新載入資料
                self.load_all_data()
                self.update_status("資料庫匯入完成")
            else:
                self.show_error_message(message)
                
        except Exception as e:
            self.show_error_message(f"匯入資料庫時發生錯誤: {e}")
    
    def execute_add_record(self, table_type, data):
        """執行新增記錄"""
        if not self.db_manager:
            return
        
        try:
            if table_type == 'cmd':
                success, message = self.db_manager.add_cmd_tool(data)
            elif table_type == 'prompt':
                success, message = self.db_manager.add_prompt_tool(data)
            elif table_type == 'winprogram':
                success, message = self.db_manager.add_win_program(data)
            elif table_type == 'website':
                success, message = self.db_manager.add_web_site(data)
            else:
                success, message = False, f"不支援的表格類型: {table_type}"
            
            if success:
                self.update_tab_data(table_type)
                QMessageBox.information(self, "成功", message)
            else:
                self.show_error_message(message)
                
        except Exception as e:
            self.show_error_message(f"新增記錄時發生錯誤: {e}")
    
    def execute_update_record(self, table_type, seq_no, data):
        """執行更新記錄"""
        if not self.db_manager:
            return
        
        try:
            if table_type == 'cmd':
                success, message = self.db_manager.update_cmd_tool(seq_no, data)
            elif table_type == 'prompt':
                success, message = self.db_manager.update_prompt_tool(seq_no, data)
            elif table_type == 'winprogram':
                success, message = self.db_manager.update_win_program(seq_no, data)
            elif table_type == 'website':
                success, message = self.db_manager.update_web_site(seq_no, data)
            else:
                success, message = False, f"不支援的表格類型: {table_type}"
            
            if success:
                self.update_tab_data(table_type)
                QMessageBox.information(self, "成功", message)
            else:
                self.show_error_message(message)
                
        except Exception as e:
            self.show_error_message(f"更新記錄時發生錯誤: {e}")
    
    def execute_delete_record(self, table_type, seq_no):
        """執行刪除記錄"""
        if not self.db_manager:
            return
        
        try:
            if table_type == 'cmd':
                success, message = self.db_manager.delete_cmd_tool(seq_no)
            elif table_type == 'prompt':
                success, message = self.db_manager.delete_prompt_tool(seq_no)
            elif table_type == 'winprogram':
                success, message = self.db_manager.delete_win_program(seq_no)
            elif table_type == 'website':
                success, message = self.db_manager.delete_web_site(seq_no)
            else:
                success, message = False, f"不支援的表格類型: {table_type}"
            
            if success:
                self.update_tab_data(table_type)
                QMessageBox.information(self, "成功", message)
            else:
                self.show_error_message(message)
                
        except Exception as e:
            self.show_error_message(f"刪除記錄時發生錯誤: {e}")
    
    def execute_export(self, table_type, settings):
        """執行匯出"""
        try:
            if table_type == 'cmd':
                data = self.db_manager.cmd_tools_data
                total_count = len(data)
                filtered_count = self.cmd_tab.get_record_count_info()['current']
                # 獲取篩選後資料
                if settings['export_filtered']:
                    data = self.cmd_tab.table_widget.filtered_data
            elif table_type == 'prompt':
                data = self.db_manager.prompt_tools_data
                total_count = len(data)
                filtered_count = self.prompt_tab.get_record_count_info()['current']
                # 獲取篩選後資料
                if settings['export_filtered']:
                    data = self.prompt_tab.table_widget.filtered_data
            elif table_type == 'winprogram':
                data = self.db_manager.win_program_data
                total_count = len(data)
                filtered_count = self.win_program_tab.get_record_count_info()['current']
                if settings['export_filtered']:
                    data = self.win_program_tab.table_widget.filtered_data
            elif table_type == 'website':
                data = self.db_manager.web_site_data
                total_count = len(data)
                filtered_count = self.web_site_tab.get_record_count_info()['current']
                if settings['export_filtered']:
                    data = self.web_site_tab.table_widget.filtered_data
            else:
                data = []
                total_count = 0
                filtered_count = 0
            
            # 產生 JSON
            json_data = self.db_manager.export_to_json(
                data,
                table_type.capitalize(),
                total_count,
                filtered_count
            )
            
            # 儲存檔案
            with open(settings['file_path'], 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            QMessageBox.information(
                self,
                "匯出成功",
                f"資料已成功匯出至:\n{settings['file_path']}"
            )
            
        except Exception as e:
            self.show_error_message(f"匯出資料時發生錯誤: {e}")
    
    def update_tab_data(self, table_type):
        """更新分頁資料"""
        if table_type == 'cmd':
            self.cmd_tab.set_data(self.db_manager.cmd_tools_data)
        elif table_type == 'prompt':
            self.prompt_tab.set_data(self.db_manager.prompt_tools_data)
        elif table_type == 'winprogram':
            self.win_program_tab.set_data(self.db_manager.win_program_data)
        elif table_type == 'website':
            self.web_site_tab.set_data(self.db_manager.web_site_data)
        
        self.update_data_status()
    
    def get_current_tab_type(self):
        """取得目前分頁類型"""
        current_index = self.tab_widget.currentIndex()
        if current_index == 0:
            return 'cmd'
        elif current_index == 1:
            return 'prompt'
        elif current_index == 2:
            return 'winprogram'
        elif current_index == 3:
            return 'website'
        return None
    
    def get_current_tab_record(self):
        """取得目前分頁選中的記錄"""
        current_tab = self.get_current_tab_type()
        if current_tab == 'cmd':
            return self.cmd_tab.get_current_record()
        elif current_tab == 'prompt':
            return self.prompt_tab.get_current_record()
        elif current_tab == 'winprogram':
            return self.win_program_tab.get_current_record()
        elif current_tab == 'website':
            return self.web_site_tab.get_current_record()
        return {}
    
    def update_connection_status(self, message, connected):
        """更新連線狀態"""
        if connected:
            self.connection_label.setText(f"連線狀態: {message}")
            self.connection_label.setStyleSheet("color: green;")
        else:
            self.connection_label.setText(f"連線狀態: {message}")
            self.connection_label.setStyleSheet("color: red;")
    
    def update_data_status(self):
        """更新資料統計"""
        cmd_info = self.cmd_tab.get_record_count_info() if self.cmd_tab else {'current': 0, 'total': 0}
        prompt_info = self.prompt_tab.get_record_count_info() if self.prompt_tab else {'current': 0, 'total': 0}
        win_program_info = self.win_program_tab.get_record_count_info() if self.win_program_tab else {'current': 0, 'total': 0}
        web_site_info = self.web_site_tab.get_record_count_info() if self.web_site_tab else {'current': 0, 'total': 0}
        
        self.data_label.setText(
            f"命令工具: {cmd_info['current']}/{cmd_info['total']} | "
            f"提示工具: {prompt_info['current']}/{prompt_info['total']} | "
            f"Windows 程式: {win_program_info['current']}/{win_program_info['total']} | "
            f"網站管理: {web_site_info['current']}/{web_site_info['total']}"
        )
    
    def update_status(self, message):
        """更新狀態列訊息"""
        self.status_bar.showMessage(message, 3000)
    
    def show_error_message(self, message):
        """顯示錯誤訊息"""
        QMessageBox.critical(self, "錯誤", message)
        self.update_status(f"錯誤: {message}")


def main():
    """主程式入口"""
    app = QApplication(sys.argv)
    app.setApplicationName("我的工具程式")
    app.setApplicationVersion("1.0.1")
    
    # 設定應用程式圖示（如果有的話）
    # app.setWindowIcon(QIcon("icon.png"))
    
    # 創建主視窗
    window = MainWindow()
    window.show()
    
    # 啟動應用程式
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()