# -*- coding: utf-8 -*-
"""
MySQL 資料庫連線和管理模組
負責資料庫連線、資料載入快取和 CRUD 操作
"""

import json
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional, Tuple
import os


class DatabaseManager:
    """資料庫管理類"""
    
    def __init__(self, config_file: str = 'config.json'):
        """初始化資料庫管理器"""
        self.config = self._load_config(config_file)
        self.connection = None
        self.cmd_tools_data = []
        self.prompt_tools_data = []
        self.win_program_data = []
        self.web_site_data = []
        
    def _load_config(self, config_file: str) -> Dict:
        """載入資料庫配置"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                raise FileNotFoundError(f"配置文件 {config_file} 不存在")
        except Exception as e:
            raise Exception(f"無法載入配置文件: {e}")
    
    def connect(self) -> bool:
        """連線到資料庫"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config['DBServer'],
                port=self.config['DBPort'],
                user=self.config['DBUser'],
                password=self.config['DBPassword'],
                database=self.config['DataBase'],
                charset='utf8mb4',
                use_unicode=True
            )
            return True
        except Error as e:
            print(f"資料庫連線錯誤: {e}")
            return False
    
    def disconnect(self):
        """中斷資料庫連線"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def load_all_data(self) -> Tuple[bool, str]:
        """載入所有資料到記憶體"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False, "無法連線到資料庫"
        
        try:
            # 載入 CmdTools 資料（已移除 remark2 欄位）
            self.cmd_tools_data = self._load_table_data("CmdTools", [
                "iSeqNo", "cmd", "example", "remark1", "Classification"
            ])
            
            # 載入 PromptTools 資料
            self.prompt_tools_data = self._load_table_data("PromptTools", [
                "iSeqNo", "Prompt", "Prompt_Eng", "Classification"
            ])
            
            # 載入 WinProgram 資料
            self.win_program_data = self._load_table_data("WinProgram", [
                "iSeqNo", "remark1", "ProgramPathAndName", "ClickEndRun"
            ])
            
            # 載入 WebSite 資料
            self.web_site_data = self._load_table_data("WebSite", [
                "iSeqNo", "Remark", "Classification", "Website", "account", "account_webid", "password", "password_webid"
            ])
            
            return True, "資料載入成功"
            
        except Exception as e:
            return False, f"載入資料時發生錯誤: {e}"
    
    def _load_table_data(self, table_name: str, columns: List[str]) -> List[Dict]:
        """載入指定資料表的資料"""
        if not self.connection:
            raise Exception("未建立資料庫連線")
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 構建查詢 SQL
            columns_str = ", ".join(columns)
            query = f"SELECT {columns_str} FROM {table_name} ORDER BY iSeqNo"
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            # 轉換 None 值為空字串
            for row in results:
                for key, value in row.items():
                    if value is None:
                        row[key] = ""
            
            cursor.close()
            return results
            
        except Exception as e:
            raise Exception(f"載入 {table_name} 資料時發生錯誤: {e}")
    
    # CmdTools CRUD 操作
    
    def add_cmd_tool(self, data: Dict) -> Tuple[bool, str]:
        """新增命令工具記錄"""
        try:
            cursor = self.connection.cursor()
            
            sql = """
                INSERT INTO CmdTools (cmd, example, remark1, Classification)
                VALUES (%s, %s, %s, %s)
            """
            values = (
                data.get('cmd', ''),
                data.get('example', ''),
                data.get('remark1', ''),
                data.get('Classification', '')
            )
            
            cursor.execute(sql, values)
            self.connection.commit()
            
            # 獲取新插入的序號
            new_id = cursor.lastrowid
            
            # 更新本地快取
            new_record = {
                'iSeqNo': new_id,
                'cmd': data.get('cmd', ''),
                'example': data.get('example', ''),
                'remark1': data.get('remark1', ''),
                'Classification': data.get('Classification', '')
            }
            self.cmd_tools_data.append(new_record)
            
            cursor.close()
            return True, "命令工具新增成功"
            
        except Exception as e:
            return False, f"新增命令工具失敗: {e}"
    
    def update_cmd_tool(self, seq_no: int, data: Dict) -> Tuple[bool, str]:
        """更新命令工具記錄"""
        try:
            cursor = self.connection.cursor()
            
            sql = """
                UPDATE CmdTools SET cmd=%s, example=%s, remark1=%s, Classification=%s
                WHERE iSeqNo=%s
            """
            values = (
                data.get('cmd', ''),
                data.get('example', ''),
                data.get('remark1', ''),
                data.get('Classification', ''),
                seq_no
            )
            
            cursor.execute(sql, values)
            self.connection.commit()
            cursor.close()
            
            # 更新本地快取
            for record in self.cmd_tools_data:
                if record['iSeqNo'] == seq_no:
                    record.update({
                        'cmd': data.get('cmd', ''),
                        'example': data.get('example', ''),
                        'remark1': data.get('remark1', ''),
                        'Classification': data.get('Classification', '')
                    })
                    break
            
            return True, "命令工具更新成功"
            
        except Exception as e:
            return False, f"更新命令工具失敗: {e}"
    
    def delete_cmd_tool(self, seq_no: int) -> Tuple[bool, str]:
        """刪除命令工具記錄"""
        try:
            cursor = self.connection.cursor()
            
            sql = "DELETE FROM CmdTools WHERE iSeqNo = %s"
            cursor.execute(sql, (seq_no,))
            
            if cursor.rowcount == 0:
                cursor.close()
                return False, f"找不到序號 {seq_no} 的記錄"
            
            self.connection.commit()
            cursor.close()
            
            # 更新本地快取
            self.cmd_tools_data = [record for record in self.cmd_tools_data 
                                 if record['iSeqNo'] != seq_no]
            
            return True, "命令工具刪除成功"
            
        except Exception as e:
            return False, f"刪除命令工具失敗: {e}"
    
    # PromptTools CRUD 操作
    
    def add_prompt_tool(self, data: Dict) -> Tuple[bool, str]:
        """新增提示工具記錄"""
        try:
            cursor = self.connection.cursor()
            
            sql = """
                INSERT INTO PromptTools (Prompt, Prompt_Eng, Classification) 
                VALUES (%s, %s, %s)
            """
            values = (
                data.get('Prompt', ''),
                data.get('Prompt_Eng', ''),
                data.get('Classification', '')
            )
            
            cursor.execute(sql, values)
            self.connection.commit()
            
            # 獲取新插入的序號
            new_id = cursor.lastrowid
            
            # 更新本地快取
            new_record = {
                'iSeqNo': new_id,
                'Prompt': data.get('Prompt', ''),
                'Prompt_Eng': data.get('Prompt_Eng', ''),
                'Classification': data.get('Classification', '')
            }
            self.prompt_tools_data.append(new_record)
            
            cursor.close()
            return True, "提示工具新增成功"
            
        except Exception as e:
            return False, f"新增提示工具失敗: {e}"
    
    def update_prompt_tool(self, seq_no: int, data: Dict) -> Tuple[bool, str]:
        """更新提示工具記錄"""
        try:
            cursor = self.connection.cursor()
            
            sql = """
                UPDATE PromptTools SET Prompt=%s, Prompt_Eng=%s, Classification=%s 
                WHERE iSeqNo=%s
            """
            values = (
                data.get('Prompt', ''),
                data.get('Prompt_Eng', ''),
                data.get('Classification', ''),
                seq_no
            )
            
            cursor.execute(sql, values)
            self.connection.commit()
            cursor.close()
            
            # 更新本地快取
            for record in self.prompt_tools_data:
                if record['iSeqNo'] == seq_no:
                    record.update({
                        'Prompt': data.get('Prompt', ''),
                        'Prompt_Eng': data.get('Prompt_Eng', ''),
                        'Classification': data.get('Classification', '')
                    })
                    break
            
            return True, "提示工具更新成功"
            
        except Exception as e:
            return False, f"更新提示工具失敗: {e}"
    
    def delete_prompt_tool(self, seq_no: int) -> Tuple[bool, str]:
        """刪除提示工具記錄"""
        try:
            cursor = self.connection.cursor()
            
            sql = "DELETE FROM PromptTools WHERE iSeqNo = %s"
            cursor.execute(sql, (seq_no,))
            
            if cursor.rowcount == 0:
                cursor.close()
                return False, f"找不到序號 {seq_no} 的記錄"
            
            self.connection.commit()
            cursor.close()
            
            # 更新本地快取
            self.prompt_tools_data = [record for record in self.prompt_tools_data 
                                    if record['iSeqNo'] != seq_no]
            
            return True, "提示工具刪除成功"
            
        except Exception as e:
            return False, f"刪除提示工具失敗: {e}"
    
    # 資料篩選功能
    
    def filter_cmd_tools(self, filters: Dict[str, str]) -> List[Dict]:
        """篩選命令工具資料"""
        filtered_data = self.cmd_tools_data.copy()
        
        for field, keyword in filters.items():
            if keyword.strip():  # 非空搜尋關鍵字
                keyword_lower = keyword.lower()
                filtered_data = [
                    record for record in filtered_data
                    if keyword_lower in str(record.get(field, "")).lower()
                ]
        
        return filtered_data
    
    def filter_prompt_tools(self, filters: Dict[str, str]) -> List[Dict]:
        """篩選提示工具資料"""
        filtered_data = self.prompt_tools_data.copy()
        
        for field, keyword in filters.items():
            if keyword.strip():  # 非空搜尋關鍵字
                keyword_lower = keyword.lower()
                filtered_data = [
                    record for record in filtered_data
                    if keyword_lower in str(record.get(field, "")).lower()
                ]
        
        return filtered_data
    
    # WinProgram CRUD 操作
    
    def add_win_program(self, data: Dict) -> Tuple[bool, str]:
        """新增 Windows 程式記錄"""
        try:
            cursor = self.connection.cursor()
            
            sql = """
                INSERT INTO WinProgram (remark1, ProgramPathAndName, ClickEndRun)
                VALUES (%s, %s, %s)
            """
            values = (
                data.get('remark1', ''),
                data.get('ProgramPathAndName', ''),
                data.get('ClickEndRun', 0)
            )
            
            cursor.execute(sql, values)
            self.connection.commit()
            
            # 獲取新插入的序號
            new_id = cursor.lastrowid
            
            # 更新本地快取
            new_record = {
                'iSeqNo': new_id,
                'remark1': data.get('remark1', ''),
                'ProgramPathAndName': data.get('ProgramPathAndName', ''),
                'ClickEndRun': data.get('ClickEndRun', 0)
            }
            self.win_program_data.append(new_record)
            
            cursor.close()
            return True, "Windows 程式新增成功"
            
        except Exception as e:
            return False, f"新增 Windows 程式失敗: {e}"
    
    def update_win_program(self, seq_no: int, data: Dict) -> Tuple[bool, str]:
        """更新 Windows 程式記錄"""
        try:
            cursor = self.connection.cursor()
            
            sql = """
                UPDATE WinProgram SET remark1=%s, ProgramPathAndName=%s, ClickEndRun=%s
                WHERE iSeqNo=%s
            """
            values = (
                data.get('remark1', ''),
                data.get('ProgramPathAndName', ''),
                data.get('ClickEndRun', 0),
                seq_no
            )
            
            cursor.execute(sql, values)
            self.connection.commit()
            cursor.close()
            
            # 更新本地快取
            for record in self.win_program_data:
                if record['iSeqNo'] == seq_no:
                    record.update({
                        'remark1': data.get('remark1', ''),
                        'ProgramPathAndName': data.get('ProgramPathAndName', ''),
                        'ClickEndRun': data.get('ClickEndRun', 0)
                    })
                    break
            
            return True, "Windows 程式更新成功"
            
        except Exception as e:
            return False, f"更新 Windows 程式失敗: {e}"
    
    def delete_win_program(self, seq_no: int) -> Tuple[bool, str]:
        """刪除 Windows 程式記錄"""
        try:
            cursor = self.connection.cursor()
            
            sql = "DELETE FROM WinProgram WHERE iSeqNo = %s"
            cursor.execute(sql, (seq_no,))
            
            if cursor.rowcount == 0:
                cursor.close()
                return False, f"找不到序號 {seq_no} 的記錄"
            
            self.connection.commit()
            cursor.close()
            
            # 更新本地快取
            self.win_program_data = [record for record in self.win_program_data
                                   if record['iSeqNo'] != seq_no]
            
            return True, "Windows 程式刪除成功"
            
        except Exception as e:
            return False, f"刪除 Windows 程式失敗: {e}"
    
    # WebSite CRUD 操作
    
    def add_web_site(self, data: Dict) -> Tuple[bool, str]:
        """新增網站記錄"""
        try:
            cursor = self.connection.cursor()
            
            sql = """
                INSERT INTO WebSite (Remark, Classification, Website, account, account_webid, password, password_webid)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                data.get('Remark', ''),
                data.get('Classification', ''),
                data.get('Website', ''),
                data.get('account', ''),
                data.get('account_webid', ''),
                data.get('password', ''),
                data.get('password_webid', '')
            )
            
            cursor.execute(sql, values)
            self.connection.commit()
            
            # 獲取新插入的序號
            new_id = cursor.lastrowid
            
            # 更新本地快取
            new_record = {
                'iSeqNo': new_id,
                'Remark': data.get('Remark', ''),
                'Classification': data.get('Classification', ''),
                'Website': data.get('Website', ''),
                'account': data.get('account', ''),
                'account_webid': data.get('account_webid', ''),
                'password': data.get('password', ''),
                'password_webid': data.get('password_webid', '')
            }
            self.web_site_data.append(new_record)
            
            cursor.close()
            return True, "網站新增成功"
            
        except Exception as e:
            return False, f"新增網站失敗: {e}"
    
    def update_web_site(self, seq_no: int, data: Dict) -> Tuple[bool, str]:
        """更新網站記錄"""
        try:
            cursor = self.connection.cursor()
            
            sql = """
                UPDATE WebSite SET Remark=%s, Classification=%s, Website=%s, account=%s, account_webid=%s, password=%s, password_webid=%s
                WHERE iSeqNo=%s
            """
            values = (
                data.get('Remark', ''),
                data.get('Classification', ''),
                data.get('Website', ''),
                data.get('account', ''),
                data.get('account_webid', ''),
                data.get('password', ''),
                data.get('password_webid', ''),
                seq_no
            )
            
            cursor.execute(sql, values)
            self.connection.commit()
            cursor.close()
            
            # 更新本地快取
            for record in self.web_site_data:
                if record['iSeqNo'] == seq_no:
                    record.update({
                        'Remark': data.get('Remark', ''),
                        'Classification': data.get('Classification', ''),
                        'Website': data.get('Website', ''),
                        'account': data.get('account', ''),
                        'account_webid': data.get('account_webid', ''),
                        'password': data.get('password', ''),
                        'password_webid': data.get('password_webid', '')
                    })
                    break
            
            return True, "網站更新成功"
            
        except Exception as e:
            return False, f"更新網站失敗: {e}"
    
    def delete_web_site(self, seq_no: int) -> Tuple[bool, str]:
        """刪除網站記錄"""
        try:
            cursor = self.connection.cursor()
            
            sql = "DELETE FROM WebSite WHERE iSeqNo = %s"
            cursor.execute(sql, (seq_no,))
            
            if cursor.rowcount == 0:
                cursor.close()
                return False, f"找不到序號 {seq_no} 的記錄"
            
            self.connection.commit()
            cursor.close()
            
            # 更新本地快取
            self.web_site_data = [record for record in self.web_site_data
                                if record['iSeqNo'] != seq_no]
            
            return True, "網站刪除成功"
            
        except Exception as e:
            return False, f"刪除網站失敗: {e}"
    
    # 資料篩選功能擴展
    
    def filter_win_program(self, filters: Dict[str, str]) -> List[Dict]:
        """篩選 Windows 程式資料"""
        filtered_data = self.win_program_data.copy()
        
        for field, keyword in filters.items():
            if keyword.strip():  # 非空搜尋關鍵字
                keyword_lower = keyword.lower()
                filtered_data = [
                    record for record in filtered_data
                    if keyword_lower in str(record.get(field, "")).lower()
                ]
        
        return filtered_data
    
    def filter_web_site(self, filters: Dict[str, str]) -> List[Dict]:
        """篩選網站資料"""
        filtered_data = self.web_site_data.copy()
        
        for field, keyword in filters.items():
            if keyword.strip():  # 非空搜尋關鍵字
                keyword_lower = keyword.lower()
                filtered_data = [
                    record for record in filtered_data
                    if keyword_lower in str(record.get(field, "")).lower()
                ]
        
        return filtered_data
    
    # 匯出功能
     
    def export_to_json(self, data: List[Dict], table_name: str,
                      total_count: int, filtered_count: int) -> str:
        """匯出單一表格資料為 JSON 格式（舊匯出功能保留）"""
        from datetime import datetime
         
        export_data = {
            "export_time": datetime.now().isoformat(),
            "table_name": table_name,
            "total_records": total_count,
            "filtered_records": filtered_count,
            "data": data
        }
         
        return json.dumps(export_data, ensure_ascii=False, indent=2)
    
    def export_all_database(self, file_path: str):
        """
        匯出整個資料庫到單一 JSON 檔案。
        結構：
        {
          "export_time": "...",
          "tables": {
            "CmdTools": [...],
            "PromptTools": [...],
            "WinProgram": [...],
            "WebSite": [...]
          }
        }
        """
        from datetime import datetime
    
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False, "無法連線到資料庫，匯出失敗"
    
        try:
            # 確保最新資料
            load_ok, load_msg = self.load_all_data()
            if not load_ok:
                return False, f"載入資料失敗：{load_msg}"
    
            export_payload = {
                "export_time": datetime.now().isoformat(),
                "tables": {
                    "CmdTools": self.cmd_tools_data,
                    "PromptTools": self.prompt_tools_data,
                    "WinProgram": self.win_program_data,
                    "WebSite": self.web_site_data,
                }
            }
    
            # 建立目錄（若需要）
            os.makedirs(os.path.dirname(file_path), exist_ok=True) if os.path.dirname(file_path) else None
    
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_payload, f, ensure_ascii=False, indent=2)
    
            return True, "整個資料庫匯出成功"
    
        except Exception as e:
            return False, f"匯出整個資料庫時發生錯誤: {e}"
    
    def import_from_json_file(self, file_path: str):
        """
        從 JSON 檔匯入整個資料庫。
        規則：
        - 僅支援本函式輸出的結構或相容格式：
          { "tables": { "CmdTools": [...], "PromptTools": [...], "WinProgram": [...], "WebSite": [...] } }
        - 先 TRUNCATE 這四張表，再重新插入 JSON 資料。
        - 若任一步驟失敗，整體 ROLLBACK。
        - 注意：此操作具破壞性，請在 UI 端先提醒使用者備份。
        """
        if not os.path.exists(file_path):
            return False, f"找不到指定檔案: {file_path}"
    
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False, "無法連線到資料庫，匯入失敗"
    
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
    
            # 兼容格式判斷
            if "tables" in content and isinstance(content["tables"], dict):
                tables = content["tables"]
            else:
                # 若沒有 tables，就視為不支援的格式
                return False, "JSON 格式不正確，缺少 'tables' 區塊"
    
            cmdtools_rows = tables.get("CmdTools", [])
            prompt_rows = tables.get("PromptTools", [])
            win_rows = tables.get("WinProgram", [])
            web_rows = tables.get("WebSite", [])
    
            cursor = self.connection.cursor()
            try:
                # 使用交易保護
                self.connection.start_transaction()
    
                # 清空既有資料
                cursor.execute("TRUNCATE TABLE CmdTools")
                cursor.execute("TRUNCATE TABLE PromptTools")
                cursor.execute("TRUNCATE TABLE WinProgram")
                cursor.execute("TRUNCATE TABLE WebSite")
    
                # 匯入 CmdTools
                for row in cmdtools_rows:
                    cursor.execute(
                        """
                        INSERT INTO CmdTools (cmd, example, remark1, Classification)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            row.get("cmd", ""),
                            row.get("example", ""),
                            row.get("remark1", ""),
                            row.get("Classification", ""),
                        ),
                    )
    
                # 匯入 PromptTools
                for row in prompt_rows:
                    cursor.execute(
                        """
                        INSERT INTO PromptTools (Prompt, Prompt_Eng, Classification)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            row.get("Prompt", ""),
                            row.get("Prompt_Eng", ""),
                            row.get("Classification", ""),
                        ),
                    )
    
                # 匯入 WinProgram
                for row in win_rows:
                    cursor.execute(
                        """
                        INSERT INTO WinProgram (remark1, ProgramPathAndName, ClickEndRun)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            row.get("remark1", ""),
                            row.get("ProgramPathAndName", ""),
                            int(row.get("ClickEndRun", 0) or 0),
                        ),
                    )
    
                # 匯入 WebSite
                for row in web_rows:
                    cursor.execute(
                        """
                        INSERT INTO WebSite
                        (Remark, Classification, Website, account, account_webid, password, password_webid)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            row.get("Remark", ""),
                            row.get("Classification", ""),
                            row.get("Website", ""),
                            row.get("account", ""),
                            row.get("account_webid", ""),
                            row.get("password", ""),
                            row.get("password_webid", ""),
                        ),
                    )
    
                # 提交交易
                self.connection.commit()
                cursor.close()
    
                # 重新載入快取
                self.load_all_data()
    
                return True, "從 JSON 匯入資料庫成功"
    
            except Exception as e:
                self.connection.rollback()
                cursor.close()
                return False, f"匯入資料時發生錯誤，已還原變更: {e}"
    
        except Exception as e:
            return False, f"讀取或解析 JSON 檔案時發生錯誤: {e}"