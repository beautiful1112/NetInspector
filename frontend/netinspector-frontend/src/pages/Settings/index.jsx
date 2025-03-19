import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  InputNumber,
  Switch,
  Select,
  Button,
  Tabs,
  message,
  Space,
  Spin,
  Alert,
  Typography
} from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import axios from '@/utils/axios';
import './styles.css';

const { TabPane } = Tabs;
const { Option } = Select;
const { Text } = Typography;

const Settings = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const loadSettings = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('/api/settings');
      console.log('Loaded settings:', response.data);
      if (response.data) {
        form.setFieldsValue(response.data);
      }
    } catch (err) {
      console.error('Settings loading error:', err);
      setError(err.response?.data?.error || 'Failed to load settings');
      message.error('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const onFinish = async (values) => {
    setSaving(true);
    try {
      await axios.post('/api/settings', values);
      message.success('Settings saved successfully');
      await loadSettings();
    } catch (err) {
      message.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="settings-loading">
        <Spin size="large" />
        <span>Loading settings...</span>
      </div>
    );
  }

  return (
    <div className="settings-container">
      <Card 
        title="System Settings" 
        className="settings-card"
        extra={
          <Button 
            icon={<ReloadOutlined />} 
            onClick={loadSettings}
            loading={loading}
          >
            Refresh
          </Button>
        }
      >
        {error && (
          <Alert
            message="Error"
            description={error}
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}
        
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
        >
          <Tabs defaultActiveKey="connection">
            <TabPane tab="Connection" key="connection">
              <Form.Item
                label="Connect Timeout (seconds)"
                name={['connection', 'connect_timeout']}
                rules={[{ required: true }]}
              >
                <InputNumber min={1} max={300} />
              </Form.Item>
              <Form.Item
                label="Command Timeout (seconds)"
                name={['connection', 'command_timeout']}
                rules={[{ required: true }]}
              >
                <InputNumber min={1} max={600} />
              </Form.Item>
              <Form.Item
                label="Retry Times"
                name={['connection', 'retry_times']}
                rules={[{ required: true }]}
              >
                <InputNumber min={0} max={10} />
              </Form.Item>
              <Form.Item
                label="Retry Interval (seconds)"
                name={['connection', 'retry_interval']}
                rules={[{ required: true }]}
              >
                <InputNumber min={1} max={60} />
              </Form.Item>
            </TabPane>

            <TabPane tab="Logging" key="logging">
              <Form.Item
                label="Enable Console Output"
                name={['logging', 'enable_console']}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
              <Form.Item
                label="Log Level"
                name={['logging', 'log_level']}
                rules={[{ required: true }]}
              >
                <Select>
                  <Option value="DEBUG">Debug</Option>
                  <Option value="INFO">Info</Option>
                  <Option value="WARNING">Warning</Option>
                  <Option value="ERROR">Error</Option>
                </Select>
              </Form.Item>
              <Form.Item
                label="Log Directory"
                name={['logging', 'log_dir']}
                rules={[{ required: true }]}
              >
                <Input />
              </Form.Item>
              <Form.Item
                label="Log Format"
                name={['logging', 'log_format']}
                rules={[{ required: true }]}
              >
                <Input />
              </Form.Item>
            </TabPane>

            <TabPane tab="LangChain" key="langchain">
              <Form.Item
                label="Verbose Mode"
                name={['langchain', 'verbose']}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
              <Form.Item
                label="Debug Mode"
                name={['langchain', 'debug']}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </TabPane>

            <TabPane tab="AI Configuration" key="ai_config">
              <Form.Item
                label="API Base URL"
                name={['ai_config', 'api_base']}
                rules={[{ required: true }]}
              >
                <Input />
              </Form.Item>
              <Form.Item
                label="API Key"
                name={['ai_config', 'api_key']}
                rules={[{ required: true }]}
              >
                <Input.Password />
              </Form.Item>
              <Form.Item
                label="Model"
                name={['ai_config', 'model']}
                rules={[{ required: true }]}
              >
                <Input />
              </Form.Item>
            </TabPane>

            <TabPane tab="Directories" key="directories">
              <Form.Item
                label="Raw Configs Directory"
                name={['directories', 'raw_configs']}
              >
                <Input disabled />
              </Form.Item>
              <Form.Item
                label="Reports Directory"
                name={['directories', 'reports']}
              >
                <Input disabled />
              </Form.Item>
              <Text type="secondary">
                Directory settings are read-only and can only be modified in settings.py
              </Text>
            </TabPane>
          </Tabs>

          <Form.Item className="settings-submit">
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={saving}
                icon={<SaveOutlined />}
              >
                Save Settings
              </Button>
              <Button onClick={() => {
                form.resetFields();
                loadSettings();
              }}>
                Reset
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Settings; 