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
            # 載入 CmdTools 資料
            self.cmd_tools_data = self._load_table_data("CmdTools", [
                "iSeqNo", "cmd", "example", "remark1", "remark2", "Classification"
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
                INSERT INTO CmdTools (cmd, example, remark1, remark2, Classification)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                data.get('cmd', ''),
                data.get('example', ''),
                data.get('remark1', ''),
                data.get('remark2', ''),
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
                'remark2': data.get('remark2', ''),
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
                UPDATE CmdTools SET cmd=%s, example=%s, remark1=%s, remark2=%s, Classification=%s
                WHERE iSeqNo=%s
            """
            values = (
                data.get('cmd', ''),
                data.get('example', ''),
                data.get('remark1', ''),
                data.get('remark2', ''),
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
                        'remark2': data.get('remark2', ''),
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
        """匯出資料為 JSON 格式"""
        from datetime import datetime
        
        export_data = {
            "export_time": datetime.now().isoformat(),
            "table_name": table_name,
            "total_records": total_count,
            "filtered_records": filtered_count,
            "data": data
        }
        
        return json.dumps(export_data, ensure_ascii=False, indent=2)