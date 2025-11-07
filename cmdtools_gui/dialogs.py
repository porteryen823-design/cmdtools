# -*- coding: utf-8 -*-
"""
資料編輯和匯出對話框模組
包含新增、編輯、匯出等功能對話框
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QGroupBox, QFormLayout,
    QMessageBox, QFileDialog, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt


class EditRecordDialog(QDialog):
    """編輯記錄對話框"""
    
    def __init__(self, parent=None, table_type=None, record=None, is_edit=False):
        """
        初始化編輯對話框
        
        Args:
            parent: 父視窗
            table_type: 表格類型 ('cmd', 'prompt', 'winprogram', 'website')
            record: 現有記錄資料（編輯模式）
            is_edit: 是否為編輯模式
        """
        super().__init__(parent)
        self.table_type = table_type
        self.is_edit = is_edit
        self.record = record
        
        self.init_ui()
        self.setup_data()
    
    def init_ui(self):
        """初始化 UI"""
        # 設定對話框標題
        title_mapping = {
            'cmd': '命令工具',
            'prompt': '提示工具',
            'winprogram': 'Windows 程式',
            'website': '網站管理'
        }
        table_title = title_mapping.get(self.table_type, '未知表格')
        self.setWindowTitle(f"{'編輯' if self.is_edit else '新增'}{table_title}")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # 創建表單
        form_layout = QFormLayout()
        
        if self.table_type == 'cmd':
            # 命令工具表單
            self.cmd_input = QLineEdit()
            self.example_input = QLineEdit()
            self.remark1_input = QLineEdit()
            self.remark2_input = QLineEdit()
            self.type_input = QLineEdit()
            
            form_layout.addRow("命令:", self.cmd_input)
            form_layout.addRow("範例:", self.example_input)
            form_layout.addRow("備註1:", self.remark1_input)
            form_layout.addRow("備註2:", self.remark2_input)
            form_layout.addRow("類型:", self.type_input)
            
        elif self.table_type == 'prompt':
            # 提示工具表單
            self.prompt_input = QTextEdit()
            self.prompt_eng_input = QTextEdit()
            self.classification_input = QLineEdit()
            
            # 設置文本編輯區域高度
            self.prompt_input.setMaximumHeight(80)
            self.prompt_eng_input.setMaximumHeight(80)
            
            form_layout.addRow("提示:", self.prompt_input)
            form_layout.addRow("提示英文:", self.prompt_eng_input)
            form_layout.addRow("分類:", self.classification_input)
            
        elif self.table_type == 'winprogram':
            # Windows 程式表單
            self.remark1_input = QLineEdit()
            self.program_path_and_name_input = QLineEdit()
            self.click_end_run_input = QComboBox()
            self.click_end_run_input.addItems(["是", "否"])
            
            form_layout.addRow("備註1:", self.remark1_input)
            form_layout.addRow("程式路徑與名稱:", self.program_path_and_name_input)
            form_layout.addRow("點擊後執行:", self.click_end_run_input)
            
        elif self.table_type == 'website':
            # 網站管理表單
            self.remark_input = QLineEdit()
            self.classification_input = QLineEdit()
            self.website_input = QLineEdit()
            self.account_input = QLineEdit()
            self.account_webid_input = QLineEdit()
            self.password_input = QLineEdit()
            self.password_webid_input = QLineEdit()
            
            form_layout.addRow("備註:", self.remark_input)
            form_layout.addRow("分類:", self.classification_input)
            form_layout.addRow("網站:", self.website_input)
            form_layout.addRow("帳號:", self.account_input)
            form_layout.addRow("帳號ID:", self.account_webid_input)
            form_layout.addRow("密碼:", self.password_input)
            form_layout.addRow("密碼ID:", self.password_webid_input)
        
        layout.addLayout(form_layout)
        
        # 按鈕區域
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("確定")
        self.cancel_button = QPushButton("取消")
        
        self.ok_button.clicked.connect(self.accept_data)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def setup_data(self):
        """填入現有資料（編輯模式）"""
        if self.is_edit and self.record:
            if self.table_type == 'cmd':
                self.cmd_input.setText(self.record.get('cmd', ''))
                self.example_input.setText(self.record.get('example', ''))
                self.remark1_input.setText(self.record.get('remark1', ''))
                self.remark2_input.setText(self.record.get('remark2', ''))
                self.type_input.setText(self.record.get('Type', ''))
            elif self.table_type == 'prompt':
                self.prompt_input.setText(self.record.get('Prompt', ''))
                self.prompt_eng_input.setText(self.record.get('Prompt_Eng', ''))
                self.classification_input.setText(self.record.get('Classification', ''))
            elif self.table_type == 'winprogram':
                self.remark1_input.setText(self.record.get('remark1', ''))
                self.program_path_and_name_input.setText(self.record.get('ProgramPathAndName', ''))
                click_end_run = self.record.get('ClickEndRun', None)
                if click_end_run is not None:
                    if click_end_run == 1:
                        self.click_end_run_input.setCurrentText("是")
                    else:
                        self.click_end_run_input.setCurrentText("否")
            elif self.table_type == 'website':
                self.remark_input.setText(self.record.get('Remark', ''))
                self.classification_input.setText(self.record.get('Classification', ''))
                self.website_input.setText(self.record.get('Website', ''))
                self.account_input.setText(self.record.get('account', ''))
                self.account_webid_input.setText(self.record.get('account_webid', ''))
                self.password_input.setText(self.record.get('password', ''))
                self.password_webid_input.setText(self.record.get('password_webid', ''))
    
    def accept_data(self):
        """驗證並接受資料"""
        if self.table_type == 'cmd':
            # 驗證命令工具資料
            if not self.cmd_input.text().strip():
                QMessageBox.warning(self, "驗證錯誤", "命令欄位不能為空")
                return
        elif self.table_type == 'prompt':
            # 驗證提示工具資料
            if not self.prompt_input.toPlainText().strip():
                QMessageBox.warning(self, "驗證錯誤", "提示欄位不能為空")
                return
        elif self.table_type == 'winprogram':
            # 驗證 Windows 程式資料
            if not self.program_path_and_name_input.text().strip():
                QMessageBox.warning(self, "驗證錯誤", "程式路徑與名稱欄位不能為空")
                return
        elif self.table_type == 'website':
            # 驗證網站管理資料
            if not self.website_input.text().strip():
                QMessageBox.warning(self, "驗證錯誤", "網站欄位不能為空")
                return
        
        self.accept()
    
    def get_data(self):
        """取得輸入的資料"""
        if self.table_type == 'cmd':
            return {
                'cmd': self.cmd_input.text().strip(),
                'example': self.example_input.text().strip(),
                'remark1': self.remark1_input.text().strip(),
                'remark2': self.remark2_input.text().strip(),
                'Type': self.type_input.text().strip()
            }
        elif self.table_type == 'prompt':
            return {
                'Prompt': self.prompt_input.toPlainText().strip(),
                'Prompt_Eng': self.prompt_eng_input.toPlainText().strip(),
                'Classification': self.classification_input.text().strip()
            }
        elif self.table_type == 'winprogram':
            # 轉換 "是"/"否" 為 1/0
            click_end_run = 1 if self.click_end_run_input.currentText() == "是" else 0
            return {
                'remark1': self.remark1_input.text().strip(),
                'ProgramPathAndName': self.program_path_and_name_input.text().strip(),
                'ClickEndRun': click_end_run
            }
        elif self.table_type == 'website':
            return {
                'Remark': self.remark_input.text().strip(),
                'Classification': self.classification_input.text().strip(),
                'Website': self.website_input.text().strip(),
                'account': self.account_input.text().strip(),
                'account_webid': self.account_webid_input.text().strip(),
                'password': self.password_input.text().strip(),
                'password_webid': self.password_webid_input.text().strip()
            }


class ExportDialog(QDialog):
    """資料匯出對話框"""
    
    def __init__(self, parent=None, table_type=None):
        """
        初始化匯出對話框
        
        Args:
            parent: 父視窗
            table_type: 表格類型 ('cmd' 或 'prompt')
        """
        super().__init__(parent)
        self.table_type = table_type
        self.selected_file_path = ""
        
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle(f"匯出{'命令工具' if self.table_type == 'cmd' else '提示工具'}資料")
        self.setModal(True)
        self.resize(450, 200)
        
        layout = QVBoxLayout()
        
        # 匯出範圍選擇
        scope_group = QGroupBox("匯出範圍")
        scope_layout = QVBoxLayout()
        
        self.all_data_radio = QCheckBox("匯出全部資料")
        self.filtered_data_radio = QCheckBox("匯出目前篩選結果")
        self.filtered_data_radio.setChecked(True)  # 預設選擇篩選結果
        
        scope_layout.addWidget(self.all_data_radio)
        scope_layout.addWidget(self.filtered_data_radio)
        scope_group.setLayout(scope_layout)
        
        layout.addWidget(scope_group)
        
        # 檔案路徑選擇
        file_group = QGroupBox("檔案設定")
        file_layout = QFormLayout()
        
        self.filename_input = QLineEdit()
        self.filename_input.setText(f"{'cmdtools' if self.table_type == 'cmd' else 'prompttools'}_export.json")
        
        self.browse_button = QPushButton("瀏覽...")
        self.browse_button.clicked.connect(self.browse_file)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.filename_input)
        path_layout.addWidget(self.browse_button)
        
        file_layout.addRow("檔案名稱:", path_layout)
        file_group.setLayout(file_layout)
        
        layout.addWidget(file_group)
        
        # 按鈕區域
        button_layout = QHBoxLayout()
        
        self.export_button = QPushButton("匯出")
        self.cancel_button = QPushButton("取消")
        
        self.export_button.clicked.connect(self.accept_export)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def browse_file(self):
        """瀏覽檔案"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "選擇匯出檔案",
            self.filename_input.text(),
            "JSON 檔案 (*.json);;所有檔案 (*)"
        )
        
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
            self.filename_input.setText(file_path)
    
    def accept_export(self):
        """接受匯出設定"""
        if not self.filename_input.text().strip():
            QMessageBox.warning(self, "驗證錯誤", "請指定匯出檔案名稱")
            return
        
        if not self.filename_input.text().strip().endswith('.json'):
            QMessageBox.warning(self, "驗證錯誤", "檔案名稱必須以 .json 結尾")
            return
        
        self.selected_file_path = self.filename_input.text().strip()
        self.accept()
    
    def get_export_settings(self):
        """取得匯出設定"""
        return {
            'file_path': self.selected_file_path,
            'export_all': self.all_data_radio.isChecked(),
            'export_filtered': self.filtered_data_radio.isChecked()
        }


class ConfirmDialog(QDialog):
    """確認對話框"""
    
    def __init__(self, parent=None, title="確認", message="確定要執行此操作嗎？"):
        """
        初始化確認對話框
        
        Args:
            parent: 父視窗
            title: 對話框標題
            message: 確認訊息
        """
        super().__init__(parent)
        self.init_ui(title, message)
    
    def init_ui(self, title, message):
        """初始化 UI"""
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(300, 120)
        
        layout = QVBoxLayout()
        
        # 訊息標籤
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(message_label)
        
        # 按鈕區域
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("確定")
        self.cancel_button = QPushButton("取消")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)