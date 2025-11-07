# 新增資料表 SQL 腳本

## WinProgram 表格

```sql
CREATE TABLE `WinProgram` (
	`iSeqNo` INT(11) NOT NULL AUTO_INCREMENT,
	`remark1` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`ProgramPathAndName` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`ClickEndRun` INT(11) NULL DEFAULT NULL,
	PRIMARY KEY (`iSeqNo`) USING BTREE
);
```

## WebSite 表格

```sql
CREATE TABLE `WebSite` (
	`iSeqNo` INT(11) NOT NULL AUTO_INCREMENT,
	`Remark` VARCHAR(250) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`Classification` VARCHAR(250) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`Website` VARCHAR(250) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`account` VARCHAR(250) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`account_webid` VARCHAR(250) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`password` VARCHAR(250) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`password_webid` VARCHAR(250) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	PRIMARY KEY (`iSeqNo`) USING BTREE
) COMMENT='登入 Website'
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=4;
```

## 使用說明

請在 MySQL 資料庫中執行上述 SQL 語句來創建兩個新表格。