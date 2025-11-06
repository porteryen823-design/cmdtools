# -*- coding: utf-8 -*-
"""
表格顯示和篩選模組
負責資料表格的顯示、篩選和基本操作
"""

from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QWidget,
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QLabel, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Dict, Callable


class FilterWidget(QWidget):
    """篩選控制項組件"""
    
    def __init__(self, parent=None, fields=None):
        """
        初始化篩選控制項
        
        Args:
            parent: 父視窗
            fields: 欄位清單，例如 ['cmd', 'example', 'remark1', ...]
        """
        super().__init__(parent)
        self.fields = fields or []
        self.field_inputs = {}
        self.search_callback = None  # 搜尋回調函數
        
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        
        # 為每個欄位創建搜尋控制項
        for field in self.fields:
            field_layout = QHBoxLayout()
            
            # 欄位標籤
            field_label = QLabel(f"{field}:")
            field_label.setFixedWidth(80)
            
            # 搜尋輸入框
            search_input = QLineEdit()
            search_input.setPlaceholderText(f"搜尋 {field}...")
            search_input.textChanged.connect(lambda text, f=field: self.on_search_text_changed(f, text))
            
            # 搜尋按鈕
            search_button = QPushButton("搜尋")
            search_button.clicked.connect(lambda checked, f=field: self.on_search_clicked(f))
            
            # 清除按鈕
            clear_button = QPushButton("清除")
            clear_button.clicked.connect(lambda checked, f=field: self.on_clear_clicked(f))
            
            field_layout.addWidget(field_label)
            field_layout.addWidget(search_input)
            field_layout.addWidget(search_button)
            field_layout.addWidget(clear_button)
            
            self.field_inputs[field] = {
                'input': search_input,
                'search_btn': search_button,
                'clear_btn': clear_button
            }
            
            layout.addLayout(field_layout)
        
        self.setLayout(layout)
    
    def on_search_text_changed(self, field, text):
        """搜尋文字變化時觸發（即時搜尋）"""
        self.on_search_clicked(field)
    
    def on_search_clicked(self, field):
        """點擊搜尋按鈕"""
        search_text = self.field_inputs[field]['input'].text()
        if self.search_callback:
            self.search_callback(field, search_text)
    
    def on_clear_clicked(self, field):
        """點擊清除按鈕"""
        self.field_inputs[field]['input'].clear()
        if self.search_callback:
            self.search_callback(field, "")
    
    def get_all_filters(self) -> Dict[str, str]:
        """取得所有篩選條件"""
        filters = {}
        for field, widgets in self.field_inputs.items():
            filters[field] = widgets['input'].text()
        return filters
    
    def clear_all_filters(self):
        """清除所有篩選條件"""
        for field, widgets in self.field_inputs.items():
            widgets['input'].clear()
    
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
            self.setColumnCount(6)
            headers = ["序號", "命令", "範例", "備註1", "備註2", "類型"]
        else:
            self.setColumnCount(4)
            headers = ["序號", "提示", "提示英文", "分類"]
        
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
                # CmdTools 表格
                self.setItem(row, 0, QTableWidgetItem(str(record.get('iSeqNo', ''))))
                self.setItem(row, 1, QTableWidgetItem(str(record.get('cmd', ''))))
                self.setItem(row, 2, QTableWidgetItem(str(record.get('example', ''))))
                self.setItem(row, 3, QTableWidgetItem(str(record.get('remark1', ''))))
                self.setItem(row, 4, QTableWidgetItem(str(record.get('remark2', ''))))
                self.setItem(row, 5, QTableWidgetItem(str(record.get('Type', ''))))
            else:
                # PromptTools 表格
                self.setItem(row, 0, QTableWidgetItem(str(record.get('iSeqNo', ''))))
                self.setItem(row, 1, QTableWidgetItem(str(record.get('Prompt', ''))))
                self.setItem(row, 2, QTableWidgetItem(str(record.get('Prompt_Eng', ''))))
                self.setItem(row, 3, QTableWidgetItem(str(record.get('Classification', ''))))
        
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
                # CmdTools 全域搜尋：搜尋所有欄位
                searchable_fields = ['cmd', 'example', 'remark1', 'remark2', 'Type']
            else:
                # PromptTools 全域搜尋：搜尋所有欄位
                searchable_fields = ['Prompt', 'Prompt_Eng', 'Classification']
            
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
        
        # 篩選控制項區域
        filter_group = QGroupBox("搜尋篩選")
        filter_layout = QVBoxLayout()
        
        if self.table_type == 'cmd':
            # 命令工具篩選控制項
            cmd_fields = ['cmd', 'example', 'remark1', 'remark2', 'Type']
            self.filter_widget = FilterWidget(fields=cmd_fields)
        else:
            # 提示工具篩選控制項
            prompt_fields = ['Prompt', 'Prompt_Eng', 'Classification']
            self.filter_widget = FilterWidget(fields=prompt_fields)
        
        filter_layout.addWidget(self.filter_widget)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # 表格區域
        self.table_widget = DataTableWidget(table_type=self.table_type)
        layout.addWidget(self.table_widget)
        
        self.setLayout(layout)
        
        # 更新標題
        self.update_table_title()
        
        # 設置搜尋回調
        self.filter_widget.set_search_callback(self.on_field_search)
    
    def update_table_title(self):
        """更新表格標題"""
        if self.table_type == 'cmd':
            title = "命令工具資料表"
        else:
            title = "提示工具資料表"
        
        if self.table_title_label:
            self.table_title_label.setText(title)
    
    def on_field_search(self, field, keyword):
        """
        處理欄位搜尋
        
        Args:
            field: 搜尋欄位
            keyword: 搜尋關鍵字
        """
        if self.table_widget:
            filters = {field: keyword}
            # 清除其他欄位的搜尋
            all_filters = self.filter_widget.get_all_filters()
            for f in all_filters:
                if f != field:
                    all_filters[f] = ""
            
            self.table_widget.apply_filters(all_filters)
    
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
        """清除所有篩選"""
        if self.filter_widget:
            self.filter_widget.clear_all_filters()
        if self.table_widget:
            self.table_widget.apply_filters({})
    
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