<script setup lang="ts">
// Placeholder download entries; files are served as static assets under /software/.
const packages = [
  { name: 'Windows 版', file: '/software/solotalk-windows.zip' },
  { name: 'macOS 版', file: '/software/solotalk-macos.dmg' },
  { name: 'Android 版', file: '/software/solotalk-android.apk' },
]
</script>

<template>
  <section>
    <h2>软件下载</h2>
    <div class="cards">
      <n-card v-for="pkg in packages" :key="pkg.name" :title="pkg.name">
        <n-button tag="a" :href="pkg.file" type="primary" download>下载</n-button>
      </n-card>
    </div>
  </section>
</template>

<style scoped>
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
</style>
