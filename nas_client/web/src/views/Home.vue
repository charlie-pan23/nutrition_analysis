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
                      <h4 style="margin-top: 0; margin-bottom: 10px;">
                        {{ mealDetail.formatted_time }}
                      </h4>
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
                          碳水: {{ food.carbs }}g
                        </li>
                      </ul>
                    </div>
                  </div>
                  <div v-else class="empty-result">
                    <el-empty description="暂无数据"/>
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
              <el-button type="warning" class="btn" @click="record">记录</el-button>
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
          <div style="font-size: 40rpx; font-weight: bolder;margin-bottom: 20rpx;color: #C64E0B;">医生建议：</div>
          <div v-html="doctor()"></div>
          <div style="font-size: 40rpx; font-weight: bolder;margin-bottom: 20rpx;color: #C64E0B;margin-top: 20rpx;">
            菜谱推荐：
          </div>
          <div v-html="food()"></div>
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
import {ElLoading, ElMessage} from 'element-plus';
import AudioRecorder from '../components/AudioRecorder.vue'
import {marked} from "marked";

const router = useRouter();
const currentWeight = ref(0);
const weightInterval = ref(null);
const dialogVisible = ref(false);

const isRecording = ref(false);
const recorder = ref(null);
const recordTime = ref(0);
const loading = ref(false);

const foodRes = ref(undefined)
const doctorRes = ref(undefined)
// 检测数据 - 用于el-table展示
const detectionData = ref([]);


const doctor = () => {
  return marked(foodRes.value);
}
const food = () => {
  return marked(doctorRes.value);
}


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
const selectedMeal = ref(null);
const selectedMealType = ref(null);
const mealTypeOptions = ref([
  {label: '早饭', value: '1'},// breakfast
  {label: '午饭', value: '2'},// lunch
  {label: '晚饭', value: '3'},// dinner
  {label: '夜宵', value: '4'},// super
  {label: '加餐', value: '5'} // extra
]);
const mealDetail = ref()

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


const foodData = ref(null);

const fetchDetections = async () => {
  try {
    const response = await axios.post('http://172.20.10.3:5000/get_detections_json');
    if (response.code === 200) {
      foodData.value = response.data
    } else {
      foodData.value = null
    }
    // 如果为空，则保留原数据不变
  } catch (error) {
    console.error('获取检测数据失败:', error);
    // 请求失败也保持原数据不变
  }
};

const record = () => {
  if (!foodData.value) {
    return uni.showToast({title: '暂无记录，请确认', icon: 'none', duration: 2000})
  }
  const params = foodData.value
  params['user_openid'] = getOpenId()
  const res = http.post("http://172.20.10.3:5000/records", params)

  if (res.code === 200) {
    return uni.showToast({title: '记录成功', icon: 'success', duration: 2000})
  }
}

// const foodData = ref([
//   {
//     name: '鸡蛋',
//     weight: '86g',
//     calories: '87kcal',
//     protein: '8.1g',
//     fat: '5.3g',
//     carbohydrate: '1.6g'
//   }
// ])
const handleMealTypeChange = async (mealType) => {
  console.log(mealType)
  await fetchMeals()
}
// 获取餐食列表
const fetchMeals = async () => {
  if (!selectedMealType.value) {
    mealDetail.value = null;
    return ElMessage.warning('请选择餐食类型');

  }// 从下拉菜单获取餐食类型
  try {
    const res = await axios.get(`http://172.20.10.3:5000/records/meal-detail/oJ2D36yAHQ1-RsKpSEH8Sf01HZwA/${selectedMealType.value}`);
    console.log(res)
    if (res.data.code !== 200) {
      mealDetail.value = null;
      return ElMessage.warning(res.data.message);
    }
    console.log(res.data.data)
    mealDetail.value = res.data.data;
  } catch (error) {
    console.error('获取餐食列表失败:', error);
  }
};



// 分析按钮
const analysis = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: '分析中,请耐心等待...',
    background: 'rgba(0, 0, 0, 0.7)',
  })
  try {
    const instance = axios.create({
      timeout: 50000 // 10秒超时
    });
    const res = await instance.get("http://172.20.10.3:5000/analysis")
    console.log(res.data)
    loading.close()
    if (res.data.code !== 200) {
      return ElMessage.error(res.message);
    }
    foodRes.value = res.data.data.food
    doctorRes.value = res.data.data.doctor
    dialogVisible.value = true;
  } catch (e) {
    console.log(e)
    loading.close()
    return ElMessage.error('网络异常，请稍后再试');
  }
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
  // setInterval(fetchDetections, 2000);

  // setInterval(async () => {
  //   console.log('获取重量')
  //   startWeightUpdates()
  // }, 5000)
  // socket.connect()
  // fetchMeals(); // 加载餐食列表
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