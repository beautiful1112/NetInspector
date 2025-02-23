<template>
  <el-container class="inspector-detail-container">
    <!-- Left Sidebar -->
    <el-aside width="200px" class="sidebar">
      <el-menu :default-active="activeMenu" :router="true" class="menu">
        <el-menu-item index="aiOps" @click="navigate('aiOps')">
          <el-icon><chat-line-square /></el-icon>
          <span>AI OPS</span>
        </el-menu-item>
        <el-menu-item index="aiInspection" @click="navigate('aiInspection')">
          <el-icon><search /></el-icon>
          <span>AI Inspection</span>
        </el-menu-item>
        <el-menu-item index="docs" @click="navigate('docs')">
          <el-icon><document /></el-icon>
          <span>Docs</span>
        </el-menu-item>
        <el-menu-item index="settings" @click="navigate('settings')">
          <el-icon><setting /></el-icon>
          <span>Settings</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- Main Content -->
    <el-container>
      <el-header class="header">
        <div class="title">NetInspector - Inspector Detail</div>
      </el-header>

      <el-main class="main-content">
        <el-row :gutter="20">
          <!-- Devices Info Panel -->
          <el-col :span="12">
            <el-card shadow="hover" class="card">
              <template #header>
                <div class="card-header">Devices Info</div>
              </template>
              <div class="panel-content">
                <div class="upload-section">
                  <span class="section-title">Upload Excel File:</span>
                  <el-upload
                    class="upload-demo"
                    drag
                    :action="`${baseURL}/api/upload/excel-to-yaml`"
                    :on-success="handleUploadSuccess"
                    :on-error="handleUploadError"
                    :before-upload="(file) => beforeUpload(file, 'excel')"
                    :on-remove="handleRemove"
                    :file-list="excelFileList"
                    accept=".xls,.xlsx"
                    :headers="uploadHeaders"
                  >
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                      Drop Excel file here or <em>click to upload</em>
                    </div>
                  </el-upload>
                </div>
                <el-divider />
                <div class="select-section">
                  <span class="section-title">Select YAML Template:</span>
                  <el-select
                    v-model="selectedDeviceYaml"
                    placeholder="Select a YAML file"
                    class="full-width"
                    @change="loadDeviceConfig"
                  >
                    <el-option
                      v-for="item in deviceYamlTemplates"
                      :key="item.path"
                      :label="item.name"
                      :value="item.path"
                    />
                  </el-select>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- Credential Panel -->
          <el-col :span="12">
            <el-card shadow="hover" class="card">
              <template #header>
                <div class="card-header">Credential</div>
              </template>
              <div class="panel-content">
                <div class="upload-section">
                  <span class="section-title">Upload YAML File:</span>
                  <el-upload
                    class="upload-demo"
                    drag
                    :action="`${baseURL}/api/upload/credential`"
                    :on-success="handleUploadSuccess"
                    :on-error="handleUploadError"
                    :before-upload="(file) => beforeUpload(file, 'yaml')"
                    :on-remove="handleRemove"
                    :file-list="credentialFileList"
                    accept=".yaml,.yml"
                    :headers="uploadHeaders"
                  >
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                      Drop YAML file here or <em>click to upload</em>
                    </div>
                  </el-upload>
                </div>
                <el-divider />
                <div class="select-section">
                  <span class="section-title">Select Existing YAML File:</span>
                  <el-select
                    v-model="selectedCredentialYaml"
                    placeholder="Select a YAML file"
                    class="full-width"
                    @change="loadCredentialConfig"
                  >
                    <el-option
                      v-for="item in credentialYamlFiles"
                      :key="item.path"
                      :label="item.name"
                      :value="item.path"
                    />
                  </el-select>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-divider />

        <el-row :gutter="20">
          <!-- Commands Panel -->
          <el-col :span="12">
            <el-card shadow="hover" class="card">
              <template #header>
                <div class="card-header">Commands</div>
              </template>
              <div class="panel-content">
                <div class="upload-section">
                  <span class="section-title">Upload JSON Template:</span>
                  <el-upload
                    class="upload-demo"
                    drag
                    :action="`${baseURL}/api/upload/commands`"
                    :on-success="handleUploadSuccess"
                    :on-error="handleUploadError"
                    :before-upload="(file) => beforeUpload(file, 'json')"
                    :on-remove="handleRemove"
                    :file-list="commandsFileList"
                    accept=".json"
                    :headers="uploadHeaders"
                  >
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                      Drop JSON file here or <em>click to upload</em>
                    </div>
                  </el-upload>
                </div>
                <el-divider />
                <div class="select-section">
                  <span class="section-title">Select Existing JSON Template:</span>
                  <el-select
                    v-model="selectedCommandJson"
                    placeholder="Select a JSON file"
                    class="full-width"
                    @change="loadCommandConfig"
                  >
                    <el-option
                      v-for="item in commandJsonTemplates"
                      :key="item.path"
                      :label="item.name"
                      :value="item.path"
                    />
                  </el-select>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- Prompt Panel -->
          <el-col :span="12">
            <el-card shadow="hover" class="card">
              <template #header>
                <div class="card-header">Prompt</div>
              </template>
              <div class="panel-content">
                <div class="upload-section">
                  <span class="section-title">Upload TXT File:</span>
                  <el-upload
                    class="upload-demo"
                    drag
                    :action="`${baseURL}/api/upload/prompt`"
                    :on-success="handleUploadSuccess"
                    :on-error="handleUploadError"
                    :before-upload="(file) => beforeUpload(file, 'txt')"
                    :on-remove="handleRemove"
                    :file-list="promptFileList"
                    accept=".txt"
                    :headers="uploadHeaders"
                  >
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                      Drop TXT file here or <em>click to upload</em>
                    </div>
                  </el-upload>
                </div>
                <el-divider />
                <div class="select-section">
                  <span class="section-title">Select Existing TXT File:</span>
                  <el-select
                    v-model="selectedPromptTxt"
                    placeholder="Select a TXT file"
                    class="full-width"
                    @change="loadPromptConfig"
                  >
                    <el-option
                      v-for="item in promptTxtFiles"
                      :key="item.path"
                      :label="item.name"
                      :value="item.path"
                    />
                  </el-select>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-divider />

        <!-- Start Inspection Button -->
        <el-row>
          <el-col :span="24" class="text-center">
            <el-button type="primary" size="large" @click="startInspection">
              Start Inspection
            </el-button>
          </el-col>
        </el-row>

        <el-divider />

        <!-- Console Output -->
        <el-row>
          <el-col :span="24">
            <el-card shadow="hover" class="card">
              <template #header>
                <div class="card-header">Console</div>
              </template>
              <pre class="console-output">
                <span v-for="(line, idx) in consoleLogs" :key="idx">{{ line }}</span>
              </pre>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from '@/utils/axios'

