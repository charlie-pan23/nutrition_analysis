<template>
  <div class="test-view">
    <el-main>
      <el-row>
        <el-col :span="24">
          <el-row class="main-card" :gutter="15">
            <el-col :span="11">
              <el-card hadow="never">
                <template #header>
                  <div>
                    <span>相机画面</span>
                  </div>
                </template>
                <img :src="videoUrl" alt="实时摄像头" class="camera-feed">
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card hadow="never">
                <template #header>
                  <div>
                    <span>实时分析</span>
                  </div>
                </template>
                <el-scrollbar :wrap-style="{ overflowX: 'auto' }" style="width: 100%">
                  <!-- 添加动画效果 -->
                  <el-table
                      :data="foodData"
                      height="400px"
                      stripe
                      :show-header="true"
                      border
                  >
                    <el-table-column prop="name" fixed="left" label="食物" width="100px">
                      <template #default="{ row }">
                        <span style="font-weight: bold">{{ row.name }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="weight" label="重量" align="center" width="80px/"/>
                    <el-table-column prop="calories" label="热量" align="center" width="90px"/>
                    <el-table-column prop="protein" label="蛋白质(g)" align="center" width="100px"/>
                    <el-table-column prop="fat" label="脂肪(g)" align="center" width="100px"/>
                    <el-table-column prop="carbohydrate" label="碳水化合物(g)" align="center" width="120px"/>
                  </el-table>

                  <div v-if="detectionData.length === 0" class="empty-result">
                    <el-empty description="暂无检测结果"/>
                  </div>
                </el-scrollbar>
              </el-card>
            </el-col>
            <el-col :span="5">
              <el-card hadow="never" class="third">
                <template #header>
                  <div>
                    <el-select
                        v-model="selectedMealType"
                        placeholder="选择餐食类型"
                        size="large"
                        @change="handleMealTypeChange"
                    >
                      <el-option
                          v-for="item in mealTypeOptions"
                          :key="item.value"
                          :label="item.label"
                          :value="item.value"
                      />
                    </el-select>
                  </div>
                </template>
                <el-scrollbar height="400px">
                  <div v-if="mealDetail">
                    <!-- 显示餐食详情 -->
                    <div class="meal-detail">
                      <h3 style="margin-top: 0; margin-bottom: 10px;">{{ mealDetail.meal_type }} -
                        {{ mealDetail.formatted_time }}</h3>
                      <el-descriptions border :column="1">
                        <el-descriptions-item label="总热量">{{ mealDetail.total.calories }} kcal</el-descriptions-item>
                        <el-descriptions-item label="蛋白质">{{ mealDetail.total.protein }} g</el-descriptions-item>
                        <el-descriptions-item label="脂肪">{{ mealDetail.total.fat }} g</el-descriptions-item>
                        <el-descriptions-item label="碳水化合物">{{ mealDetail.total.carbohydrates }} g
                        </el-descriptions-item>
                      </el-descriptions>

                      <h4 style="margin-top: 5px; margin-bottom: 5px;">包含食物：</h4>
                      <ul class="food-list">
                        <li v-for="(food, index) in mealDetail.foods" :key="index">
                          {{ food.name }} -
                          热量: {{ food.calories }}kcal,
                          蛋白质: {{ food.protein }}g,
                          脂肪: {{ food.fat }}g,
                          碳水: {{ food.carbohydrates }}g
                        </li>
                      </ul>
                    </div>
                  </div>
                </el-scrollbar>
              </el-card>
            </el-col>
          </el-row>
        </el-col>

        <el-col :span="24" class="operate-card" style="margin-top: 20px; ">
          <el-row :gutter="15">
            <el-col :span="11">
              <div style="background-color: #FFF; border-radius: 5px;height: 150px;" class="column">
                <div style="font-size: 32px; font-weight: bolder;color: #606266;padding: 10px; width: 100%"
                     class="center">
                  <span>总重量</span>
                </div>
                <div style="font-size: 24px; width: 100%;" class="center">
                  <p class="weight-value">{{ currentWeight }}<span class="unit">g</span></p>
                  <!--                  <span>13.145千克</span>-->
                </div>
              </div>
            </el-col>
            <el-col :span="4">
              <el-button type="success" class="btn" @click="analysis">分析</el-button>
            </el-col>
            <el-col :span="4">
              <el-button type="warning" class="btn" @click="recordMeal">记录</el-button>
            </el-col>
            <el-col :span="5">
              <div style="background-color: #FFF; border-radius: 5px;height: 150px;" class="column">
                <div style="width: 100%; padding: 0px;">
                  <AudioRecorder/>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-col>
      </el-row>

      <el-dialog
          v-model="dialogVisible"
          title="分析结果"
          width="800"
          center
          :header-style="{
        fontSize: '24px',
        fontWeight: 'bold',
        color: '#606266',
        textAlign: 'center'
        }"
      >

        <el-scrollbar height="400px">
          <div style="font-size: 16px; font-weight: bolder; color: #606266; padding: 10px; text-align: center">
            数据采集
          </div>
          <div
              v-for="(item, index) in foodData"
              :key="index"
              class="report" style="flex-direction: column; align-items: flex-start; padding: 15px;"
          >
            <el-row>
              <el-col :span="12">
                <div style="display: flex; width: 100%; margin-bottom: 20px;">
                  <span style="width: 200px; font-weight: bold;">食物：</span>
                  <span style="width: 200px">{{ item.name }}</span>
                </div>
              </el-col>
              <el-col :span="12">
                <div style="display: flex; width: 100%; margin-bottom: 20px;">
                  <span style="width: 200px; font-weight: bold;">重量：</span>
                  <span style="width: 200px">{{ item.weight }}</span>
                </div>
              </el-col>
            </el-row>
            <el-row>
              <el-col :span="12">
                <div style="display: flex; width: 100%; margin-bottom: 20px;">
                  <span style="width: 200px; font-weight: bold;">热量：</span>
                  <span style="width: 200px">{{ item.calories }}</span>
                </div>
              </el-col>
              <el-col :span="12">
                <div style="display: flex; width: 100%; margin-bottom: 20px;">
                  <span style="width: 200px; font-weight: bold;">蛋白质：</span>
                  <span style="width: 200px">{{ item.protein }}</span>
                </div>
              </el-col>
            </el-row>

            <el-row>
              <el-col :span="12">
                <div style="display: flex; width: 100%; margin-bottom: 20px;">
                  <span style="width: 200px; font-weight: bold;">脂肪：</span>
                  <span style="width: 200px">{{ item.fat }}</span>
                </div>
              </el-col>
              <el-col :span="12">
                <div style="display: flex; width: 100%; margin-bottom: 20px;">
                  <span style="width: 200px; font-weight: bold;">碳水化合物：</span>
                  <span style="width: 200px">{{ item.carbohydrate }}</span>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-scrollbar>

        <template #footer>
          <div class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="dialogVisible = false">
              确定
            </el-button>
          </div>
        </template>
      </el-dialog>
    </el-main>
  </div>
