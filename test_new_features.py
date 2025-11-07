# -*- coding: utf-8 -*-
"""
測試新增功能的測試腳本
"""

import mysql.connector
import json
import os
from cmdtools_gui.database import DatabaseManager


def create_test_database():
    """建立測試資料庫"""
    print("創建測試資料庫...")

    # 讀取配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 連接到 MySQL 伺服器（不指定資料庫）
    conn = mysql.connector.connect(
        host=config['DBServer'],
        port=config['DBPort'],
        user=config['DBUser'],
        password=config['DBPassword'],
    )
    
    cursor = conn.cursor()
    
    # 創建測試資料庫
    test_db_name = config['DataBase'] + '_test'
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {test_db_name}")
    cursor.execute(f"USE {test_db_name}")
    
    # 創建測試表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS WinProgram (
            iSeqNo INT(11) NOT NULL AUTO_INCREMENT,
            remark1 VARCHAR(150) NULL DEFAULT NULL,
            ProgramPathAndName VARCHAR(150) NULL DEFAULT NULL,
            ClickEndRun INT(11) NULL DEFAULT NULL,
            PRIMARY KEY (iSeqNo)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS WebSite (
            iSeqNo INT(11) NOT NULL AUTO_INCREMENT,
            Remark VARCHAR(250) NULL DEFAULT NULL,
            Classification VARCHAR(250) NULL DEFAULT NULL,
            Website VARCHAR(250) NULL DEFAULT NULL,
            account VARCHAR(250) NULL DEFAULT NULL,
            password VARCHAR(250) NULL DEFAULT NULL,
            PRIMARY KEY (iSeqNo)
        )
    """)
    
    # 插入測試數據
    cursor.execute("""
        INSERT INTO WinProgram (remark1, ProgramPathAndName, ClickEndRun)
        VALUES ('記事本', 'notepad.exe', 1)
    """)
    
    cursor.execute("""
        INSERT INTO WebSite (Remark, Classification, Website, account, password)
        VALUES ('我的網站', '工作', 'https://example.com', 'user', 'pass')
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"測試資料庫 {test_db_name} 創建成功")
    return test_db_name


def test_database_manager():
    """測試 DatabaseManager 類"""
    print("\n測試 DatabaseManager 類...")
    
    # 建立測試資料庫
    test_db_name = create_test_database()
    
    # 修改配置以使用測試資料庫
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    original_db = config['DataBase']
    config['DataBase'] = test_db_name
    
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    try:
        # 測試 DatabaseManager
        db_manager = DatabaseManager()
        
        # 測試連線
        if db_manager.connect():
            print("資料庫連線成功")
        else:
            print("資料庫連線失敗")
            return
        
        # 測試載入資料
        success, message = db_manager.load_all_data()
        if success:
            print(f"資料載入成功: {message}")
            print(f"WinProgram 記錄數: {len(db_manager.win_program_data)}")
            print(f"WebSite 記錄數: {len(db_manager.web_site_data)}")
        else:
            print(f"資料載入失敗: {message}")
            return
        
        # 測試新增 WinProgram 記錄
        new_win_program = {
            'remark1': '測試程式',
            'ProgramPathAndName': 'test.exe',
            'ClickEndRun': 0
        }
        success, message = db_manager.add_win_program(new_win_program)
        if success:
            print(f"WinProgram 新增成功: {message}")
        else:
            print(f"WinProgram 新增失敗: {message}")
        
        # 測試新增 WebSite 記錄
        new_web_site = {
            'Remark': '測試網站',
            'Classification': '測試',
            'Website': 'https://test.com',
            'account': 'test',
            'password': 'test123'
        }
        success, message = db_manager.add_web_site(new_web_site)
        if success:
            print(f"WebSite 新增成功: {message}")
        else:
            print(f"WebSite 新增失敗: {message}")
        
        # 測試篩選功能
        print("\n測試篩選功能...")
        win_program_filtered = db_manager.filter_win_program({'remark1': '記事本'})
        print(f"WinProgram 篩選結果: {len(win_program_filtered)} 條記錄")
        
        web_site_filtered = db_manager.filter_web_site({'Remark': '我的網站'})
        print(f"WebSite 篩選結果: {len(web_site_filtered)} 條記錄")
        
        # 測試更新記錄
        if len(db_manager.win_program_data) > 0:
            seq_no = db_manager.win_program_data[0]['iSeqNo']
            update_data = {
                'remark1': '記事本（已更新）',
                'ProgramPathAndName': 'notepad++.exe',
                'ClickEndRun': 1
            }
            success, message = db_manager.update_win_program(seq_no, update_data)
            if success:
                print(f"WinProgram 更新成功: {message}")
            else:
                print(f"WinProgram 更新失敗: {message}")
        
        if len(db_manager.web_site_data) > 0:
            seq_no = db_manager.web_site_data[0]['iSeqNo']
            update_data = {
                'Remark': '我的網站（已更新）',
                'Classification': '工作相關',
                'Website': 'https://example.com/new',
                'account': 'newuser',
                'password': 'newpass'
            }
            success, message = db_manager.update_web_site(seq_no, update_data)
            if success:
                print(f"WebSite 更新成功: {message}")
            else:
                print(f"WebSite 更新失敗: {message}")
        
        # 測試刪除記錄
        if len(db_manager.win_program_data) > 0:
            seq_no = db_manager.win_program_data[-1]['iSeqNo']
            success, message = db_manager.delete_win_program(seq_no)
            if success:
                print(f"WinProgram 刪除成功: {message}")
            else:
                print(f"WinProgram 刪除失敗: {message}")
        
        # 測試匯出功能
        print("\n測試匯出功能...")
        export_data = db_manager.export_to_json(
            db_manager.win_program_data,
            "WinProgram",
            len(db_manager.win_program_data),
            len(db_manager.win_program_data)
        )
        
        with open('test_winprogram_export.json', 'w', encoding='utf-8') as f:
            f.write(export_data)
        print("WinProgram 資料匯出成功: test_winprogram_export.json")
        
        export_data = db_manager.export_to_json(
            db_manager.web_site_data,
            "WebSite",
            len(db_manager.web_site_data),
            len(db_manager.web_site_data)
        )
        
        with open('test_website_export.json', 'w', encoding='utf-8') as f:
            f.write(export_data)
        print("WebSite 資料匯出成功: test_website_export.json")
        
        print("\n所有 DatabaseManager 測試完成!")
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
    finally:
        # 恢復原始資料庫配置
        config['DataBase'] = original_db
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # 清理測試資料庫
        conn = mysql.connector.connect(
            host=config['DBServer'],
            port=config['DBPort'],
            user=config['DBUser'],
            password=config['DBPassword'],
        )
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"測試資料庫 {test_db_name} 已刪除")


