# 網站管理分頁開啟網站功能整合指南

## 需要修改的檔案
`cmdtools_gui/table_widget.py`

## 需要的修改

### 1. 在現有的 `init_ui` 方法中修改按鈕創建邏輯

在第 374 行左右，將：
```python
# 根據表格類型添加相應的按鈕
if self.table_type == 'winprogram':
    self.create_execute_button(layout)
```

改為：
```python
# 根據表格類型添加相應的按鈕
if self.table_type == 'winprogram':
    self.create_execute_button(layout)
elif self.table_type == 'website':
    self.create_open_website_button(layout)
```

### 2. 在 TableTabWidget 類中添加以下三個新方法

```python
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
    
    if not website_url:
        QMessageBox.warning(self, "警告", "網站網址為空，無法開啟")
        return
    
    try:
        # 確保 URL 有正確的協議
        if not website_url.startswith(('http://', 'https://')):
            # 如果沒有協議，預設使用 https
            website_url = 'https://' + website_url
        
        # 開啟網站
        webbrowser.open(website_url)
        
        # 顯示成功訊息
        QMessageBox.information(self, "成功", f"已開啟網站: {website_url}")
        
    except Exception as e:
        QMessageBox.critical(self, "錯誤", f"開啟網站時發生錯誤: {str(e)}")
```

## 功能說明

### 開啟網站按鈕功能
- **按鈕顯示**：只在網站管理分頁顯示「開啟網站」按鈕
- **動態啟用**：根據選中的記錄自動啟用/禁用按鈕
  - 當選中記錄且網站網址不為空時啟用
  - 否則按鈕為灰色禁用狀態

### 狀態指示
- **按鈕文字**：顯示為「開啟網站: [網站域名]」
- **狀態標籤**：提供即時狀態訊息
  - 「網站可以開啟」（綠色）
  - 「網站網址為空」（灰色）
  - 「請先選擇一個網站」（灰色）

### 網站開啟機制
- **URL驗證**：檢查網站網址是否存在
- **協議處理**：自動添加 https:// 協議（如果缺少）
- **瀏覽器開啟**：使用系統默認瀏覽器開啟網站
- **錯誤處理**：完整的錯誤提示和異常處理

### 用戶體驗
- **選擇即反應**：選擇不同記錄時按鈕狀態即時更新
- **視覺反饋**：按鈕顏色和狀態標籤提供清晰視覺反饋
- **操作確認**：成功開啟後顯示確認訊息

## 整合後的完整功能

完成整合後，網站管理分頁將具備：
- ✅ 新增、編輯、刪除網站記錄
- ✅ 搜尋和篩選功能
- ✅ 直接開啟網站功能
- ✅ 資料匯出功能
- ✅ 狀態顯示和用戶反饋

這個功能與 Windows 程式分頁的執行按鈕功能類似，提供了一鍵操作體驗。