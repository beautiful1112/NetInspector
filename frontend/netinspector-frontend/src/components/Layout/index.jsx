import React, { useState, useEffect } from 'react';
import { Layout, Menu, Avatar, Dropdown, Badge, theme } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  MessageOutlined,
  SearchOutlined,
  SettingOutlined,
  BellOutlined,
  UserOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  HomeOutlined,
  ToolOutlined,
} from '@ant-design/icons';
import './styles.css';

const { Header, Sider, Content } = Layout;

const AppLayout = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = theme.useToken();

  const [notifications] = useState(3); // 示例通知数量

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: 'Home',
    },
    {
      key: '/inspector',
      icon: <SearchOutlined />,
      label: 'Inspector',
    },
    {
      key: '/configuration',
      icon: <SettingOutlined />,
      label: 'Configuration',
    },
    {
      key: '/settings',
      icon: <ToolOutlined />,
      label: 'Settings',
    },
  ];

  const userMenuItems = [
    {
      key: 'profile',
      label: 'Profile',
    },
    {
      key: 'logout',
      label: 'Logout',
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  return (
    <Layout className="app-layout">
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        style={{
          background: token.colorBgContainer,
          borderRight: `1px solid ${token.colorBorderSecondary}`,
        }}
        width={256}
      >
        <div className="logo">
          <img src="/vite.svg" alt="logo" />
          {!collapsed && <span>NetInspector</span>}
        </div>
        <Menu
          theme="light"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <div className="header-left">
            {React.createElement(collapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
              className: 'trigger',
              onClick: () => setCollapsed(!collapsed),
            })}
            <span className="page-title">
              {menuItems.find(item => item.key === location.pathname)?.label || 'Dashboard'}
            </span>
          </div>
          <div className="header-right">
            <Badge count={notifications} className="notification-badge">
              <BellOutlined className="header-icon" />
            </Badge>
            <Dropdown 
              menu={{ items: userMenuItems }} 
              placement="bottomRight"
              trigger={['click']}
            >
              <Avatar icon={<UserOutlined />} className="user-avatar" />
            </Dropdown>
          </div>
        </Header>
        <Content className="app-content">
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout; 