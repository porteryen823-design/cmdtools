const express = require('express');
const cors = require('cors');
const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const port = 3001;

// 允許跨域請求
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 載入資料庫配置
let dbConfig;
try {
  const configPath = path.join(__dirname, '..', 'config.json');
  const configData = fs.readFileSync(configPath, 'utf8');
  dbConfig = JSON.parse(configData);
  console.log('資料庫配置載入成功:', {
    host: dbConfig.DBServer,
    port: dbConfig.DBPort,
    database: dbConfig.DataBase,
    user: dbConfig.DBUser
  });
} catch (error) {
  console.error('無法載入資料庫配置:', error);
  process.exit(1);
}

// MySQL連線池
let pool;
try {
  pool = mysql.createPool({
    host: dbConfig.DBServer,
    port: dbConfig.DBPort,
    user: dbConfig.DBUser,
    password: dbConfig.DBPassword,
    database: dbConfig.DataBase,
    charset: 'utf8mb4',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
  });
  console.log('MySQL連線池創建成功');
} catch (error) {
  console.error('MySQL連線池創建失敗:', error);
  process.exit(1);
}

// 測試資料庫連線
async function testConnection() {
  try {
    const connection = await pool.getConnection();
    console.log('✅ MySQL資料庫連線成功');
    connection.release();
    return true;
  } catch (error) {
    console.error('❌ MySQL資料庫連線失敗:', error.message);
    return false;
  }
}

// 輔助函數：獲取所有資料表資料
async function getTableData(tableName, columns) {
  try {
    const [rows] = await pool.execute(
      `SELECT ${columns.join(', ')} FROM ${tableName} ORDER BY iSeqNo`
    );
    return rows;
  } catch (error) {
    console.error(`獲取 ${tableName} 資料失敗:`, error);
    return [];
  }
}

// API 路由：取得所有資料
app.get('/api/data', async (req, res) => {
  try {
    const data = {
      cmd_tools: await getTableData('CmdTools', ['iSeqNo', 'cmd', 'example', 'remark1', 'Classification']),
      prompt_tools: await getTableData('PromptTools', ['iSeqNo', 'Prompt', 'Prompt_Eng', 'Classification']),
      win_programs: await getTableData('WinProgram', ['iSeqNo', 'remark1', 'ProgramPathAndName', 'ClickEndRun']),
      websites: await getTableData('WebSite', ['iSeqNo', 'Remark', 'Classification', 'Website', 'account', 'account_webid', 'password', 'password_webid'])
    };
    res.json(data);
  } catch (error) {
    console.error('API /api/data 錯誤:', error);
    res.status(500).json({ error: '獲取資料失敗' });
  }
});

// API 路由：取得命令工具資料
app.get('/api/cmd-tools', async (req, res) => {
  try {
    const data = await getTableData('CmdTools', ['iSeqNo', 'cmd', 'example', 'remark1', 'Classification']);
    res.json(data);
  } catch (error) {
    console.error('API /api/cmd-tools 錯誤:', error);
    res.status(500).json({ error: '獲取命令工具資料失敗' });
  }
});

// API 路由：取得提示工具資料
app.get('/api/prompt-tools', async (req, res) => {
  try {
    const data = await getTableData('PromptTools', ['iSeqNo', 'Prompt', 'Prompt_Eng', 'Classification']);
    res.json(data);
  } catch (error) {
    console.error('API /api/prompt-tools 錯誤:', error);
    res.status(500).json({ error: '獲取提示工具資料失敗' });
  }
});

// API 路由：取得Windows程式資料
app.get('/api/win-programs', async (req, res) => {
  try {
    const data = await getTableData('WinProgram', ['iSeqNo', 'remark1', 'ProgramPathAndName', 'ClickEndRun']);
    res.json(data);
  } catch (error) {
    console.error('API /api/win-programs 錯誤:', error);
    res.status(500).json({ error: '獲取Windows程式資料失敗' });
  }
});

// API 路由：取得網站資料
app.get('/api/websites', async (req, res) => {
  try {
    const data = await getTableData('WebSite', ['iSeqNo', 'Remark', 'Classification', 'Website', 'account', 'account_webid', 'password', 'password_webid']);
    res.json(data);
  } catch (error) {
    console.error('API /api/websites 錯誤:', error);
    res.status(500).json({ error: '獲取網站資料失敗' });
  }
});

