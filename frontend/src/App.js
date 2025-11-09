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
  const [currentPage, setCurrentPage] = useState(1); // 當前頁碼
  const itemsPerPage = 10; // 每頁顯示 10 筆資料

  // 輔助函數：動態獲取後端 URL
  const getBackendUrl = async () => {
    try {
      // 嘗試從 public/backend_port.json 獲取實際埠號
      const response = await fetch('/backend_port.json');
      if (response.ok) {
        const { port } = await response.json();
        if (port) {
          console.log(`後端埠號從 backend_port.json 讀取成功: ${port}`);
          return `http://localhost:${port}`;
        }
      }
    } catch (e) {
      console.warn('無法讀取 backend_port.json，使用預設埠 3001');
    }
    // 預設回退
    return 'http://localhost:3001';
  };

  useEffect(() => {
    // 當 activeTab 改變時，重設頁碼
    setCurrentPage(1);
  }, [activeTab]);

  useEffect(() => {
    const fetchData = async () => {
      const backendUrl = await getBackendUrl();
      
      // 檢查健康狀態
      axios.get(`${backendUrl}/health`)
        .then(response => {
          setConnectionStatus(response.data);
        })
        .catch(err => {
          setConnectionStatus({ status: 'unhealthy', database: 'disconnected' });
        });

      // 載入資料
      axios.get(`${backendUrl}/api/data`)
        .then(response => {
          setData(response.data);
        setLoading(false);
      })
      .catch(err => {
        setError('無法取得資料: ' + (err.response?.data?.error || err.message));
        setLoading(false);
      })
      .catch(err => {
        setError('無法取得資料: ' + (err.response?.data?.error || err.message));
        setLoading(false);
      });
    };

    fetchData();
  }, []);
  
  const getFilteredAndPaginatedData = (tableData, filterText, page, itemsPerPage) => {
    // 1. 過濾
    let filteredData = tableData;
    if (filterText) {
      const lowerCaseFilter = filterText.toLowerCase();
      filteredData = tableData.filter(row =>
        Object.values(row).some(value =>
          String(value).toLowerCase().includes(lowerCaseFilter)
        )
      );
    }

    // 2. 分頁
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedData = filteredData.slice(startIndex, endIndex);

    return {
      filteredData, // 包含所有過濾後的資料 (用於計算總頁數)
      paginatedData // 僅包含當前頁的資料 (用於渲染表格)
    };
  };

  const renderTable = (paginatedData, tableName) => {
    if (!paginatedData || paginatedData.length === 0) {
      return <div className="no-data">此資料表無資料</div>;
    }

    const columns = Object.keys(paginatedData[0]);
    
    return (
      <div className="table-container">
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
            {paginatedData.map((row, idx) => (
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

  // 獲取當前過濾和分頁後的資料
  const { filteredData, paginatedData } = getFilteredAndPaginatedData(
    data[activeTab],
    filterText,
    currentPage,
    itemsPerPage
  );

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const renderPagination = () => {
    if (totalPages <= 1) return null;

    const pages = [];
    for (let i = 1; i <= totalPages; i++) {
      pages.push(
        <button
          key={i}
          className={`page-button ${currentPage === i ? 'active' : ''}`}
          onClick={() => handlePageChange(i)}
        >
          {i}
        </button>
      );
    }

    return (
      <div className="pagination-controls">
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          上一頁
        </button>
        {pages}
        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          下一頁
        </button>
      </div>
    );
  };

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
      
      <div className="table-info">
        <h3>{getTableDisplayName(activeTab)} ({filteredData.length} 筆記錄)</h3>
        {renderPagination()}
      </div>

      <div className="content">
        {renderTable(paginatedData, activeTab)}
      </div>

      <footer>
        <p>資料來源: MySQL資料庫 (127.0.0.1:3306) | 最後更新: {new Date().toLocaleString()}</p>
      </footer>
    </div>
  );
}

export default App;