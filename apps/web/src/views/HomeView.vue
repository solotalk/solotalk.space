<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <section class="hero">
    <h1>Solotalk Space</h1>
    <p>试题分享与下载</p>
    <div class="actions">
      <n-button type="primary" size="large" @click="router.push('/questions')">
        进入试题库
      </n-button>
      <n-button size="large" @click="router.push('/download')">软件下载</n-button>
    </div>
  </section>
</template>

<style scoped>
.hero {
  text-align: center;
  padding: 96px 16px;
}

.hero h1 {
  margin: 0 0 12px;
  font-size: 40px;
}

.hero p {
  margin: 0 0 32px;
  color: #666;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}
</style>
