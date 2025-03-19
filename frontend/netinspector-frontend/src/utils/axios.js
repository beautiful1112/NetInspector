// src/utils/axios.js
import axios from 'axios'
import { message } from 'antd'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 创建axios实例
const instance = axios.create({
  baseURL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
})

// 请求拦截器
instance.interceptors.request.use(
  config => {
    // 在这里可以添加loading状态
    // 添加token等认证信息
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  response => {
    // 处理响应数据
    return response
  },
  error => {
    console.error('Response error:', error)
    const errorMessage = error.response?.data?.detail || error.message
    message.error(errorMessage)
    return Promise.reject(error)
  }
)

export default instance