<script setup lang="ts">
import { onMounted, ref } from 'vue'

import client from '../api/client'
import { formatFileSize, type Software } from '../types/software'

const items = ref<Software[]>([])
const loading = ref(false)

async function fetchSoftware() {
  loading.value = true
  try {
    const { data } = await client.get('/software')
    items.value = data.items ?? data
  } finally {
    loading.value = false
  }
}

function download(id: number) {
  window.open(`/api/software/${id}/download`, '_blank')
}

onMounted(fetchSoftware)
</script>

<template>
  <section>
    <h2>下载</h2>
    <n-spin :show="loading">
      <n-empty v-if="!items.length" description="暂无可用下载" />
      <div v-else class="cards">
        <n-card v-for="item in items" :key="item.id" :title="item.name">
          <div class="meta">
            <n-tag size="small">{{ item.platform }}</n-tag>
            <span>v{{ item.version }}</span>
            <span>{{ formatFileSize(item.file_size) }}</span>
            <span>{{ item.download_count }} 次下载</span>
          </div>
          <p v-if="item.description" class="desc">{{ item.description }}</p>
          <n-button type="primary" @click="download(item.id)">下载</n-button>
        </n-card>
      </div>
    </n-spin>
  </section>
</template>

<style scoped>
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  color: #777;
  font-size: 13px;
}

.desc {
  color: #777;
  font-size: 13px;
  margin: 8px 0;
}
</style>
