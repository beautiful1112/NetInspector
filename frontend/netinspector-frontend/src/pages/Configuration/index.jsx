import React, { useState, useEffect } from 'react';
import { Upload, Card, Button, message, Row, Col, Typography, Alert, Select, Space } from 'antd';
import { InboxOutlined, CheckCircleOutlined, SyncOutlined } from '@ant-design/icons';
import axios from '@/utils/axios';
import './styles.css';

const { Dragger } = Upload;
const { Title, Text } = Typography;
const { Option } = Select;

const Configuration = () => {
  const [fileList, setFileList] = useState({
    hosts: [],
    groups: [],
    defaults: []
  });
  const [existingFiles, setExistingFiles] = useState({
    hosts: [],
    groups: [],
    defaults: []
  });
  const [selectedFiles, setSelectedFiles] = useState({
    hosts: '',
    groups: '',
    defaults: ''
  });
  const [validationStatus, setValidationStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const configFiles = {
    hosts: {
      title: "Hosts Configuration",
      description: "Upload hosts.yaml containing device inventory information",
      help: "Define network devices with their connection parameters",
      accept: ".yaml,.yml"
    },
    groups: {
      title: "Groups Configuration",
      description: "Upload groups.yaml containing device group settings",
      help: "Define device groups with shared attributes and connection options",
      accept: ".yaml,.yml"
    },
    defaults: {
      title: "Defaults Configuration",
      description: "Upload defaults.yaml containing default settings",
      help: "Define default parameters for all devices",
      accept: ".yaml,.yml"
    }
  };

  // 获取现有配置文件列表
  const fetchExistingFiles = async () => {
    setIsLoading(true);
    try {
      console.log('Fetching existing files...');
      const response = await axios.get('/api/files/list?directory=config');
      console.log('Response:', response.data);

      if (response.data.files) {
        const files = response.data.files;
        const newExistingFiles = {
          hosts: files.filter(f => f.name.toLowerCase().includes('hosts')),
          groups: files.filter(f => f.name.toLowerCase().includes('groups')),
          defaults: files.filter(f => f.name.toLowerCase().includes('defaults'))
        };
        
        console.log('Filtered files:', newExistingFiles);
        setExistingFiles(newExistingFiles);
        
        // 自动选择默认文件
        Object.entries(newExistingFiles).forEach(([type, typeFiles]) => {
          if (typeFiles.length > 0) {
            const exactMatch = typeFiles.find(f => f.name === `${type}.yaml`);
            if (exactMatch) {
              setSelectedFiles(prev => ({
                ...prev,
                [type]: exactMatch.path
              }));
              console.log(`Selected ${type} file:`, exactMatch.path);
            }
          }
        });
      }
    } catch (error) {
      console.error('Failed to fetch files:', error);
      message.error('Failed to fetch existing configuration files');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchExistingFiles();
  }, []);

  const handleUpload = async ({ file, onSuccess, onError, fileType }) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', fileType);

    try {
      const response = await axios.post('/api/upload-config', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      if (response.data.success) {
        message.success(`${file.name} uploaded successfully`);
        onSuccess(response);
        await fetchExistingFiles(); // 重新获取文件列表
        
        // 自动选择上传的文件
        setSelectedFiles(prev => ({
          ...prev,
          [fileType]: response.data.path
        }));
      } else {
        throw new Error(response.data.error || 'Upload failed');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message;
      message.error(`${file.name} upload failed: ${errorMessage}`);
      onError(error);
    }
  };

  const validateConfigs = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/validate-configs');
      if (response.data.success) {
        setValidationStatus({
          type: 'success',
          message: response.data.message
        });
        message.success('Configuration validated successfully');
      } else {
        throw new Error(response.data.error);
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message;
      setValidationStatus({
        type: 'error',
        message: errorMessage
      });
      message.error('Configuration validation failed');
    } finally {
      setLoading(false);
    }
  };

  const getUploadProps = (fileType) => ({
    name: 'file',
    multiple: false,
    fileList: fileList[fileType],
    accept: configFiles[fileType].accept,
    onChange: (info) => {
      const newFileList = [...info.fileList].slice(-1);
      setFileList(prev => ({
        ...prev,
        [fileType]: newFileList
      }));
    },
    customRequest: ({ file, onSuccess, onError }) => {
      handleUpload({ file, onSuccess, onError, fileType });
    },
    onRemove: () => {
      setFileList(prev => ({
        ...prev,
        [fileType]: []
      }));
      setValidationStatus(null);
    }
  });

  const handleFileSelect = (value, type) => {
    setSelectedFiles(prev => ({
      ...prev,
      [type]: value || ''  // 处理清除选择的情况
    }));
    // 清除上传的文件
    setFileList(prev => ({
      ...prev,
      [type]: []
    }));
  };

  const allFilesReady = () => {
    return Object.keys(configFiles).every(type => {
      const hasUploadedFile = fileList[type].length > 0;
      const hasSelectedFile = Boolean(selectedFiles[type]);
      return hasUploadedFile || hasSelectedFile;
    });
  };

  return (
    <div className="config-container">
      <Title level={2}>Network Configuration</Title>
      <Text type="secondary" className="description">
        Upload and validate Nornir configuration files
      </Text>

      <Row gutter={[24, 24]} className="upload-row">
        {Object.entries(configFiles).map(([type, config]) => (
          <Col xs={24} md={8} key={type}>
            <Card 
              title={config.title}
              className="upload-card"
              extra={
                <Space>
                  <Select
                    placeholder="Select existing"
                    style={{ width: 150 }}
                    onChange={(value) => handleFileSelect(value, type)}
                    value={selectedFiles[type]}
                    allowClear
                  >
                    {existingFiles[type]?.map(file => (
                      <Option key={file.path} value={file.path}>{file.name}</Option>
                    ))}
                  </Select>
                  <Button
                    icon={<SyncOutlined />}
                    size="small"
                    onClick={fetchExistingFiles}
                    title="Refresh file list"
                  />
                </Space>
              }
            >
              <Dragger {...getUploadProps(type)} className="upload-dragger">
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">Click or drag file to upload</p>
                <p className="ant-upload-hint">{config.description}</p>
              </Dragger>
              <Text type="secondary" className="help-text">
                {config.help}
              </Text>
              {(fileList[type].length > 0 || selectedFiles[type]) && (
                <div className="file-status">
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  <span>File selected</span>
                </div>
              )}
            </Card>
          </Col>
        ))}
      </Row>

      <div className="action-section">
        <Button
          type="primary"
          size="large"
          onClick={validateConfigs}
          loading={loading}
          disabled={!allFilesReady()}
          block
        >
          Validate Configurations
        </Button>

        {validationStatus && (
          <Alert
            message={validationStatus.type === 'success' ? 'Success' : 'Error'}
            description={validationStatus.message}
            type={validationStatus.type}
            showIcon
            className="validation-alert"
          />
        )}
      </div>
    </div>
  );
};

export default Configuration; 