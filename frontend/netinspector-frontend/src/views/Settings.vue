<template>
<el-container class="settings-container">
<!-- Sidebar Navigation -->
<el-aside width="200px" class="sidebar">
<el-menu :default-active="activeMenu">
<el-menu-item index="aiOps" @click="navigate('aiOps')">
<i class="el-icon-chat-line-square"></i>
<span>AI OPS</span>
</el-menu-item>
<el-menu-item index="aiInspection" @click="navigate('aiInspection')">
<i class="el-icon-search"></i>
<span>AI Inspection</span>
</el-menu-item>
<el-menu-item index="docs" @click="navigate('docs')">
<i class="el-icon-document"></i>
<span>Docs</span>
</el-menu-item>
<el-menu-item index="settings" @click="navigate('settings')">
<i class="el-icon-setting"></i>
<span>Settings</span>
</el-menu-item>
</el-menu>
</el-aside>
  <!-- Main Content Area -->
<el-container>
  <!-- Header Section -->
  <el-header class="header">
    <div class="title">Settings</div>
  </el-header>

  <!-- Content Section -->
  <el-main class="main-content">
    <el-form ref="settingsForm" :model="settings" label-width="200px">
      <!-- Tabs for different settings groups -->
      <el-tabs v-model="activeTab" type="card">
        <!-- Connection Settings Tab -->
        <el-tab-pane label="Connection Settings" name="connection">
          <el-form-item label="Connect Timeout (seconds)">
            <el-input-number v-model="settings.connectTimeout" :min="1"></el-input-number>
          </el-form-item>
          <el-form-item label="Command Timeout (seconds)">
            <el-input-number v-model="settings.commandTimeout" :min="1"></el-input-number>
          </el-form-item>
          <el-form-item label="Retry Times">
            <el-input-number v-model="settings.retryTimes" :min="0"></el-input-number>
          </el-form-item>
          <el-form-item label="Retry Interval (seconds)">
            <el-input-number v-model="settings.retryInterval" :min="1"></el-input-number>
          </el-form-item>
        </el-tab-pane>

        <!-- Log Settings Tab -->
        <el-tab-pane label="Log Settings" name="log">
          <el-form-item label="Enable Console Output">
            <el-switch v-model="settings.enableConsoleOutput"></el-switch>
          </el-form-item>
          <el-form-item label="Log Directory">
            <el-input v-model="settings.logDir"></el-input>
          </el-form-item>
          <el-form-item label="Log Level">
            <el-select v-model="settings.logLevel" placeholder="Select Log Level">
              <el-option label="DEBUG" value="DEBUG"></el-option>
              <el-option label="INFO" value="INFO"></el-option>
              <el-option label="WARNING" value="WARNING"></el-option>
              <el-option label="ERROR" value="ERROR"></el-option>
              <el-option label="CRITICAL" value="CRITICAL"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="Log Format">
            <el-input v-model="settings.logFormat"></el-input>
          </el-form-item>
        </el-tab-pane>

        <!-- LangChain Settings Tab -->
        <el-tab-pane label="LangChain Settings" name="langchain">
          <el-form-item label="LangChain Verbose">
            <el-switch v-model="settings.langchainVerbose"></el-switch>
          </el-form-item>
          <el-form-item label="LangChain Debug">
            <el-switch v-model="settings.langchainDebug"></el-switch>
          </el-form-item>
        </el-tab-pane>

        <!-- AI Settings Tab -->
        <el-tab-pane label="AI Settings" name="ai">
          <el-form-item label="API Base">
            <el-input v-model="settings.aiSettings.apiBase"></el-input>
          </el-form-item>
          <el-form-item label="API Key">
            <el-input v-model="settings.aiSettings.apiKey" show-password></el-input>
          </el-form-item>
          <el-form-item label="Model">
            <el-input v-model="settings.aiSettings.model"></el-input>
          </el-form-item>
        </el-tab-pane>

        <!-- Output Directories Tab -->
        <el-tab-pane label="Output Directories" name="output">
          <el-form-item label="Raw Configs Directory">
            <el-input v-model="settings.outputDirectories.rawConfigs"></el-input>
          </el-form-item>
          <el-form-item label="Reports Directory">
            <el-input v-model="settings.outputDirectories.reports"></el-input>
          </el-form-item>
        </el-tab-pane>
      </el-tabs>

      <!-- Save Button -->
      <el-form-item style="text-align: center; margin-top: 20px;">
        <el-button type="primary" @click="saveSettings">Save Settings</el-button>
      </el-form-item>
    </el-form>
  </el-main>
</el-container>
  </el-container>

</template>

<script>

export default {

name: "Settings",

data() {

return {

activeMenu: "settings", // Default active sidebar menu item

activeTab: "connection", // Default active tab

settings: {

// Connection Settings based on Python settings.py

connectTimeout: 60,

commandTimeout: 120,

retryTimes: 3,

retryInterval: 10,

// Log Settings

enableConsoleOutput: true,

logDir: "logs",

logLevel: "INFO",

logFormat: "%(asctime)s - %(name)s - %(levelname)s - %(message)s",

// LangChain Settings

langchainVerbose: true,

langchainDebug: false,

// AI Settings (for deepseek)

aiSettings: {

apiBase: "https://dashscope.aliyuncs.com/compatible-mode/v1",

apiKey: "sk-82ab0776a4b54524a0f19d0f2d220324",

model: "qwen2.5-14b-instruct-1m"

},

// Output Directories

outputDirectories: {

rawConfigs: "raw_configs",

reports: "reports"

}

}

}

},

methods: {

// Navigation method to ensure consistent routing

navigate(page) {

if (page === "aiOps") {

this.$router.push({ name: "Home" });

} else if (page === "aiInspection") {

this.$router.push({ name: "InspectorDetail" });

} else if (page === "docs") {

this.$router.push({ name: "Docs" });

} else if (page === "settings") {

this.$router.push({ name: "Settings" });

}

},

// Save settings method (simulate saving to back-end)

saveSettings() {

this.$message({

message: "Settings have been saved successfully.",

type: "success"

});

console.log("Saved settings:", this.settings);

}

}

};

</script>

<style scoped>

.settings-container {

height: 100vh;

}

.sidebar {

background-color: #2f4050;

color: #fff;

}

.header {

background-color: #fff;

padding: 10px 20px;

display: flex;

align-items: center;

border-bottom: 1px solid #ebeef5;

}

.title {

font-size: 20px;

font-weight: bold;

}

.main-content {

padding: 20px;

background-color: #f0f2f5;

overflow-y: auto;

}

</style>