import {
  ChatLineSquare,
  Search,
  Document,
  Setting,
  UploadFilled
} from '@element-plus/icons-vue'

export default {
  name: 'InspectorDetail',
  components: {
    ChatLineSquare,
    Search,
    Document,
    Setting,
    UploadFilled
  },
  setup() {
    const message = ElMessage
    return {
      message
    }
  },
  data() {
    return {
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      activeMenu: 'aiInspection',
      excelFileList: [],
      credentialFileList: [],
      commandsFileList: [],
      promptFileList: [],
      selectedDeviceYaml: null,
      deviceYamlTemplates: [],
      selectedCredentialYaml: null,
      credentialYamlFiles: [],
      selectedCommandJson: null,
      selectedDeviceType: '',
      selectedDeviceIp: '',
      deviceTypes: ['firewall', 'switch', 'wireless'], // 从你的配置中获取
      deviceIps: [],
      commandJsonTemplates: [],
      selectedPromptTxt: null,
      promptTxtFiles: [],
      consoleLogs: [
        'System initialized. Waiting for inspection to start...'
      ],
      uploadHeaders: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      fileTypeLimits: {
        excel: { extensions: ['.xls', '.xlsx'], maxSize: 5 },
        yaml: { extensions: ['.yaml', '.yml'], maxSize: 2 },
        json: { extensions: ['.json'], maxSize: 2 },
        txt: { extensions: ['.txt'], maxSize: 1 }
      }
    }
  },
  created() {
    console.log('Component InspectorDetail created, loading file lists...')
    this.loadFileLists()
  },
  methods: {
    navigate(page) {
      this.activeMenu = page
      const routes = {
        aiOps: 'Home',
        aiInspection: 'InspectorDetail',
        docs: 'Docs',
        settings: 'Settings'
      }
      if (routes[page]) {
        this.$router.push({ name: routes[page] })
      }
    },

    beforeUpload(file, type) {
      const { extensions, maxSize } = this.fileTypeLimits[type]

      // 检查文件类型
      const isValidType = extensions.some(ext =>
        file.name.toLowerCase().endsWith(ext)
      )

      // 检查文件大小 (MB)
      const isValidSize = file.size / 1024 / 1024 < maxSize

      if (!isValidType) {
        this.message.error(`Please upload ${extensions.join('/')} file!`)
        return false
      }
      if (!isValidSize) {
        this.message.error(`File size cannot exceed ${maxSize}MB!`)
        return false
      }
      return true
    },

    handleUploadSuccess(response, file, fileList) {
      console.log('Upload success:', response)
      this.message({
        message: `File ${file.name} uploaded successfully`,
        type: 'success'
      })

      const extension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
      const fileListMap = {
        '.xls': 'excelFileList',
        '.xlsx': 'excelFileList',
        '.yaml': 'credentialFileList',
        '.yml': 'credentialFileList',
        '.json': 'commandsFileList',
        '.txt': 'promptFileList'
      }

      if (fileListMap[extension]) {
        this[fileListMap[extension]] = fileList
        this.loadFileLists()
      }
    },

    handleUploadError(error, file) {
      console.error('Upload error:', error)
      console.error('File:', file)

      let errorMessage = 'Upload failed'
      if (error.response) {
        console.error('Error response:', error.response)
        errorMessage = error.response.data?.detail || error.response.statusText
      } else if (error.request) {
        errorMessage = 'No response from server'
      } else {
        errorMessage = error.message
      }

      this.message({
        message: `File ${file.name} upload failed: ${errorMessage}`,
        type: 'error',
        duration: 5000
      })
    },

    handleRemove(file, fileList) {
      console.log('Removed file:', file)
      const extension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
      const fileListMap = {
        '.xls': 'excelFileList',
        '.xlsx': 'excelFileList',
        '.yaml': 'credentialFileList',
        '.yml': 'credentialFileList',
        '.json': 'commandsFileList',
        '.txt': 'promptFileList'
      }

      if (fileListMap[extension]) {
        this[fileListMap[extension]] = fileList
        this.loadFileLists()
      }
    },

    async fetchWithRetry(url, config, retries) {
      try {
        return await axios.get(url, config)
      } catch (error) {
        if (retries > 0) {
          console.log(`Retrying... ${retries} attempts left`)
          await new Promise(resolve => setTimeout(resolve, 1000))
          return this.fetchWithRetry(url, config, retries - 1)
        }
        throw error
      }
    },

    async loadFileLists(retryCount = 3) {
      try {
        console.log('Loading file lists...')
        const config = {
          headers: this.uploadHeaders,
          cache: false,
          timeout: 5000
        }

        const directories = {
          device: 'config',
          commands: 'templates/commands',
          prompts: 'templates/prompts'
        }

        const responses = await Promise.all(
          Object.entries(directories).map(([key, dir]) =>
            this.fetchWithRetry(`/api/files/list?directory=${dir}`, config, retryCount)
          )
        )

        const [deviceResponse, commandsResponse, promptsResponse] = responses

        this.deviceYamlTemplates = this.filterFiles(deviceResponse.data.files, ['.yaml', '.yml'])
        this.credentialYamlFiles = this.deviceYamlTemplates
        this.commandJsonTemplates = this.filterFiles(commandsResponse.data.files, ['.json'])
        this.promptTxtFiles = this.filterFiles(promptsResponse.data.files, ['.txt'])

      } catch (error) {
        console.error('Error loading file lists:', error)
        this.handleError(error)
        this.resetFileLists()
      }
    },

    filterFiles(files, extensions) {
      return (files || []).filter(file =>
        extensions.some(ext => file.name.toLowerCase().endsWith(ext))
      )
    },

    resetFileLists() {
      this.deviceYamlTemplates = []
      this.credentialYamlFiles = []
      this.commandJsonTemplates = []
      this.promptTxtFiles = []
    },

    handleError(error) {
      const message = error.response?.data?.detail || error.message
      this.message({
        message: `Operation failed: ${message}`,
        type: 'error',
        duration: 5000
      })
    },

    loadDeviceConfig(value) {
      console.log('Selected device YAML:', value)
      this.message({
        message: `Loaded device config: ${value}`,
        type: 'success'
      })
    },

    loadCredentialConfig(value) {
      console.log('Selected credential YAML:', value)
      this.message({
        message: `Loaded credential config: ${value}`,
        type: 'success'
      })
    },

    loadCommandConfig(value) {
      console.log('Selected command JSON:', value)
      this.message({
        message: `Loaded command template: ${value}`,
        type: 'success'
      })
    },

    loadPromptConfig(value) {
      console.log('Selected prompt TXT:', value)
      this.message({
        message: `Loaded prompt template: ${value}`,
        type: 'success'
      })
    },

  async startInspection() {
      if (this.isInspecting) return;

      try {
        this.isInspecting = true;
        this.consoleLogs = ['Starting inspection...'];

        // 准备文件路径数据
        const requestData = {
          deviceYaml: this.selectedDeviceYaml,
          credentialYaml: this.selectedCredentialYaml,
          commandJson: this.selectedCommandJson,
          promptTxt: this.selectedPromptTxt
        };

        console.log('Starting inspection with paths:', requestData);

        // 发送请求
        const response = await axios.post('/api/inspection/start', requestData);

        // 处理响应
        if (response.data) {
          // 更新控制台日志
          if (Array.isArray(response.data.logs)) {
            this.consoleLogs = response.data.logs;
          }

          // 显示成功消息
          this.$message.success('Inspection completed successfully');
        }

      } catch (error) {
        console.error('Inspection error:', error);

        let errorMessage = 'Inspection failed: ';
        if (error.response?.data?.detail) {
          errorMessage += error.response.data.detail;
        } else if (error.message) {
          errorMessage += error.message;
        } else {
          errorMessage += 'Unknown error occurred';
        }

        this.consoleLogs.push(`Error: ${errorMessage}`);
        this.$message.error(errorMessage);

      } finally {
        this.isInspecting = false;
      }
    },
     async loadFileLists() {
        try {
          // 加载设备YAML模板
          const deviceYamlResponse = await axios.get('/api/files/list?directory=config');
          this.deviceYamlTemplates = deviceYamlResponse.data.files;

          // 加载凭证YAML文件
          const credentialYamlResponse = await axios.get('/api/files/list?directory=config');
          this.credentialYamlFiles = credentialYamlResponse.data.files;

          // 加载命令JSON模板
          const commandJsonResponse = await axios.get('/api/files/list?directory=templates/commands');
          this.commandJsonTemplates = commandJsonResponse.data.files;

          // 加载提示TXT文件
          const promptTxtResponse = await axios.get('/api/files/list?directory=templates/prompts');
          this.promptTxtFiles = promptTxtResponse.data.files;

        } catch (error) {
          console.error('Error loading file lists:', error);
          this.$message.error('Failed to load file lists');
        }
      }
  }
}
</script>

