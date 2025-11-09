# -*- coding: utf-8 -*-
"""
表格顯示和篩選模組
負責資料表格的顯示、篩選和基本操作
"""

from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QWidget,
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QGroupBox, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Dict, Callable
import subprocess
import os
import platform
import json
import urllib.parse
import time
import webbrowser


class FilterWidget(QWidget):
    """簡化後的單一搜尋框篩選控制項組件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_input = None
        self.search_callback = None  # 搜尋回調函數
        
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 搜尋標籤
        search_label = QLabel("搜尋:")
        search_label.setStyleSheet("font-weight: bold; color: #2E8B57;")
        layout.addWidget(search_label)
        
        # 搜尋輸入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("在所有欄位中搜尋...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self.search_input)
        
        # 清除按鈕
        clear_button = QPushButton("清除")
        clear_button.clicked.connect(self.on_clear_clicked)
        layout.addWidget(clear_button)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def on_search_text_changed(self, text):
        """搜尋文字變化時觸發（即時搜尋）"""
        if self.search_callback:
            self.search_callback(text)
    
    def on_clear_clicked(self):
        """點擊清除按鈕"""
        self.search_input.clear()
        if self.search_callback:
            self.search_callback("")
    
    def get_search_text(self) -> str:
        """取得搜尋文字"""
        return self.search_input.text() if self.search_input else ""
    
    def set_search_text(self, text: str):
        """設定搜尋文字"""
        if self.search_input:
            self.search_input.setText(text)
    
    def set_search_callback(self, callback: Callable):
        """設定搜尋回調函數"""
        self.search_callback = callback


class DataTableWidget(QTableWidget):
    """資料表格組件"""
    
    # 定義信號
    item_double_clicked = pyqtSignal(int, str)  # 雙擊事件: (行號, 表格類型)
    selection_changed = pyqtSignal()  # 選擇變化事件
    
    def __init__(self, parent=None, table_type="cmd"):
        """
        初始化資料表格
        
        Args:
            parent: 父視窗
            table_type: 表格類型 ('cmd' 或 'prompt')
        """
        super().__init__(parent)
        self.table_type = table_type
        self.original_data = []  # 原始資料
        self.filtered_data = []  # 篩選後資料
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """初始化 UI"""
        # 設置表格基本屬性
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        
        # 設置表頭
        if self.table_type == 'cmd':
            self.setColumnCount(5)
            headers = ["序號", "命令", "範例", "備註1", "類型"]
        elif self.table_type == 'prompt':
            self.setColumnCount(4)
            headers = ["序號", "提示", "提示英文", "分類"]
        elif self.table_type == 'winprogram':
            self.setColumnCount(4)
            headers = ["序號", "備註1", "程式路徑", "點擊結束執行"]
        elif self.table_type == 'website':
            self.setColumnCount(8)
            headers = ["序號", "備註", "分類", "網站", "帳號", "帳號ID", "密碼", "密碼ID"]
        else:
            self.setColumnCount(1)
            headers = ["序號"]
        
        self.setHorizontalHeaderLabels(headers)
        
        # 設置表頭樣式
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        
        # 自動調整欄寬
        self.resizeColumnsToContents()
        
        # 設置最小高度
        self.setMinimumHeight(300)
    
    def setup_connections(self):
        """設置信號連接"""
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.itemSelectionChanged.connect(self.on_selection_changed)
    
    def on_item_double_clicked(self, item):
        """處理雙擊事件"""
        row = item.row()
        self.item_double_clicked.emit(row, self.table_type)
    
    def on_selection_changed(self):
        """處理選擇變化事件"""
        self.selection_changed.emit()
    
    def set_data(self, data: List[Dict]):
        """
        設定表格資料
        
        Args:
            data: 資料清單
        """
        self.original_data = data.copy()
        self.filtered_data = data.copy()
        self.update_table()
    
    def update_table(self):
        """更新表格顯示"""
        self.setRowCount(len(self.filtered_data))
        
        for row, record in enumerate(self.filtered_data):
            if self.table_type == 'cmd':
                # CmdTools 表格（已移除 remark2 欄位）
                self.setItem(row, 0, QTableWidgetItem(str(record.get('iSeqNo', ''))))
                self.setItem(row, 1, QTableWidgetItem(str(record.get('cmd', ''))))
                self.setItem(row, 2, QTableWidgetItem(str(record.get('example', ''))))
                self.setItem(row, 3, QTableWidgetItem(str(record.get('remark1', ''))))
                self.setItem(row, 4, QTableWidgetItem(str(record.get('Classification', ''))))
            elif self.table_type == 'prompt':
                # PromptTools 表格
                self.setItem(row, 0, QTableWidgetItem(str(record.get('iSeqNo', ''))))
                self.setItem(row, 1, QTableWidgetItem(str(record.get('Prompt', ''))))
                self.setItem(row, 2, QTableWidgetItem(str(record.get('Prompt_Eng', ''))))
                self.setItem(row, 3, QTableWidgetItem(str(record.get('Classification', ''))))
            elif self.table_type == 'winprogram':
                # WinProgram 表格
                self.setItem(row, 0, QTableWidgetItem(str(record.get('iSeqNo', ''))))
                self.setItem(row, 1, QTableWidgetItem(str(record.get('remark1', ''))))
                self.setItem(row, 2, QTableWidgetItem(str(record.get('ProgramPathAndName', ''))))
                self.setItem(row, 3, QTableWidgetItem(str(record.get('ClickEndRun', ''))))
            elif self.table_type == 'website':
                # WebSite 表格
                self.setItem(row, 0, QTableWidgetItem(str(record.get('iSeqNo', ''))))
                self.setItem(row, 1, QTableWidgetItem(str(record.get('Remark', ''))))
                self.setItem(row, 2, QTableWidgetItem(str(record.get('Classification', ''))))
                self.setItem(row, 3, QTableWidgetItem(str(record.get('Website', ''))))
                self.setItem(row, 4, QTableWidgetItem(str(record.get('account', ''))))
                self.setItem(row, 5, QTableWidgetItem(str(record.get('account_webid', ''))))
                self.setItem(row, 6, QTableWidgetItem(str(record.get('password', ''))))
                self.setItem(row, 7, QTableWidgetItem(str(record.get('password_webid', ''))))
        
        # 更新表格標題
        self.update_table_title()
        
        # 自動調整欄寬
        self.resizeColumnsToContents()
    
    def update_table_title(self):
        """更新表格標題"""
        pass  # 標題更新由父視窗處理
    
    def apply_filters(self, filters: Dict[str, str]):
        """
        套用篩選條件
        
        Args:
            filters: 篩選條件字典
        """
        self.filtered_data = self.original_data.copy()
        
        for field, keyword in filters.items():
            if keyword.strip():  # 非空關鍵字
                keyword_lower = keyword.lower()
                self.filtered_data = [
                    record for record in self.filtered_data
                    if keyword_lower in str(record.get(field, "")).lower()
                ]
        
        self.update_table()
    
    def apply_global_filter(self, keyword: str, table_type: str = None):
        """
        套用全域搜尋
        
        Args:
            keyword: 搜尋關鍵字
            table_type: 表格類型（用於判斷搜尋範圍）
        """
        if not keyword.strip():
            # 關鍵字為空時顯示所有資料
            self.filtered_data = self.original_data.copy()
        else:
            keyword_lower = keyword.lower()
            
            if self.table_type == 'cmd':
                # CmdTools 全域搜尋：搜尋所有欄位（已移除 remark2）
                searchable_fields = ['cmd', 'example', 'remark1', 'Classification']
            elif self.table_type == 'prompt':
                # PromptTools 全域搜尋：搜尋所有欄位
                searchable_fields = ['Prompt', 'Prompt_Eng', 'Classification']
            elif self.table_type == 'winprogram':
                # WinProgram 全域搜尋：搜尋所有欄位
                searchable_fields = ['remark1', 'ProgramPathAndName', 'ClickEndRun']
            elif self.table_type == 'website':
                # WebSite 全域搜尋：搜尋所有欄位
                searchable_fields = ['Remark', 'Classification', 'Website', 'account', 'account_webid', 'password', 'password_webid']
            else:
                searchable_fields = []
            
            self.filtered_data = [
                record for record in self.original_data
                if any(keyword_lower in str(record.get(field, "")).lower()
                      for field in searchable_fields)
            ]
        
        self.update_table()
    
    def get_current_record(self) -> Dict:
        """取得目前選中的記錄"""
        current_row = self.currentRow()
        if 0 <= current_row < len(self.filtered_data):
            return self.filtered_data[current_row].copy()
        return {}
    
    def get_selected_seq_no(self) -> int:
        """取得選中記錄的序號"""
        record = self.get_current_record()
        return record.get('iSeqNo', 0)
    
    def get_record_count(self) -> int:
        """取得目前顯示記錄數量"""
        return len(self.filtered_data)
    
    def get_total_count(self) -> int:
        """取得總記錄數量"""
        return len(self.original_data)


class TableTabWidget(QWidget):
    """表格分頁組件"""
    
    def __init__(self, parent=None, table_type="cmd"):
        """
        初始化表格分頁組件
        
        Args:
            parent: 父視窗
            table_type: 表格類型 ('cmd' 或 'prompt')
        """
        super().__init__(parent)
        self.table_type = table_type
        self.data_callback = None  # 資料操作回調函數
        self.table_title_label = None
        
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        
        # 表格標題
        self.table_title_label = QLabel()
        self.table_title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2E8B57;")
        layout.addWidget(self.table_title_label)
        
        # 篩選控制項區域（使用簡化後的 FilterWidget）
        filter_group = QGroupBox("搜尋篩選")
        filter_layout = QVBoxLayout()
        
        # 使用簡化的 FilterWidget，無需傳入 fields
        self.filter_widget = FilterWidget()
        filter_layout.addWidget(self.filter_widget)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # 表格區域
        self.table_widget = DataTableWidget(table_type=self.table_type)
        layout.addWidget(self.table_widget)
        
        # 根據表格類型添加相應的按鈕
        if self.table_type == 'winprogram':
            self.create_execute_button(layout)
        elif self.table_type == 'website':
            self.create_open_website_button(layout)
        
        # 新增匯出/匯入按鈕
        self.create_export_import_buttons(layout)
        
        self.setLayout(layout)
        
        # 更新標題
        self.update_table_title()
        
        # 設置搜尋回調
        self.filter_widget.set_search_callback(self.on_field_search)
    
    def create_execute_button(self, layout):
        """創建執行按鈕（僅限 Windows 程式分頁）"""
        button_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton("執行選中程式")
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800; color: white; padding: 8px 16px;
                border: none; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #F57C00; }
            QPushButton:pressed { background-color: #E65100; }
            QPushButton:disabled {
                background-color: #cccccc; color: #666666;
            }
        """)
        self.execute_btn.clicked.connect(self.on_execute_program)
        self.execute_btn.setEnabled(False)  # 預設禁用，等待選擇記錄
        
        self.program_status_label = QLabel("請先選擇一個程式")
        self.program_status_label.setStyleSheet("color: #666666; font-style: italic;")
        
        button_layout.addWidget(self.execute_btn)
        button_layout.addWidget(self.program_status_label)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 連接表格選擇變化事件
        self.table_widget.selection_changed.connect(self.on_selection_changed)
    
    def on_selection_changed(self):
        """處理選擇變化事件（僅限 Windows 程式分頁）"""
        if self.table_type != 'winprogram':
            return
            
        record = self.get_current_record()
        if record:
            program_path = record.get('ProgramPathAndName', '').strip()
            click_end_run = record.get('ClickEndRun', 0)
            
            if program_path and click_end_run == 1:
                self.execute_btn.setEnabled(True)
                self.execute_btn.setText(f"執行程式: {os.path.basename(program_path) if program_path else '未知'}")
                self.program_status_label.setText("程式可以執行")
                self.program_status_label.setStyleSheet("color: green; font-style: normal;")
            else:
                self.execute_btn.setEnabled(False)
                self.execute_btn.setText("執行選中程式")
                if not program_path:
                    self.program_status_label.setText("程式路徑為空")
                else:
                    self.program_status_label.setText("此程式設定為不自動執行")
                self.program_status_label.setStyleSheet("color: #666666; font-style: italic;")
        else:
            self.execute_btn.setEnabled(False)
            self.execute_btn.setText("執行選中程式")
            self.program_status_label.setText("請先選擇一個程式")
            self.program_status_label.setStyleSheet("color: #666666; font-style: italic;")
    
    def on_execute_program(self):
        """執行選中的程式"""
        if self.table_type != 'winprogram':
            return
            
        record = self.get_current_record()
        if not record:
            return
            
        program_path = record.get('ProgramPathAndName', '').strip()
        click_end_run = record.get('ClickEndRun', 0)
        
        if not program_path:
            QMessageBox.warning(self, "警告", "程式路徑為空，無法執行")
            return
            
        if click_end_run != 1:
            QMessageBox.warning(self, "警告", "此程式設定為不自動執行")
            return
        
        try:
            # 檢查程式檔案是否存在
            if not os.path.exists(program_path):
                # 嘗試在 PATH 環境變數中尋找
                program_name = os.path.basename(program_path)
                if platform.system() == "Windows":
                    # Windows 系統，嘗試不同的副檔名
                    possible_paths = [
                        program_path,
                        program_path + ".exe",
                        program_path + ".bat",
                        program_path + ".cmd"
                    ]
                    found_path = None
                    for path in possible_paths:
                        if os.path.exists(path):
                            found_path = path
                            break
                    
                    if not found_path:
                        # 嘗試在系統 PATH 中尋找
                        import shutil
                        found_path = shutil.which(program_name)
                        if not found_path:
                            QMessageBox.warning(self, "錯誤", f"找不到程式檔案: {program_path}")
                            return
                    program_path = found_path
                else:
                    # 非 Windows 系統，直接檢查
                    QMessageBox.warning(self, "錯誤", f"找不到程式檔案: {program_path}")
                    return
            
            # 執行程式
            if platform.system() == "Windows":
                # Windows 系統
                subprocess.Popen([program_path], shell=True)
            else:
                # Linux/Mac 系統
                subprocess.Popen([program_path])
            
            # 顯示成功訊息
            program_name = os.path.basename(program_path)
            QMessageBox.information(self, "成功", f"已啟動程式: {program_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"執行程式時發生錯誤: {str(e)}")
    
    def create_open_website_button(self, layout):
        """創建開啟網站按鈕（僅限網站管理分頁）"""
        button_layout = QHBoxLayout()
        
        self.open_website_btn = QPushButton("開啟網站")
        self.open_website_btn.setStyleSheet("""
            QPushButton { 
                background-color: #2196F3; color: white; padding: 8px 16px; 
                border: none; border-radius: 4px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:pressed { background-color: #0d47a1; }
            QPushButton:disabled { 
                background-color: #cccccc; color: #666666; 
            }
        """)
        self.open_website_btn.clicked.connect(self.on_open_website)
        self.open_website_btn.setEnabled(False)  # 預設禁用，等待選擇記錄
        
        self.website_status_label = QLabel("請先選擇一個網站")
        self.website_status_label.setStyleSheet("color: #666666; font-style: italic;")
        
        button_layout.addWidget(self.open_website_btn)
        button_layout.addWidget(self.website_status_label)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 連接表格選擇變化事件
        self.table_widget.selection_changed.connect(self.on_website_selection_changed)
    
    def on_website_selection_changed(self):
        """處理網站選擇變化事件（僅限網站管理分頁）"""
        if self.table_type != 'website':
            return
            
        record = self.get_current_record()
        if record:
            website_url = record.get('Website', '').strip()
            
            if website_url:
                self.open_website_btn.setEnabled(True)
                # 顯示網站域名或簡化的URL
                try:
                    parsed_url = urllib.parse.urlparse(website_url)
                    display_name = parsed_url.netloc or website_url
                    if len(display_name) > 30:
                        display_name = display_name[:30] + "..."
                    self.open_website_btn.setText(f"開啟網站: {display_name}")
                except:
                    self.open_website_btn.setText(f"開啟網站: {website_url[:30]}...")
                
                self.website_status_label.setText("網站可以開啟")
                self.website_status_label.setStyleSheet("color: green; font-style: normal;")
            else:
                self.open_website_btn.setEnabled(False)
                self.open_website_btn.setText("開啟網站")
                self.website_status_label.setText("網站網址為空")
                self.website_status_label.setStyleSheet("color: #666666; font-style: italic;")
        else:
            self.open_website_btn.setEnabled(False)
            self.open_website_btn.setText("開啟網站")
            self.website_status_label.setText("請先選擇一個網站")
            self.website_status_label.setStyleSheet("color: #666666; font-style: italic;")
    
    def on_open_website(self):
        """開啟選中的網站"""
        if self.table_type != 'website':
            return
            
        record = self.get_current_record()
        if not record:
            return
            
        website_url = record.get('Website', '').strip()
        account = record.get('account', '').strip()
        account_webid = record.get('account_webid', '').strip()
        password = record.get('password', '').strip()
        password_webid = record.get('password_webid', '').strip()
        
        if not website_url:
            QMessageBox.warning(self, "警告", "網站網址為空，無法開啟")
            return
        
        try:
            # 確保 URL 有正確的協議
            if not website_url.startswith(('http://', 'https://')):
                # 如果沒有協議，預設使用 https
                website_url = 'https://' + website_url
            
            # 如果有帳號密碼或 webid，使用 web_login.py 進行開啟和登入
            if account or password or account_webid or password_webid:
                # 建構 web_login.py 命令行參數
                try:
                    import sys
                    import os
                    
                    # 使用絕對路徑執行 web_login.exe
                    exe_path = os.path.abspath("web_login_tool/dist/web_login.exe")
                    
                    if not os.path.exists(exe_path):
                        # 如果執行檔不存在，回退到普通瀏覽器開啟
                        QMessageBox.warning(self, "警告", "找不到 web_login.exe 程式，使用普通瀏覽器開啟網站")
                        webbrowser.open(website_url)
                        QMessageBox.information(self, "成功", f"已開啟網站: {website_url}")
                        return
                    
                    # 準備參數 - 使用與測試成功相同的格式
                    args = [
                        "-u", website_url,
                        "-username", account if account else "admin",  # 如果帳號為空則使用預設 admin
                        "-password", password if password else "gsi5613686#"  # 如果密碼為空則使用預設密碼
                    ]
                    
                    # 如果有自定義的 webid，添加到參數中
                    #if account_webid:
                    #    args.extend(["-username_webid", account_webid])
                    #if password_webid:
                    #    args.extend(["-password_webid", password_webid])
                    
                    try:
                        # 使用 subprocess.run 執行並等待完成
                        result = subprocess.run([exe_path] + args, capture_output=True, text=True, timeout=30)
                        
                        if result.returncode == 0:
                            # 檢查輸出是否包含成功訊息
                            if "SUCCESS" in result.stdout or "登入成功" in result.stdout:
                                QMessageBox.information(self, "成功", "已開啟網站並自動登入")
                            else:
                                QMessageBox.information(self, "成功", "已開啟網站並執行登入程序")
                        else:
                            # 如果執行失敗，但網站已開啟
                            if "ERROR" in result.stderr:
                                QMessageBox.information(self, "部分成功", "已開啟網站（執行過程中遇到問題）")
                            else:
                                QMessageBox.information(self, "成功", "已開啟網站")
                            
                    except subprocess.TimeoutExpired:
                        QMessageBox.information(self, "成功", "已開啟網站（登入程序仍在執行中）")
                    
                except FileNotFoundError:
                    # web_login.py 不存在，回退到普通瀏覽器開啟
                    QMessageBox.warning(self, "警告", "找不到 web_login.py 程式，使用普通瀏覽器開啟網站")
                    webbrowser.open(website_url)
                    QMessageBox.information(self, "成功", f"已開啟網站: {website_url}")
                except Exception as e:
                    # 其他錯誤，回退到普通瀏覽器開啟
                    QMessageBox.warning(self, "警告", f"自動登入過程發生錯誤: {str(e)}")
                    webbrowser.open(website_url)
                    QMessageBox.information(self, "成功", f"已開啟網站: {website_url}")
            else:
                # 沒有帳號密碼，直接使用瀏覽器開啟
                webbrowser.open(website_url)
                QMessageBox.information(self, "成功", f"已開啟網站: {website_url}")
            
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"開啟網站時發生錯誤: {str(e)}")

    def update_table_title(self):
        """更新表格標題"""
        if self.table_type == 'cmd':
            title = "命令工具資料表"
        elif self.table_type == 'prompt':
            title = "提示工具資料表"
        elif self.table_type == 'winprogram':
            title = "Windows 程式資料表"
        elif self.table_type == 'website':
            title = "網站管理資料表"
        else:
            title = "未知資料表"
        
        if self.table_title_label:
            self.table_title_label.setText(title)
    
    def on_field_search(self, keyword):
        """
        處理單一搜尋框搜尋
        這個函數現在處理全欄位搜尋，與前端行為一致
        """
        if self.table_widget:
            self.table_widget.apply_global_filter(keyword)
    
    def create_export_import_buttons(self, layout):
        """創建匯出/匯入按鈕"""
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("匯出資料庫")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white; padding: 8px 16px;
                border: none; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
        """)
        export_btn.clicked.connect(self.on_export_database)
        
        import_btn = QPushButton("匯入資料庫")
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; color: white; padding: 8px 16px;
                border: none; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:pressed { background-color: #0d47a1; }
        """)
        import_btn.clicked.connect(self.on_import_database)
        
        button_layout.addWidget(export_btn)
        button_layout.addWidget(import_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def on_export_database(self):
        """匯出整個資料庫到 JSON 檔案"""
        # 取得所有表格資料
        all_data = {
            'cmd': self.table_widget.get_data() if hasattr(self.table_widget, 'get_data') else [],
            'prompt': self.table_widget.get_data() if hasattr(self.table_widget, 'get_data') else [],
            'winprogram': self.table_widget.get_data() if hasattr(self.table_widget, 'get_data') else [],
            'website': self.table_widget.get_data() if hasattr(self.table_widget, 'get_data') else []
        }
        
        # 讓使用者選擇儲存位置
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "匯出資料庫",
            "database_export.json",
            "JSON 檔案 (*.json);;所有檔案 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "匯出成功", f"資料已匯出至 {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "匯出失敗", f"匯出時發生錯誤: {str(e)}")
    
    def on_import_database(self):
        """從 JSON 檔案匯入資料庫"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "匯入資料庫",
            "",
            "JSON 檔案 (*.json);;所有檔案 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 依表格類型插入資料
                for table_type, records in data.items():
                    if isinstance(records, list):
                        for record in records:
                            # 這裡假設有一個插入函式 insert_record(table_type, record)
                            # 需要根據實際實現調整
                            self.insert_record(table_type, record)
                
                QMessageBox.information(self, "匯入成功", f"資料已從 {file_path} 匯入")
            except Exception as e:
                QMessageBox.critical(self, "匯入失敗", f"匯入時發生錯誤: {str(e)}")
    
    def insert_record(self, table_type, record):
        """插入單筆資料到資料庫（示例實作，需根據實際資料庫調整）"""
        # 這裡僅示範，實際應使用資料庫連線執行 INSERT
        # 例如使用 sqlite3 或 mysql.connector
        pass
    
    def set_data_callback(self, callback: Callable):
        """設定資料操作回調函數"""
        self.data_callback = callback
        if self.table_widget:
            self.table_widget.item_double_clicked.connect(
                lambda row, table_type: self.on_record_double_clicked(row)
            )
    
    def on_record_double_clicked(self, row):
        """處理記錄雙擊事件（編輯）"""
        if self.data_callback:
            self.data_callback('edit', self.table_type, self.table_widget.get_current_record())
    
    def set_data(self, data: List[Dict]):
        """設定表格資料"""
        if self.table_widget:
            self.table_widget.set_data(data)
    
    def apply_global_filter(self, keyword: str):
        """套用全域搜尋"""
        if self.table_widget:
            self.table_widget.apply_global_filter(keyword)
    
    def clear_all_filters(self):
        """清除所有篩選（重置為初始狀態）"""
        if self.filter_widget:
            self.filter_widget.set_search_text("")
        if self.table_widget:
            # 清除搜尋時顯示所有資料
            self.table_widget.apply_global_filter("")
            self.table_widget.update_table()
            
            # 記錄日誌（可選）
            # print("已清除搜尋條件，顯示全部資料")
    
    def get_current_record(self) -> Dict:
        """取得目前選中的記錄"""
        if self.table_widget:
            return self.table_widget.get_current_record()
        return {}
    
    def get_selected_seq_no(self) -> int:
        """取得選中記錄的序號"""
        if self.table_widget:
            return self.table_widget.get_selected_seq_no()
        return 0
    
    def get_record_count_info(self) -> Dict[str, int]:
        """取得記錄數量資訊"""
        if self.table_widget:
            return {
                'current': self.table_widget.get_record_count(),
                'total': self.table_widget.get_total_count()
            }
        return {'current': 0, 'total': 0}