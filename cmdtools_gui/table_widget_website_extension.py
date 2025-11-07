# -*- coding: utf-8 -*-
"""
網站管理分頁擴展功能
為網站管理分頁添加開啟網站按鈕功能
"""

# 這些是需要在 table_widget.py 中添加的函數

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