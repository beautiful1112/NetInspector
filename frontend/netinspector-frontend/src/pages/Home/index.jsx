import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Switch, Modal, message, Card, Spin, Typography } from 'antd';
import { SendOutlined, CodeOutlined, LoadingOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons';
import axios from '@/utils/axios';
import './styles.css';

const { TextArea } = Input;
const { Title, Text } = Typography;

const Home = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [terminalOn, setTerminalOn] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [pendingCommand, setPendingCommand] = useState(null);
  const [terminalContent, setTerminalContent] = useState([]);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  
  // 自动滚动到最新消息
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 发送消息
  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('/api/chat', {
        message: input
      });

      if (response.data.command) {
        setPendingCommand(response.data.command);
        setShowConfirm(true);
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response
      }]);

    } catch (error) {
      message.error('Failed to send message');
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  // 确认执行命令
  const handleConfirmCommand = async () => {
    try {
      const response = await axios.post('/api/execute-command', {
        command: pendingCommand
      });

      setTerminalContent(prev => [...prev, 
        `> Executing command: ${pendingCommand}`,
        response.data.output
      ]);

      message.success('Command executed successfully');
    } catch (error) {
      message.error('Failed to execute command');
    } finally {
      setShowConfirm(false);
      setPendingCommand(null);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const renderMessage = (msg, idx) => {
    const isUser = msg.role === 'user';
    return (
      <div key={idx} className={`message-wrapper ${isUser ? 'user' : 'assistant'}`}>
        <div className="message-avatar">
          {isUser ? <UserOutlined /> : <RobotOutlined />}
        </div>
        <div className="message-content">
          <Text className="message-text">{msg.content}</Text>
          <div className="message-time">
            {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="home-container">
      <div className="chat-section">
        <Card 
          title={
            <div className="chat-header">
              <Title level={4}>AI Network Assistant</Title>
              <div className="terminal-switch">
                <Text>Terminal</Text>
                <Switch
                  checked={terminalOn}
                  onChange={setTerminalOn}
                  checkedChildren="On"
                  unCheckedChildren="Off"
                />
              </div>
            </div>
          }
          className="chat-card"
        >
          <div className="chat-messages" ref={chatContainerRef}>
            {messages.map((msg, idx) => renderMessage(msg, idx))}
            {loading && (
              <div className="loading-message">
                <Spin indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />} />
                <Text type="secondary">AI is thinking...</Text>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            <TextArea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message here..."
              autoSize={{ minRows: 1, maxRows: 4 }}
              onKeyPress={handleKeyPress}
              disabled={loading}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSend}
              loading={loading}
              className="send-button"
            >
              Send
            </Button>
          </div>
        </Card>
      </div>

      {terminalOn && (
        <Card 
          title={
            <div className="terminal-header">
              <CodeOutlined /> Terminal Output
            </div>
          }
          className="terminal-card"
        >
          <div className="terminal-content">
            {terminalContent.map((line, idx) => (
              <div key={idx} className="terminal-line">
                {line}
              </div>
            ))}
          </div>
        </Card>
      )}

      <Modal
        title="Confirm Command Execution"
        open={showConfirm}
        onOk={handleConfirmCommand}
        onCancel={() => setShowConfirm(false)}
        okText="Execute"
        cancelText="Cancel"
        className="command-modal"
      >
        <div className="command-preview">
          <Text type="secondary">Are you sure you want to execute the following command?</Text>
          <pre className="command-code">{pendingCommand}</pre>
        </div>
      </Modal>
    </div>
  );
};

export default Home; 