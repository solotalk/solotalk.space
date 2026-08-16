<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'

import client from '../api/client'

const router = useRouter()
const message = useMessage()

const title = ref('')
const category = ref('')
const description = ref('')
const file = ref<File | null>(null)
const submitting = ref(false)

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  file.value = input.files?.[0] ?? null
}

async function submit() {
  if (!title.value || !category.value || !file.value) {
    message.warning('请填写标题、分类并选择文件')
    return
  }
  submitting.value = true
  try {
    const form = new FormData()
    form.append('file', file.value)
    form.append('title', title.value)
    form.append('category', category.value)
    form.append('description', description.value)
    await client.post('/resources', form)
    message.success('上传成功，等待审核')
    router.push('/questions')
  } catch {
    message.error('上传失败')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section>
    <h2>上传资源</h2>
    <n-form label-placement="top" style="max-width: 480px">
      <n-form-item label="标题">
        <n-input v-model:value="title" />
      </n-form-item>
      <n-form-item label="分类">
        <n-input v-model:value="category" />
      </n-form-item>
      <n-form-item label="描述">
        <n-input v-model:value="description" type="textarea" :rows="3" />
      </n-form-item>
      <n-form-item label="文件">
        <input type="file" @change="onFileChange" />
      </n-form-item>
      <n-button type="primary" :loading="submitting" @click="submit">提交</n-button>
    </n-form>
  </section>
</template>
