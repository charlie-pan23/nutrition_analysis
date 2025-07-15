<template>
  <el-dialog
      :visible.sync="dialogVisible"
      :z-index="3000"
      title="添加新用户"
      width="800px"
      @close="$emit('cancel')"
  >
    <div class="add-user-form">
      <h2>添加新用户</h2>

      <!-- 用户名 -->
      <div class="form-group">
        <label for="newUserName">用户名:</label>
        <input
            type="text"
            id="newUserName"
            v-model="formData.username"
            required
            placeholder="输入用户名"
        />
      </div>

      <!-- 年龄 -->
      <div class="form-group">
        <label>年龄: {{ formData.age }}</label>
        <input
            type="range"
            v-model="formData.age"
            min="0"
            max="120"
            class="custom-slider"
        />
        <div class="slider-value">{{ formData.age }}</div>
      </div>

      <!-- 身高 -->
      <div class="form-group">
        <label>身高 (cm): {{ formData.height }}</label>
        <input
            type="range"
            v-model="formData.height"
            min="50"
            max="250"
            class="custom-slider"
        />
        <div class="slider-value">{{ formData.height }}</div>
      </div>

      <!-- 体重 -->
      <div class="form-group">
        <label>体重 (kg): {{ formData.weight }}</label>
        <input
            type="range"
            v-model="formData.weight"
            min="20"
            max="300"
            class="custom-slider"
        />
        <div class="slider-value">{{ formData.weight }}</div>
      </div>

      <!-- 慢性病 -->
      <div class="form-group">
        <label>慢性病（可多选）:</label>
        <div class="tag-selector">
        <span
            v-for="condition in conditionOptions"
            :key="condition.value"
            class="tag"
            :class="{ 'selected': formData.conditions.includes(condition.value) }"
            @click="toggleCondition(condition.value)"
        >
          {{ condition.label }}
        </span>
        </div>
      </div>

      <!-- 忌口 -->
      <div class="form-group">
        <label>忌口（可多选）:</label>
        <div class="tag-selector">
        <span
            v-for="avoidance in avoidanceOptions"
            :key="avoidance.value"
            class="tag"
            :class="{ 'selected': formData.avoidances.includes(avoidance.value) }"
            @click="toggleAvoidance(avoidance.value)"
        >
          {{ avoidance.label }}
        </span>
        </div>
      </div>

      <!-- 偏好 -->
      <div class="form-group">
        <label>饮食偏好（可多选）:</label>
        <div class="tag-selector">
        <span
            v-for="preference in preferenceOptions"
            :key="preference.value"
            class="tag"
            :class="{ 'selected': formData.preferences.includes(preference.value) }"
            @click="togglePreference(preference.value)"
        >
          {{ preference.label }}
        </span>
        </div>
      </div>

      <!-- 提交按钮 -->
      <div class="form-actions">
        <el-button type="success" @click="$emit('cancel')">取消</el-button>
        <el-button type="primary" @click="submit">添加</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { reactive, computed } from 'vue'

// 表单数据
const formData = reactive({
  username: '',
  age: 30,
  height: 170,
  weight: 60,
  conditions: [],
  avoidances: [],
  preferences: []
})

// 选项配置
const conditionOptions = [
  { label: '高血压', value: 'hypertension' },
  { label: '糖尿病', value: 'diabetes' },
  { label: '心脏病', value: 'heart_disease' },
  { label: '脂肪肝', value: 'fatty_liver' },
  { label: '高血脂', value: 'hyperlipidemia' }
]

const avoidanceOptions = [
  { label: '海鲜', value: 'seafood' },
  { label: '牛奶', value: 'milk' },
  { label: '鸡蛋', value: 'eggs' },
  { label: '花生', value: 'peanuts' },
  { label: '辛辣', value: 'spicy' },
  { label: '生冷', value: 'cold' }
]

const preferenceOptions = [
  { label: '蔬菜', value: 'vegetables' },
  { label: '肉类', value: 'meat' },
  { label: '水果', value: 'fruits' },
  { label: '鱼类', value: 'fish' },
  { label: '主食', value: 'grains' },
  { label: '素食', value: 'vegetarian' }
]

const props = defineProps({
  visible: Boolean
})

const emit = defineEmits(['cancel', 'submit'])

// 对话框显示控制
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => {
    if (!value) {
      emit('cancel')
    }
  }
})

// 切换选择状态的方法
const toggleSelection = (array, value) => {
  const index = array.indexOf(value)
  if (index > -1) {
    array.splice(index, 1)
  } else {
    array.push(value)
  }
}

const toggleCondition = (value) => toggleSelection(formData.conditions, value)
const toggleAvoidance = (value) => toggleSelection(formData.avoidances, value)
const togglePreference = (value) => toggleSelection(formData.preferences, value)

// 提交表单
const submit = () => {
  if (!formData.username.trim()) {
    alert('用户名不能为空')
    return
  }

  emit('submit', {
    ...formData,
    conditions: [...formData.conditions],
    avoidances: [...formData.avoidances],
    preferences: [...formData.preferences]
  })
}
</script>

<style scoped>
.add-user-form {
  padding: 10px;
}

h2 {
  text-align: center;
  margin-bottom: 1rem;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

label {
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #555;
}

input[type="text"] {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
}

.custom-slider {
  width: 100%;
  margin-top: 0.5rem;
  height: 8px;
  border-radius: 4px;
  background: #e0e0e0;
  outline: none;
  -webkit-appearance: none;
}

.custom-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #4CAF50;
  cursor: pointer;
}

.slider-value {
  align-self: flex-end;
  font-size: 0.9rem;
  color: #666;
  margin-top: 0.3rem;
}

.tag-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
  width: 100%;
}

.tag {
  padding: 0.5rem 1rem;
  background-color: #f0f0f0;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
  border: 1px solid #ddd;
}

.tag:hover {
  background-color: #e0e0e0;
}

.tag.selected {
  background-color: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 10px;
}

button {
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:first-child {
  background-color: #f5f5f5;
  color: #000;
}

button:first-child:hover {
  background-color: #e0e0e0;
}

button:last-child {
  background-color: #4CAF50;
  color: white;
}

button:last-child:hover {
  background-color: #388e3c;
}
</style>