</template>


<script setup>
import axios from 'axios';
import {ref, onMounted, onBeforeUnmount} from "vue";
import {useRouter} from 'vue-router';
import io from 'socket.io-client';
import {ElMessage} from 'element-plus';
import AudioRecorder from '../components/AudioRecorder.vue'

const router = useRouter();
const currentWeight = ref(0);
const weightInterval = ref(null);
const dialogVisible = ref(false);

const isRecording = ref(false);
const recorder = ref(null);
const recordTime = ref(0);
const loading = ref(false);

// 检测数据 - 用于el-table展示
const detectionData = ref([]);

// const socket = io('ws://localhost:7777', {
//   reconnection: true,
//   reconnectionAttempts: 5,
//   reconnectionDelay: 1000
// });

// 监听检测结果更新
// socket.on('detection_update', (data) => {
//   // 更新检测数据 - 格式为数组对象 [{label, count}]
//   detectionData.value = data.results.map(item => ({
//     label: item.label,
//     count: item.count
//   }));
// });

const meals = ref([]);
const selectedMeal = ref('');
const selectedMealType = ref('');
const mealTypeOptions = ref([
  {label: '早饭', value: 'Breakfast'},
  {label: '午饭', value: 'Lunch'},
  {label: '晚饭', value: 'Dinner'},
  {label: '夜宵', value: 'Supper'},
  {label: '加餐', value: 'Extra'}
]);
const mealDetail = ref()
const mealDetailData = {
  'Dinner': {
    meal_type: '晚餐',
    formatted_time: '2025年06月15日 18:40',
    total: {
      calories: 436,
      protein: 29,
      fat: 22,
      carbohydrates: 35
    },
    foods: [
      {
        name: "三文鱼",
        calories: 206,
        protein: 22,
        fat: 13,
        carbohydrates: 0
      },
      {
        name: "土豆泥",
        calories: 150,
        protein: 4,
        fat: 5,
        carbohydrates: 25
      },
      {
        name: "蔬菜沙拉",
        calories: 80,
        protein: 3,
        fat: 4,
        carbohydrates: 10
      }
    ]
  }
};
const videoUrl = ref("")
const refreshVideoStream = () => {
  const timestamp = new Date().getTime()
  videoUrl.value = `http://localhost:5000/video_feed?_=${timestamp}`
}