// OpenDoc 功能：執行系統命令打開文檔
app.post('/api/opendoc', async (req, res) => {
  try {
    const { command, filePath } = req.body;
    
    if (!command && !filePath) {
      return res.status(400).json({
        error: '需要提供 command 或 filePath 參數'
      });
    }

    // 處理打開文檔的命令
    let cmd;
    if (command) {
      cmd = command;
    } else if (filePath) {
      // 根據文件類型選擇打開方式
      if (filePath.toLowerCase().endsWith('.pdf')) {
        cmd = `start "" "${filePath}"`;  // Windows PDF
      } else if (filePath.toLowerCase().endsWith('.doc') || filePath.toLowerCase().endsWith('.docx')) {
        cmd = `start "" "${filePath}"`;  // Windows Word
      } else if (filePath.toLowerCase().endsWith('.txt')) {
        cmd = `notepad "${filePath}"`;  // Windows 記事本
      } else if (filePath.toLowerCase().endsWith('.html') || filePath.toLowerCase().endsWith('.htm')) {
        cmd = `start "" "${filePath}"`;  // 瀏覽器打開
      } else {
        cmd = `start "" "${filePath}"`;  // 默認用系統默認程序打開
      }
    }

    // 執行命令
    exec(cmd, (error, stdout, stderr) => {
      if (error) {
        console.error('執行命令失敗:', error);
        return res.status(500).json({
          success: false,
          error: '打開文檔失敗',
          details: error.message
        });
      }
      
      console.log('命令執行成功:', cmd);
      res.json({
        success: true,
        message: '文檔已打開',
        command: cmd,
        timestamp: new Date().toISOString()
      });
    });

  } catch (error) {
    console.error('OpenDoc API 錯誤:', error);
    res.status(500).json({
      success: false,
      error: '執行失敗',
      details: error.message
    });
  }
});

