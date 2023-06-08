<template>
  <template v-if="file == null">
    <a-upload-dragger :customRequest="handleRequest" :maxCount="1" :showUploadList="false">
      <p class="ant-upload-drag-icon">
        <inbox-outlined></inbox-outlined>
      </p>
      <p class="ant-upload-text">点击选择或拖拽文件分析</p>
      <p class="ant-upload-hint">
        &nbsp; 点击选择文件进行分析，或者拖拽文件进入本区域 支持上传媒体文件类型 *.ts *.flv *.mp4 &nbsp;
      </p>
    </a-upload-dragger>
  </template>
  <template v-else>
    <mpeg-ts :file="file"></mpeg-ts>
  </template>
</template>

<script setup lang="ts">
import { InboxOutlined } from '@ant-design/icons-vue'
import MpegTs from './components/MpegTs.vue'

import { UploadRequestOption } from 'ant-design-vue/lib/vc-upload/interface'
import { ref, Ref } from 'vue'

const file: Ref<File | null> = ref(null)

const handleRequest = (options: UploadRequestOption) => {
  console.log(options.file)
  file.value = options.file as File
}

</script>