def test_requirements():
    """測試依賴套件"""
    print("\n測試依賴套件...")
    
    required_packages = ['PyQt5', 'mysql.connector', 'selenium']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PyQt5':
                import PyQt5
                print(f"[OK] {package} 已安裝")
            elif package == 'mysql.connector':
                import mysql.connector
                print(f"[OK] {package} 已安裝")
            elif package == 'selenium':
                import selenium
                print(f"[OK] {package} 已安裝")
        except ImportError:
            print(f"[X] {package} 未安裝")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少以下套件，請執行: pip install {' '.join(missing_packages)}")
    else:
        print("\n所有必要套件已安裝")


def test_config():
    """測試配置"""
    print("\n測試配置...")
    
    if not os.path.exists('config.json'):
        print("[X] config.json 文件不存在")
        return
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_keys = ['DBServer', 'DBPort', 'DBUser', 'DBPassword', 'DataBase']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            print(f"[X] 缺少以下配置項: {', '.join(missing_keys)}")
        else:
            print("[OK] config.json 配置完整")
            
            # 測試資料庫連線
            try:
                conn = mysql.connector.connect(
                    host=config['DBServer'],
                    port=config['DBPort'],
                    user=config['DBUser'],
                    password=config['DBPassword'],
                    database=config['DataBase'],
                )
                
                cursor = conn.cursor()
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                print(f"[OK] 資料庫連線成功，找到 {len(tables)} 個表格")
                
                # 檢查是否存在 WinProgram 和 WebSite 表格
                table_names = [table[0] for table in tables]
                
                if 'WinProgram' in table_names:
                    print("[OK] WinProgram 表格存在")
                else:
                    print("[X] WinProgram 表格不存在，請執行 create_new_tables.md 中的 SQL")
                
                if 'WebSite' in table_names:
                    print("[OK] WebSite 表格存在")
                else:
                    print("[X] WebSite 表格不存在，請執行 create_new_tables.md 中的 SQL")
                
                cursor.close()
                conn.close()
            except mysql.connector.Error as e:
                print(f"[X] 資料庫連線失敗: {e}")
                
    except Exception as e:
        print(f"[X] 讀取 config.json 時發生錯誤: {e}")


def main():
    """主測試函數"""
    print("開始測試新增功能...")
    print("=" * 50)
    
    # 測試依賴套件
    test_requirements()
    
    # 測試配置
    test_config()
    
    # 測試 DatabaseManager 類
    test_database_manager()
    
    print("\n" + "=" * 50)
    print("所有測試完成!")


if __name__ == "__main__":
    main()