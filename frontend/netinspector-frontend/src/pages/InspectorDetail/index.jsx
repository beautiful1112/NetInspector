import React, { useState, useRef, useEffect } from 'react';
import { Card, Select, Button, message, Space, Collapse, Typography, Row, Col, Table, Checkbox, Upload } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import axios from '@/utils/axios';
import './styles.css';

const { Panel } = Collapse;
const { Title, Text } = Typography;
const { Option } = Select;

const InspectorDetail = () => {
  const [selectedHosts, setSelectedHosts] = useState([]);
  const [hostsList, setHostsList] = useState([]);
  const [commandFiles, setCommandFiles] = useState([]);
  const [promptFiles, setPromptFiles] = useState([]);
  const [selectedCommand, setSelectedCommand] = useState('');
  const [selectedPrompt, setSelectedPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [logs, setLogs] = useState([]);
  const terminalRef = useRef(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);

  // 定义表格列
  const columns = [
    {
      title: 'Device Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'IP Address',
      dataIndex: 'ip',
      key: 'ip',
    },
    {
      title: 'Platform',
      dataIndex: 'platform',
      key: 'platform',
    },
    {
      title: 'Groups',
      dataIndex: 'groups',
      key: 'groups',
      render: (groups) => groups.join(', '),
    },
  ];

  // 表格选择配置
  const rowSelection = {
    selectedRowKeys,
    onChange: (selectedKeys) => {
      setSelectedRowKeys(selectedKeys);
      setSelectedHosts(selectedKeys); // 更新选中的主机列表
    },
  };

  // 获取主机列表
  useEffect(() => {
    fetchHosts();
    fetchTemplateFiles();
  }, []);

  const fetchHosts = async () => {
    try {
      const response = await axios.get('/api/hosts/list');
      setHostsList(response.data.hosts || []);
    } catch (error) {
      console.error('Failed to fetch hosts:', error);
      message.error('Failed to load hosts list');
    }
  };

  const fetchTemplateFiles = async () => {
    try {
      // 获取命令文件
      const commandsResponse = await axios.get('/api/files/list?directory=templates/commands');
      setCommandFiles(commandsResponse.data.files || []);

      // 获取提示文件
      const promptsResponse = await axios.get('/api/files/list?directory=templates/prompts');
      setPromptFiles(promptsResponse.data.files || []);
    } catch (error) {
      console.error('Failed to fetch template files:', error);
      message.error('Failed to load template files');
    }
  };

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const newLog = {
      time: timestamp,
      message,
      type
    };
    setLogs(prevLogs => [...prevLogs, newLog]);
    
    if (terminalRef.current) {
      setTimeout(() => {
        terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
      }, 100);
    }
  };

  const startInspection = async () => {
    if (!selectedRowKeys.length) {
      message.error('Please select at least one host');
      return;
    }
    if (!selectedCommand || !selectedPrompt) {
      message.error('Please select command and prompt files');
      return;
    }

    setLoading(true);
    addLog('Starting inspection process...', 'info');
    addLog(`Selected hosts: ${selectedRowKeys.join(', ')}`, 'info');
    addLog(`Command file: ${selectedCommand}`, 'info');
    addLog(`Prompt file: ${selectedPrompt}`, 'info');

    try {
      const response = await axios.post('/api/inspection/start', {
        hosts: selectedRowKeys,
        commandFile: selectedCommand,
        promptFile: selectedPrompt
      });

      if (response.data.status === 'success') {
        addLog('Inspection started successfully', 'success');
        response.data.results.forEach(result => {
          if (result.status === 'success') {
            addLog(`Host ${result.host}: Inspection completed`, 'success');
            addLog(`Raw config saved to: ${result.raw_config}`, 'info');
            addLog(`Report generated at: ${result.report}`, 'info');
          } else {
            addLog(`Host ${result.host}: Inspection failed - ${result.error}`, 'error');
          }
        });
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      addLog(`Error: ${error.message}`, 'error');
      message.error('Inspection failed');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file, type) => {
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const endpoint = type === 'command' ? '/api/upload/commands' : '/api/upload/prompt';
      const response = await axios.post(endpoint, formData);
      if (response.data.message) {
        message.success(`${file.name} uploaded successfully`);
        await fetchTemplateFiles();
        return true;
      }
    } catch (error) {
      message.error(`${file.name} upload failed`);
    } finally {
      setUploading(false);
    }
    return false;
  };

  // 文件上传配置
  const uploadProps = (type) => ({
    showUploadList: false,
    beforeUpload: (file) => {
      const isValidType = type === 'command' 
        ? file.name.endsWith('.json')
        : file.name.endsWith('.txt');
      
      if (!isValidType) {
        message.error(`${type === 'command' ? 'Command templates must be JSON files' : 'Prompt templates must be TXT files'}`);
        return false;
      }
      
      handleUpload(file, type);
      return false;
    },
  });

  return (
    <div className="inspector-container">
      <Card title="Network Device Inspector" className="main-card">
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="Device Selection" className="selection-card">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Table
                  rowSelection={rowSelection}
                  columns={columns}
                  dataSource={hostsList}
                  rowKey="name"
                  size="middle"
                  pagination={false}
                  className="devices-table"
                />

                <div className="select-item">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Text strong>Command Template:</Text>
                    <Space>
                      <Select
                        style={{ width: '300px' }}
                        placeholder="Select command template"
                        value={selectedCommand}
                        onChange={setSelectedCommand}
                      >
                        {commandFiles.map(file => (
                          <Option key={file.path} value={file.path}>
                            {file.name}
                          </Option>
                        ))}
                      </Select>
                      <Upload {...uploadProps('command')}>
                        <Button icon={<UploadOutlined />} loading={uploading}>
                          Upload Command
                        </Button>
                      </Upload>
                    </Space>
                  </Space>
                </div>

                <div className="select-item">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Text strong>Prompt Template:</Text>
                    <Space>
                      <Select
                        style={{ width: '300px' }}
                        placeholder="Select prompt template"
                        value={selectedPrompt}
                        onChange={setSelectedPrompt}
                      >
                        {promptFiles.map(file => (
                          <Option key={file.path} value={file.path}>
                            {file.name}
                          </Option>
                        ))}
                      </Select>
                      <Upload {...uploadProps('prompt')}>
                        <Button icon={<UploadOutlined />} loading={uploading}>
                          Upload Prompt
                        </Button>
                      </Upload>
                    </Space>
                  </Space>
                </div>

                <Button 
                  type="primary" 
                  onClick={startInspection}
                  loading={loading}
                  disabled={!selectedRowKeys.length || !selectedCommand || !selectedPrompt}
                  block
                >
                  Start Inspection
                </Button>
              </Space>
            </Card>
          </Col>

          <Col span={24}>
            <Card title="Inspection Logs" className="logs-card">
              <div className="terminal" ref={terminalRef}>
                {logs.length === 0 ? (
                  <div className="empty-logs">No inspection logs yet. Start an inspection to see logs here.</div>
                ) : (
                  logs.map((log, index) => (
                    <div key={index} className={`log-line ${log.type}`}>
                      <span className="log-time">[{log.time}]</span>
                      <span className="log-message">{log.message}</span>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default InspectorDetail; 