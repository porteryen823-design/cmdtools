const express = require('express');
const cors = require('cors');

const app = express();
const port = 3001;

// 允許跨域請求
app.use(cors());

// 模擬資料
const mockData = [
  { id: 1, name: '張三', age: 25, email: 'zhang@example.com' },
  { id: 2, name: '李四', age: 30, email: 'li@example.com' },
  { id: 3, name: '王五', age: 28, email: 'wang@example.com' },
  { id: 4, name: '趙六', age: 35, email: 'zhao@example.com' },
  { id: 5, name: '錢七', age: 22, email: 'qian@example.com' }
];

// API 路由：取得模擬資料
app.get('/api/data', (req, res) => {
  res.json(mockData);
});

app.listen(port, () => {
  console.log(`後端伺服器啟動，監聽埠號 ${port}`);
});