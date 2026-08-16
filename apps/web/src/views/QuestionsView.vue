<script setup lang="ts">
import { onMounted, ref } from 'vue'

import client from '../api/client'

interface Resource {
  id: number
  title: string
  category: string
  description: string
  created_at?: string
}

const keyword = ref('')
const page = ref(1)
const pageSize = 10
const total = ref(0)
const resources = ref<Resource[]>([])
const loading = ref(false)

async function fetchResources() {
  loading.value = true
  try {
    const { data } = await client.get('/resources', {
      params: { keyword: keyword.value, page: page.value },
    })
    resources.value = data.items ?? data
    total.value = data.total ?? resources.value.length
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  fetchResources()
}

function onPageChange(next: number) {
  page.value = next
  fetchResources()
}

function download(id: number) {
  window.open(`/api/resources/${id}/download`, '_blank')
}

onMounted(fetchResources)
</script>

<template>
  <section>
    <h2>试题库</h2>
    <div class="search-bar">
      <n-input
        v-model:value="keyword"
        placeholder="搜索试题"
        clearable
        @keyup.enter="onSearch"
      />
      <n-button type="primary" @click="onSearch">搜索</n-button>
    </div>

    <n-spin :show="loading">
      <n-empty v-if="!resources.length" description="暂无资源" />
      <div v-else class="resource-list">
        <n-card v-for="item in resources" :key="item.id" size="small">
          <div class="resource-row">
            <div class="resource-info">
              <div class="resource-title">
                {{ item.title }}
                <n-tag size="small">{{ item.category }}</n-tag>
              </div>
              <div class="resource-desc">{{ item.description }}</div>
            </div>
            <n-button size="small" type="primary" @click="download(item.id)">
              下载
            </n-button>
          </div>
        </n-card>
      </div>
    </n-spin>

    <div class="pagination">
      <n-pagination
        :page="page"
        :page-size="pageSize"
        :item-count="total"
        @update:page="onPageChange"
      />
    </div>
  </section>
</template>

<style scoped>
.search-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.resource-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.resource-title {
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.resource-desc {
  color: #777;
  font-size: 13px;
  margin-top: 4px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}
</style>
