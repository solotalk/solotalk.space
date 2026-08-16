<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router'

import { authState, logout } from './stores/auth'

const router = useRouter()

function onLogout() {
  logout()
  router.push('/')
}
</script>

<template>
  <n-message-provider>
    <div class="app-shell">
      <header class="top-nav">
        <RouterLink to="/" class="brand">Solotalk Space</RouterLink>
        <nav class="nav-links">
          <RouterLink to="/">首页</RouterLink>
          <RouterLink to="/download">下载</RouterLink>
          <RouterLink to="/questions">试题库</RouterLink>
          <RouterLink to="/upload">上传</RouterLink>
          <RouterLink v-if="authState.isAdmin" to="/admin">审核</RouterLink>
        </nav>
        <div class="nav-auth">
          <template v-if="authState.accessToken">
            <span class="username">{{ authState.username }}</span>
            <n-button size="small" quaternary @click="onLogout">退出</n-button>
          </template>
          <template v-else>
            <RouterLink to="/login">登录</RouterLink>
            <RouterLink to="/register">注册</RouterLink>
          </template>
        </div>
      </header>
      <main class="app-main">
        <RouterView />
      </main>
    </div>
  </n-message-provider>
</template>

<style>
body {
  margin: 0;
  font-family:
    -apple-system, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #f7f8fa;
}

.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.top-nav {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 0 24px;
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #eee;
}

.brand {
  font-size: 18px;
  font-weight: 600;
  color: #18a058;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 16px;
  flex: 1;
}

.nav-links a,
.nav-auth a {
  color: #333;
  text-decoration: none;
}

.nav-links a.router-link-active {
  color: #18a058;
  font-weight: 600;
}

.nav-auth {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  color: #555;
}

.app-main {
  flex: 1;
  width: 100%;
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 16px;
  box-sizing: border-box;
}
</style>
