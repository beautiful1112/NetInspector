// src/utils/axios.js
import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 创建axios实例
const instance = axios.create({
  baseURL,
  timeout: 10000,
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
    // 处理错误响应
    if (error.response) {
      switch (error.response.status) {
        case 400:
          console.error('Bad request:', error.response.data)
          break
        case 401:
          console.error('Unauthorized:', error.response.data)
          break
        case 403:
          console.error('Forbidden:', error.response.data)
          break
        case 404:
          console.error('Not found:', error.response.data)
          break
        case 500:
          console.error('Server error:', error.response.data)
          break
        default:
          console.error('Error:', error.response.data)
      }
    } else if (error.request) {
      console.error('No response received:', error.request)
    } else {
      console.error('Error setting up request:', error.message)
    }
    return Promise.reject(error)
  }
)

export default instance