<style scoped>
.inspector-detail-container {
  height: 100vh;
  background-color: var(--el-bg-color);
}

.sidebar {
  background-color: var(--el-menu-bg-color);
  color: var(--el-text-color-primary);
}

.menu {
  height: 100%;
  border-right: none;
}

.header {
  background-color: white;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--el-border-color-light);
}

.title {
  font-size: 20px;
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.main-content {
  padding: 20px;
  background-color: var(--el-bg-color-page);
  overflow-y: auto;
}

.card {
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.card-header {
  font-size: 16px;
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.panel-content {
  margin-top: 10px;
}

.section-title {
  font-weight: bold;
  margin-bottom: 10px;
  display: block;
  color: var(--el-text-color-primary);
}

.text-center {
  text-align: center;
}

.full-width {
  width: 100%;
}

.console-output {
  background-color: #1e1e1e;
  color: #00ff00;
  font-family: 'Courier New', Courier, monospace;
  padding: 15px;
  height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  border-radius: 4px;
}

:deep(.el-upload) {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

.upload-section {
  margin-bottom: 20px;
}

.select-section {
  margin-top: 20px;
}

/* Loading state styles */
.el-loading-mask {
  background-color: rgba(255, 255, 255, 0.8);
}

/* Error state styles */
.upload-error {
  border: 1px solid var(--el-color-danger);
}

/* Success state styles */
.upload-success {
  border: 1px solid var(--el-color-success);
}
</style>