// 批量OpenDoc功能：根據數據庫記錄打開多個文檔
app.post('/api/opendoc/batch', async (req, res) => {
  try {
    const { type, items } = req.body;
    
    if (!type || !Array.isArray(items) || items.length === 0) {
      return res.status(400).json({
        error: '需要提供 type 和 items 陣列參數'
      });
    }

    const results = [];
    const promises = [];

    for (const item of items) {
      const promise = new Promise((resolve) => {
        let cmd;
        
        switch (type) {
          case 'websites':
            if (item.Website) {
              cmd = `start "" "${item.Website}"`;
            }
            break;
          case 'programs':
            if (item.ProgramPathAndName) {
              cmd = item.ProgramPathAndName;
            }
            break;
          case 'files':
            if (item.filePath) {
              cmd = `start "" "${item.filePath}"`;
            }
            break;
          default:
            resolve({ success: false, error: `不支援的類型: ${type}` });
            return;
        }

        if (cmd) {
          exec(cmd, (error, stdout, stderr) => {
            if (error) {
              resolve({
                success: false,
                error: error.message,
                command: cmd,
                item: item
              });
            } else {
              resolve({
                success: true,
                message: '已打開',
                command: cmd,
                item: item
              });
            }
          });
        } else {
          resolve({ success: false, error: '無效的項目', item: item });
        }
      });
      
      promises.push(promise);
    }

    // 等待所有命令執行完成
    const allResults = await Promise.all(promises);
    const successCount = allResults.filter(r => r.success).length;
    
    res.json({
      success: successCount > 0,
      total: items.length,
      successCount: successCount,
      errorCount: items.length - successCount,
      results: allResults,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('批量OpenDoc API 錯誤:', error);
    res.status(500).json({
      success: false,
      error: '批量執行失敗',
      details: error.message
    });
  }
});

// 從資料庫打開指定類型的文檔
app.post('/api/opendoc/from-db', async (req, res) => {
  try {
    const { table, ids, filter } = req.body;
    
    if (!table) {
      return res.status(400).json({ error: '需要提供 table 參數' });
    }

    let data = [];
    let whereClause = '';
    let params = [];

    // 根據表格類型設置預設欄位
    switch (table) {
      case 'websites':
        data = await getTableData('WebSite', ['iSeqNo', 'Remark', 'Website']);
        break;
      case 'win_programs':
        data = await getTableData('WinProgram', ['iSeqNo', 'remark1', 'ProgramPathAndName']);
        break;
      case 'cmd_tools':
        data = await getTableData('CmdTools', ['iSeqNo', 'cmd', 'remark1']);
        break;
      case 'prompt_tools':
        data = await getTableData('PromptTools', ['iSeqNo', 'Prompt', 'remark1']);
        break;
      default:
        return res.status(400).json({ error: `不支援的表格: ${table}` });
    }

    // 過濾數據
    if (ids && Array.isArray(ids) && ids.length > 0) {
      data = data.filter(item => ids.includes(item.iSeqNo));
    }

    if (filter) {
      const filterLower = filter.toLowerCase();
      data = data.filter(item => {
        return Object.values(item).some(value =>
          String(value).toLowerCase().includes(filterLower)
        );
      });
    }

    if (data.length === 0) {
      return res.json({
        success: false,
        message: '沒有找到匹配的數據',
        data: []
      });
    }

    // 轉換為批處理格式
    let batchItems = [];
    switch (table) {
      case 'websites':
        batchItems = data.map(item => ({
          Website: item.Website,
          iSeqNo: item.iSeqNo,
          Remark: item.Remark
        }));
        break;
      case 'win_programs':
        batchItems = data.map(item => ({
          ProgramPathAndName: item.ProgramPathAndName,
          iSeqNo: item.iSeqNo,
          remark1: item.remark1
        }));
        break;
      default:
        batchItems = data;
    }

    // 調用批處理功能
    const { type } = req.body;
    const batchRequest = {
      type: table === 'websites' ? 'websites' :
            table === 'win_programs' ? 'programs' : 'files',
      items: batchItems
    };

    // 遞歸調用批處理API
    req.body = batchRequest;
    return app._router.handle(req, res, () => {
      // 這裡需要手動調用批處理邏輯，因為我們不能直接調用路由
      const originalTable = table;
      const originalData = data;
      
      // 簡化的批處理邏輯
      const results = [];
      const promises = [];

      for (const item of batchItems) {
        const promise = new Promise((resolve) => {
          let cmd;
          
          if (table === 'websites' && item.Website) {
            cmd = `start "" "${item.Website}"`;
          } else if (table === 'win_programs' && item.ProgramPathAndName) {
            cmd = item.ProgramPathAndName;
          }

          if (cmd) {
            exec(cmd, (error, stdout, stderr) => {
              if (error) {
                resolve({
                  success: false,
                  error: error.message,
                  command: cmd,
                  item: item
                });
              } else {
                resolve({
                  success: true,
                  message: '已打開',
                  command: cmd,
                  item: item
                });
              }
            });
          } else {
            resolve({ success: false, error: '無效的項目', item: item });
          }
        });
        
        promises.push(promise);
      }

      Promise.all(promises).then(allResults => {
        const successCount = allResults.filter(r => r.success).length;
        res.json({
          success: successCount > 0,
          total: batchItems.length,
          successCount: successCount,
          errorCount: batchItems.length - successCount,
          results: allResults,
          dataCount: data.length,
          timestamp: new Date().toISOString()
        });
      });
    });

  } catch (error) {
    console.error('從資料庫OpenDoc API 錯誤:', error);
    res.status(500).json({
      success: false,
      error: '從資料庫打開失敗',
      details: error.message
    });
  }
});

// 健康檢查端點
app.get('/health', async (req, res) => {
  const isConnected = await testConnection();
  res.json({
    status: isConnected ? 'healthy' : 'unhealthy',
    database: isConnected ? 'connected' : 'disconnected',
    timestamp: new Date().toISOString()
  });
});

// 啟動伺服器
async function startServer() {
  const isConnected = await testConnection();
  if (!isConnected) {
    console.warn('⚠️  資料庫連線失敗，但伺服器仍會啟動');
  }
  
  app.listen(port, () => {
    console.log(`🚀 後端伺服器啟動，監聽埠號 ${port}`);
    console.log(`📊 API端點:`);
    console.log(`   - GET /api/data (所有資料)`);
    console.log(`   - GET /api/cmd-tools (命令工具)`);
    console.log(`   - GET /api/prompt-tools (提示工具)`);
    console.log(`   - GET /api/win-programs (Windows程式)`);
    console.log(`   - GET /api/websites (網站)`);
    console.log(`   - GET /health (健康檢查)`);
  });
}

startServer();