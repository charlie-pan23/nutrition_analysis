<template>
  <el-dialog
      :visible.sync="dialogVisible"
      :z-index="3000"
      title="添加新用户"
      width="800px"
      @close="$emit('cancel')"
  >
    <el-form label-width="140px" :model="formData" size="large">
      <el-form-item label="用户名">
        <el-input size="large" v-model="formData.username" placeholder="输入用户名"></el-input>
      </el-form-item>
      <el-form-item label="年龄:">
        <my-slider v-model="formData.age"/>
      </el-form-item>
      <el-form-item label="身高 (cm)">
          <my-slider v-model="formData.height" :max="heightMax" :min="heightMin" :show-tooltip="false"/>
      </el-form-item>
      <el-form-item label="体重 (kg)">
        <my-slider v-model="formData.weight"/>
      </el-form-item>
      <el-form-item label="慢性病（可多选）">
        <div class="tag-selector start">
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
      </el-form-item>
      <el-form-item label="过敏原（可多选）">
        <div class="tag-selector start">
        <span
            v-for="avoidance in allergiesOptions"
            :key="avoidance.value"
            class="tag"
            :class="{ 'selected': formData.allergies.includes(avoidance.value) }"
            @click="toggleAvoidance(avoidance.value)"
        >
          {{ avoidance.label }}
        </span>
        </div>
      </el-form-item>
      <el-form-item label="饮食偏好（可多选）">
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
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="success" @click="$emit('cancel')">取消</el-button>
        <el-button type="primary" @click="submit">添加</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import {reactive, computed, ref} from 'vue'
import MySlider from "./MySlider.vue";

// 表单数据
const formData = reactive({
  username: '',
  age: 30,
  height: 170,
  weight: 60,
  conditions: [],
  allergies: [],
  preferences: []
})

// 选项配置
const conditionOptions = [
  {label: '高血压', value: 'hypertension'},
  {label: '糖尿病', value: 'diabetes'},
  {label: '心脏病', value: 'heart_disease'},
  {label: '高血脂', value: 'hyperlipidemia'},
  {label: '高尿酸', value: 'high_uric_acid'}
]

const allergiesOptions = [
  {label: '海鲜', value: 'seafood'},
  {label: '牛奶', value: 'milk'},
  {label: '鸡蛋', value: 'eggs'},
  {label: '花生', value: 'peanuts'},
  {label: '坚果', value: 'nuts'},
  {label: '大豆', value: 'soybeans'}
]

const preferenceOptions = [
  {label: '蔬菜', value: 'vegetables'},
  {label: '肉类', value: 'meat'},
  {label: '水果', value: 'fruits'},
  {label: '鱼类', value: 'fish'},
  {label: '主食', value: 'grains'},
  {label: '素食', value: 'vegetarian'},
  {label: '辣口', value: 'spicy'},
  {label: '咸口', value: 'salty'}
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
const toggleAvoidance = (value) => toggleSelection(formData.allergies, value)
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
    allergies: [...formData.allergies],
    preferences: [...formData.preferences]
  })
}

const heightMin = ref(100)
const heightMax = ref(200)
const style = computed(() => {
  const length = heightMax.value - heightMin.value,
      progress = formData.height - heightMin.value,
      left = (progress / length) * 100;
  return {
    paddingLeft: `${left}%`,
  };
})

</script>

<style scoped>

:deep(.el-form-item--large .el-form-item__content){
  line-height: 22px !important;
}
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
  width: 100%;
}

.tag {
  padding: 0.3rem 1rem;
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

.dialog-footer {

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

}

:deep(.el-form-item__content) {
  line-height: 1.5;
}

:deep(.el-form-item__label) {
  font-weight: bold;
}

/* 全局样式 */

body, html {
  /* 禁用文本选择 */
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;

  /* 禁用长按菜单 */
  -webkit-touch-callout: none;

  /* 优化滚动性能 */
  overscroll-behavior-y: contain; /* 防止滚动到顶部或底部时，触发整个页面的“橡皮筋”效果 */
}

</style>