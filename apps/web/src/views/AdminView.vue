<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'

import client from '../api/client'
import { formatFileSize, PLATFORM_OPTIONS, type Software } from '../types/software'

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

// --- Software management ---

const softwareList = ref<Software[]>([])
const softwareLoading = ref(false)

const uploadForm = ref({
  name: '',
  version: '',
  platform: 'Windows',
  description: '',
})
const uploadFile = ref<File | null>(null)
const uploading = ref(false)

const editVisible = ref(false)
const editSaving = ref(false)
const editForm = ref({
  id: 0,
  name: '',
  version: '',
  platform: 'Windows',
  description: '',
})

async function fetchSoftware() {
  softwareLoading.value = true
  try {
    const { data } = await client.get('/admin/software')
    softwareList.value = data.items ?? data
  } finally {
    softwareLoading.value = false
  }
}

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  uploadFile.value = input.files?.[0] ?? null
}

async function uploadSoftware() {
  if (!uploadFile.value) {
    message.warning('请选择文件')
    return
  }
  if (!uploadForm.value.name || !uploadForm.value.version) {
    message.warning('请填写名称和版本')
    return
  }
  const formData = new FormData()
  formData.append('file', uploadFile.value)
  formData.append('name', uploadForm.value.name)
  formData.append('version', uploadForm.value.version)
  formData.append('platform', uploadForm.value.platform)
  if (uploadForm.value.description) {
    formData.append('description', uploadForm.value.description)
  }
  uploading.value = true
  try {
    await client.post('/admin/software', formData)
    message.success('上传成功')
    uploadForm.value = { name: '', version: '', platform: 'Windows', description: '' }
    uploadFile.value = null
    fetchSoftware()
  } catch {
    message.error('上传失败')
  } finally {
    uploading.value = false
  }
}

async function toggleActive(item: Software) {
  try {
    await client.patch(`/admin/software/${item.id}`, { is_active: !item.is_active })
    message.success('操作成功')
    fetchSoftware()
  } catch {
    message.error('操作失败')
  }
}

function openEdit(item: Software) {
  editForm.value = {
    id: item.id,
    name: item.name,
    version: item.version,
    platform: item.platform,
    description: item.description ?? '',
  }
  editVisible.value = true
}

async function saveEdit() {
  editSaving.value = true
  try {
    const { id, ...payload } = editForm.value
    await client.patch(`/admin/software/${id}`, payload)
    message.success('保存成功')
    editVisible.value = false
    fetchSoftware()
  } catch {
    message.error('保存失败')
  } finally {
    editSaving.value = false
  }
}

async function removeSoftware(id: number) {
  try {
    await client.delete(`/admin/software/${id}`)
    message.success('删除成功')
    fetchSoftware()
  } catch {
    message.error('删除失败')
  }
}

onMounted(() => {
  fetchResources()
  fetchSoftware()
})
</script>

<template>
  <section>
    <n-tabs type="line">
      <n-tab-pane name="resources" tab="资源审核">
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
      </n-tab-pane>

      <n-tab-pane name="software" tab="软件管理">
        <n-card size="small" title="上传软件" class="upload-card">
          <n-form label-placement="left" label-width="60px">
            <n-form-item label="名称">
              <n-input v-model:value="uploadForm.name" />
            </n-form-item>
            <n-form-item label="版本">
              <n-input v-model:value="uploadForm.version" />
            </n-form-item>
            <n-form-item label="平台">
              <n-select
                v-model:value="uploadForm.platform"
                :options="PLATFORM_OPTIONS"
              />
            </n-form-item>
            <n-form-item label="描述">
              <n-input v-model:value="uploadForm.description" type="textarea" />
            </n-form-item>
            <n-form-item label="文件">
              <input type="file" @change="onFileChange" />
            </n-form-item>
            <n-button type="primary" :loading="uploading" @click="uploadSoftware">
              上传
            </n-button>
          </n-form>
        </n-card>

        <n-spin :show="softwareLoading">
          <n-empty v-if="!softwareList.length" description="暂无软件" />
          <table v-else class="resource-table">
            <thead>
              <tr>
                <th>名称</th>
                <th>版本</th>
                <th>平台</th>
                <th>大小</th>
                <th>下载次数</th>
                <th>状态</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in softwareList" :key="item.id">
                <td>{{ item.name }}</td>
                <td>{{ item.version }}</td>
                <td>{{ item.platform }}</td>
                <td>{{ formatFileSize(item.file_size) }}</td>
                <td>{{ item.download_count }}</td>
                <td>
                  <n-tag size="small" :type="item.is_active ? 'success' : 'default'">
                    {{ item.is_active ? '启用' : '禁用' }}
                  </n-tag>
                </td>
                <td>{{ item.created_at }}</td>
                <td class="actions">
                  <n-button size="tiny" @click="toggleActive(item)">
                    {{ item.is_active ? '禁用' : '启用' }}
                  </n-button>
                  <n-button size="tiny" type="primary" @click="openEdit(item)">
                    编辑
                  </n-button>
                  <n-popconfirm @positive-click="removeSoftware(item.id)">
                    <template #trigger>
                      <n-button size="tiny" type="error">删除</n-button>
                    </template>
                    确认删除？
                  </n-popconfirm>
                </td>
              </tr>
            </tbody>
          </table>
        </n-spin>
      </n-tab-pane>
    </n-tabs>

    <n-modal v-model:show="editVisible" preset="card" title="编辑软件" style="width: 480px">
      <n-form label-placement="left" label-width="60px">
        <n-form-item label="名称">
          <n-input v-model:value="editForm.name" />
        </n-form-item>
        <n-form-item label="版本">
          <n-input v-model:value="editForm.version" />
        </n-form-item>
        <n-form-item label="平台">
          <n-select v-model:value="editForm.platform" :options="PLATFORM_OPTIONS" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="editForm.description" type="textarea" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-button type="primary" :loading="editSaving" @click="saveEdit">保存</n-button>
      </template>
    </n-modal>
  </section>
</template>

<style scoped>
.filter-bar {
  margin-bottom: 16px;
}

.upload-card {
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
