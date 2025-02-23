<template>
<el-container class="home-container">
<!-- 左侧边栏部分，保持和 InspectorDetail.vue 一致 -->
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
  <!-- 右侧主要内容区域 -->
<el-container>
  <!-- 头部：标题及右上角的开关 -->
  <el-header class="header">
    <div class="title">AI OPS</div>
    <el-switch
      v-model="terminalOn"
      active-text="Terminal On"
      inactive-text="Terminal Off"
      active-color="#0078d4"
      @change="handleSwitchChange">
    </el-switch>
  </el-header>

  <!-- 主体区域 -->
  <el-main class="main-content">
    <!-- 当终端面板开启时，聊天区与终端区并排显示，各占 1:1 -->
    <div class="content" v-if="terminalOn">
      <div class="panel chat-area">
        <div class="chat-history">
          <div
            v-for="(msg, index) in chatHistory"
            :key="index"
            class="chat-message">
            <span :class="msg.sender === 'user' ? 'user-msg' : 'ai-msg'">
              {{ msg.sender === 'user' ? '我：' : 'AI：' }} {{ msg.content }}
            </span>
          </div>
        </div>
        <div class="chat-input">
          <input
            type="text"
            v-model="userInput"
            placeholder="请输入消息，回车发送"
            @keyup.enter="sendMessage" />
          <button @click="sendMessage">发送</button>
        </div>
      </div>
      <div class="panel terminal-pane">
        <pre class="terminal-output">
          <span v-for="(line, idx) in terminalContent" :key="idx">{{ line }}</span>
</pre>
</div>
</div>
<!-- 当终端面板关闭时，仅显示聊天区，独占全宽 -->
<div class="content" v-else>
<div class="panel chat-area full">
<div class="chat-history">
<div v-for="(msg, index) in chatHistory" :key="index" class="chat-message">
<span :class="msg.sender === 'user' ? 'user-msg' : 'ai-msg'">
{{ msg.sender === 'user' ? '我：' : 'AI：' }} {{ msg.content }}
</span>
</div>
</div>
<div class="chat-input">
<input
type="text"
v-model="userInput"
placeholder="请输入消息，回车发送"
@keyup.enter="sendMessage" />
<button @click="sendMessage">发送</button>
</div>
</div>
</div>
</el-main>
</el-container>
</el-container>
</template>

<script>

export default {

name: "Home",

data() {

return {

activeMenu: "aiOps",

terminalOn: false,

userInput: "",

chatHistory: [],

terminalContent: [

"Terminal 输出区域内容..."

]

};

},

methods: {

navigate(page) {

this.activeMenu = page;

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

handleSwitchChange(value) {

console.log("Terminal 开关状态：", value);

},

sendMessage() {

const content = this.userInput.trim();

if (!content) return;

this.chatHistory.push({ sender: "user", content });

this.userInput = "";

// 模拟 AI 回复，可替换成后端接口调用

setTimeout(() => {

this.chatHistory.push({ sender: "ai", content: `回复: ${content}` });

}, 500);

}

}

};

</script>

<style scoped>

.home-container {

height: 100vh;

}

/* 左侧边栏 */

.sidebar {

background-color: #2f4050;

color: #fff;

}

/* 头部 */

.header {

background-color: #fff;

padding: 10px 20px;

border-bottom: 1px solid #ebeef5;

display: flex;

justify-content: space-between;

align-items: center;

}

.title {

font-size: 20px;

font-weight: bold;

}

/* 主内容区 */

.main-content {

padding: 20px;

background-color: #f0f2f5;

overflow: auto;

}

/* 内容区域：当终端开启时，两部分并排显示 */

.content {

display: flex;

gap: 10px;

height: calc(100vh - 80px - 40px); /* 根据 header 及其它内边距调整 */

}

/* 通用面板样式 */

.panel {

flex: 1;

display: flex;

flex-direction: column;

border: 1px solid #ccc;

border-radius: 4px;

padding: 10px;

overflow: hidden;

}

/* 聊天区 */

.chat-area {

background-color: #fff;

}

.chat-history {

flex: 1;

overflow-y: auto;

margin-bottom: 10px;

}

.chat-message {

margin-bottom: 8px;

}

.user-msg {

color: #0078d4;

}

.ai-msg {

color: #008000;

}

.chat-input {

display: flex;

}

.chat-input input {

flex: 1;

padding: 8px;

border: 1px solid #ccc;

border-radius: 4px;

}

.chat-input button {

margin-left: 10px;

padding: 8px 12px;

background-color: #0078d4;

color: #fff;

border: none;

border-radius: 4px;

cursor: pointer;

}

/* Terminal 面板 */

.terminal-pane {

background-color: #000;

color: #0f0;

}

.terminal-output {

font-family: monospace;

white-space: pre-wrap;

overflow-y: auto;

height: 100%;

}

/* 当终端关闭时，聊天区全宽 */

.chat-area.full {

flex: 1;

}

</style>