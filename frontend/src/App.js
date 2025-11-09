import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [data, setData] = useState({
    cmd_tools: [],
    prompt_tools: [],
    win_programs: [],
    websites: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('cmd_tools');
  const [filterText, setFilterText] = useState(''); // 新增過濾文字狀態
  const [connectionStatus, setConnectionStatus] = useState(null);

  useEffect(() => {
    // 檢查健康狀態
    axios.get('http://localhost:3001/health')
      .then(response => {
        setConnectionStatus(response.data);
      })
      .catch(err => {
        setConnectionStatus({ status: 'unhealthy', database: 'disconnected' });
      });

    // 載入資料
    axios.get('http://localhost:3001/api/data')
      .then(response => {
        setData(response.data);
        setLoading(false);
      })
      .catch(err => {
        setError('無法取得資料: ' + (err.response?.data?.error || err.message));
        setLoading(false);
      });
  }, []);
  const getFilteredData = (tableData, filterText) => {
    if (!filterText) return tableData;
    const lowerCaseFilter = filterText.toLowerCase();
    return tableData.filter(row => 
      Object.values(row).some(value => 
        String(value).toLowerCase().includes(lowerCaseFilter)
      )
    );
  };

  const renderTable = (tableData, tableName) => {
    if (!tableData || tableData.length === 0) {
      return <div className="no-data">此資料表無資料</div>;
    }

    const columns = Object.keys(tableData[0]);
    
    return (
      <div className="table-container">
        <h3>{getTableDisplayName(tableName)} ({tableData.length} 筆記錄)</h3>
        <div style={{ overflowX: 'auto' }}> {/* 新增可滾動容器 */}
          <table border="1" cellPadding="5" cellSpacing="0" className="data-table">
            <thead>
            <tr>
              {columns.map((column) => (
                <th key={column}>{getColumnDisplayName(column)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tableData.map((row, idx) => (
              <tr key={idx}>
                {columns.map((column) => (
                  <td key={column}>
                    {row[column] === null || row[column] === '' ? '-' : String(row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        </div> {/* 關閉可滾動容器 */}
      </div>
    );
  };

  const getTableDisplayName = (tableName) => {
    const names = {
      'cmd_tools': '命令工具',
      'prompt_tools': '提示工具',
      'win_programs': 'Windows程式',
      'websites': '網站'
    };
    return names[tableName] || tableName;
  };

  const getColumnDisplayName = (column) => {
    const names = {
      'iSeqNo': '序號',
      'cmd': '命令',
      'example': '範例',
      'remark1': '備註1',
      'Classification': '類型',
      'Prompt': '提示',
      'Prompt_Eng': '英文提示',
      'Classification': '分類',
      'ProgramPathAndName': '程式路徑',
      'ClickEndRun': '點擊後執行',
      'Remark': '備註',
      'Website': '網站',
      'account': '帳號',
      'account_webid': '帳號元素ID',
      'password': '密碼',
      'password_webid': '密碼元素ID'
    };
    return names[column] || column;
  };

  if (loading) return (
    <div className="loading">
      <h2>MySQL資料載入中...</h2>
      <div className="spinner"></div>
    </div>
  );
  
  if (error) return (
    <div className="error">
      <h2>錯誤</h2>
      <p>{error}</p>
    </div>
  );

  return (
    <div className="app">
      <header>
        <h1>🎯 命令工具管理系統</h1>
        <div className="connection-status">
          <span className={`status-indicator ${connectionStatus?.database === 'connected' ? 'connected' : 'disconnected'}`}>
            ●
          </span>
          資料庫: {connectionStatus?.database === 'connected' ? '已連接' : '未連接'}
        </div>
      </header>

      <div className="tabs">
        {Object.keys(data).map((tableName) => (
          <button
            key={tableName}
            className={`tab ${activeTab === tableName ? 'active' : ''}`}
            onClick={() => setActiveTab(tableName)}
          >
            {getTableDisplayName(tableName)}
            <span className="count">({data[tableName]?.length || 0})</span>
          </button>
        ))}
      </div>

      <div className="filter-container">
        <input
          type="text"
          placeholder={`在 ${getTableDisplayName(activeTab)} 中過濾...`}
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
          className="filter-input"
        />
      </div>

      <div className="content">
        {renderTable(getFilteredData(data[activeTab], filterText), activeTab)}
      </div>

      <footer>
        <p>資料來源: MySQL資料庫 (127.0.0.1:3306) | 最後更新: {new Date().toLocaleString()}</p>
      </footer>
    </div>
  );
}

export default App;