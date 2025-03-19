import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import Layout from './components/Layout';
import Home from './pages/Home';
import Configuration from './pages/Configuration';
import InspectorDetail from './pages/InspectorDetail';
import Settings from './pages/Settings';
import './styles/theme.css';

const theme = {
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
    colorBgContainer: '#ffffff',
    colorBgLayout: '#f0f2f5',
  },
};

const App = () => {
  return (
    <ConfigProvider theme={theme}>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/configuration" element={<Configuration />} />
          <Route path="/inspector" element={<InspectorDetail />} />
          <Route path="/settings" element={<Settings />} />
          {/* 可以添加更多路由 */}
        </Routes>
      </Layout>
    </ConfigProvider>
  );
};

export default App; 