// 获取重量定时器
const startWeightUpdates = async () => {
  const response = axios.get('/api/weight').then(response => {
    console.log(response.data.weight.toFixed(1))
    currentWeight.value = response.data.weight.toFixed(1)
  })


  // weightInterval.value = setInterval(async () => {
  //   try {
  //
  //     currentWeight.value = response.data.weight.toFixed(1)
  //   } catch (error) {
  //     console.error('获取重量失败:', error)
  //   }
  // }, 1000)


}

const foodData = ref([
  {
    name: '鸡蛋',
    weight: '86g',
    calories: '87kcal',
    protein: '8.1g',
    fat: '5.3g',
    carbohydrate: '1.6g'
  }
])
const handleMealTypeChange = (mealType) => {
  console.log(mealDetailData[mealType])
  mealDetail.value = mealDetailData[mealType]
}
// 记录餐食
const recordMeal = async () => {
  if (!selectedMealType.value) {
    ElMessage.warning('请选择餐食类型');
    return;
  }

  try {
    // 将检测到的食物列表发送到后端
    const detectedFoods = detectionData.value.map(item => ({
      name: item.label,
      count: item.count
    }))

    const response = await axios.post('/api/record-meal', {
      weight: currentWeight.value,
      mealType: selectedMealType.value,
      foods: detectedFoods  // 发送检测到的食物列表
    });

    ElMessage.success('餐食记录成功');
    await fetchMeals();
    selectedMeal.value = response.data.meal_name;
    await loadMealDetail();
  } catch (error) {
    console.error('记录餐食失败:', error);
    ElMessage.error('记录餐食失败');
  }
};

// 获取餐食列表
const fetchMeals = async () => {
  try {
    const response = await axios.get('/api/user-meals');
    meals.value = response.data.meals;
  } catch (error) {
    console.error('获取餐食列表失败:', error);
  }
};

// 加载餐食详情
const loadMealDetail = async () => {
  if (!selectedMeal.value) {
    mealDetail.value = null;
    return;
  }

  try {
    const response = await axios.get(`/api/meal-detail/${selectedMeal.value}`);
    mealDetail.value = response.data;
  } catch (error) {
    console.error('获取餐食详情失败:', error);
    mealDetail.value = null;
  }
};

// 分析按钮
const analysis = () => {
  dialogVisible.value = true;
};

// 登出
const logout = async () => {
  try {
    await axios.get('/api/logout')
    router.push('/standby')
  } catch (error) {
    console.error('退出登录失败:', error)
  }
}

onMounted(() => {
  refreshVideoStream()


  setInterval(async () => {
    console.log('获取重量')
    startWeightUpdates()
  }, 500)
  // socket.connect()
  fetchMeals(); // 加载餐食列表
})

onBeforeUnmount(() => {
  clearInterval(weightInterval.value)
  // socket.disconnect()
})
</script>

<style>
.third {
  .el-card__header {
    padding: 10px 20px 10px 20px !important;
  }

  .el-select {
    width: 100%;
  }
}
</style>
<style scoped>
.main-card {
  height: 500px;

  div, .el-card {
    height: 100%;
  }
}

.operate-card {
  height: 150px;

  .el-card {
    height: 100%;
  }
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.video-error {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fef0f0;
}


.btn {
  margin-top: 10px;
  width: 100%;
  height: 120px;
  font-size: 40px;
  font-weight: bolder;
  border-radius: 20px;
}

.btn.is-recording {
  background-color: #dc3545;
  border-color: #dc3545;
}

.flip-list-move {
  transition: transform 0.5s ease;
}

.detection-item {
  margin-bottom: 10px;
  transition: all 0.5s;
}

.report {
  display: flex;
  margin: 10px;
  border-radius: 4px;
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

@keyframes slide-up {
  0% {
    transform: translateY(20px);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

.detection-item {
  animation: slide-up 0.5s ease;
}

.empty-result {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.meal-detail {
  padding: 10px;
}

.food-list {
  list-style-type: none;
  padding: 0;
  margin-top: 0px;
}

.food-list li {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
  font-size: 13px;
}

.detection-table .el-table__row {
  transition: all 0.5s ease;
}

/* 新行进入动画 */
.detection-table .el-table__row-enter-active {
  animation: slide-up 0.5s ease;
}

/* 定义动画 */
@keyframes slide-up {
  0% {
    transform: translateY(20px);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 空结果样式 */
.empty-result {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

</style>