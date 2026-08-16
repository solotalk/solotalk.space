<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'

import client from '../api/client'

interface AdminResource {
  id: number
  title: string
  category: string
  description: string
  status: string
  username?: string
  created_at?: string
}

const STATUS_OPTIONS = [
  { label: '待审核', value: 'pending' },
  { label: '已发布', value: 'published' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已封禁', value: 'banned' },
]

const message = useMessage()

const status = ref('pending')
const resources = ref<AdminResource[]>([])
const loading = ref(false)

async function fetchResources() {
  loading.value = true
  try {
    const { data } = await client.get('/admin/resources', {
      params: { status: status.value },
    })
    resources.value = data.items ?? data
  } finally {
    loading.value = false
  }
}

async function moderate(id: number, action: 'approve' | 'reject' | 'ban') {
  try {
    await client.post(`/admin/resources/${id}/${action}`)
    message.success('操作成功')
    fetchResources()
  } catch {
    message.error('操作失败')
  }
}

onMounted(fetchResources)
</script>

<template>
  <section>
    <h2>资源审核</h2>
    <div class="filter-bar">
      <n-select
        v-model:value="status"
        :options="STATUS_OPTIONS"
        style="width: 160px"
        @update:value="fetchResources"
      />
    </div>

    <n-spin :show="loading">
      <n-empty v-if="!resources.length" description="暂无资源" />
      <table v-else class="resource-table">
        <thead>
          <tr>
            <th>标题</th>
            <th>分类</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in resources" :key="item.id">
            <td>{{ item.title }}</td>
            <td>{{ item.category }}</td>
            <td>{{ item.status }}</td>
            <td class="actions">
              <n-button
                size="tiny"
                type="primary"
                @click="moderate(item.id, 'approve')"
              >
                通过
              </n-button>
              <n-button
                size="tiny"
                type="warning"
                @click="moderate(item.id, 'reject')"
              >
                拒绝
              </n-button>
              <n-button
                size="tiny"
                type="error"
                @click="moderate(item.id, 'ban')"
              >
                封禁
              </n-button>
            </td>
          </tr>
        </tbody>
      </table>
    </n-spin>
  </section>
</template>

<style scoped>
.filter-bar {
  margin-bottom: 16px;
}

.resource-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
}

.resource-table th,
.resource-table td {
  padding: 8px 12px;
  border: 1px solid #eee;
  text-align: left;
}

.actions {
  display: flex;
  gap: 8px;
}
</style>
