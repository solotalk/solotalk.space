<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'

import { login } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const username = ref('')
const password = ref('')
const submitting = ref(false)

async function submit() {
  if (!username.value || !password.value) {
    message.warning('请输入用户名和密码')
    return
  }
  submitting.value = true
  try {
    await login(username.value, password.value)
    router.push((route.query.redirect as string) || '/')
  } catch {
    message.error('登录失败')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <n-card title="登录" style="max-width: 360px; margin: 48px auto">
      <n-form label-placement="top">
        <n-form-item label="用户名">
          <n-input v-model:value="username" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input
            v-model:value="password"
            type="password"
            show-password-on="click"
            @keyup.enter="submit"
          />
        </n-form-item>
        <n-button type="primary" block :loading="submitting" @click="submit">
          登录
        </n-button>
      </n-form>
    </n-card>
  </section>
</template>
