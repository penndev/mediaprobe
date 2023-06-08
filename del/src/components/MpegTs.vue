<template>
  <div>
    <a-card title="Hex Viewer" :body-style="{ padding: '0' }">
      <div class="hex-viewer">
        <div class="hex-header">
          <span v-for="byte in headerBytes" :key="byte" class="hex-cell">{{ byte }}</span>
        </div>
        <div class="hex-content">
          <div v-for="(row, rowIndex) in rows" :key="rowIndex" class="hex-row">
            <span class="row-index">{{ rowIndex }}</span>
            <span v-for="(byte, byteIndex) in row" :key="byteIndex" class="hex-cell">{{ byte }}</span>
          </div>
        </div>
      </div>
    </a-card>
  </div>
</template>

<script>
export default {
  data() {
    return {
      data: [0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1], // 16进制字节数据
      bytesPerRow: 16 // 每行字节数
    };
  },
  computed: {
    rows() {
      // 将字节数据按每行字节数拆分成多行
      const rows = [];
      for (let i = 0; i < this.data.length; i += this.bytesPerRow) {
        rows.push(this.data.slice(i, i + this.bytesPerRow));
      }
      return rows;
    },
    headerBytes() {
      // 表头的字节标识
      return Array.from(Array(this.bytesPerRow).keys()).map((_, index) => index.toString(16));
    }
  }
};
</script>

<style scoped>
.hex-viewer {
  display: flex;
  flex-direction: column;
}

.hex-header,
.hex-row {
  display: flex;
}

.hex-cell {
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid #ccc;
}

.hex-content {
  overflow: auto;
  max-height: 400px;
}

.row-index {
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid #ccc;
  font-weight: bold;
}
</style>


<!-- <template>
    <p>总分包大小 {{ packetTotal }}</p>
    
    <table>
      <tr>
        <td></td>
      </tr>
    </table>

    <pre>{{packetCurrentHex}}</pre>
    <h1>
        Heelo
    </h1>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps({
  file: File
})

const packetTotal = ref<Number>(0) 
const packetCurrentHex = ref<Uint8Array>()

if (props.file instanceof File){
    packetTotal.value = props.file.size / 188
    const hexDate = props.file.slice(0,188)
    
    hexDate.arrayBuffer().then(resule => {
        packetCurrentHex.value = new Uint8Array(resule) 
    })
}


function byteToHexString(byte: number) {
  return byte.toString(16).padStart(2, '0');
}

</script> -->