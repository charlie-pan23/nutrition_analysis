<template>
  <view class="container">
    <Nav :has-nav="false" title="" title-color="#444444"></Nav>
    <view :style="sysHeight.paddingHeight" class="content">
      <view class="card c1">
        <view class="card-title">实时画面</view>
        <view class="camera-container">
          <img :src="videoUrl" alt="实时摄像头" class="camera-feed"/>
        </view>
      </view>
      <view class="card c2">
        <view class="title">实时分析</view>
        <!-- 表格容器 -->
        <view class="table-container">
          <!-- 滚动区域 + 数据行 -->
          <scroll-view v-if="foodData" scroll-x="true" @scroll="scroll">
            <view class="table-header">
              <view class="table-cell">食物名称</view>
              <view class="table-cell">重量/g</view>
              <view class="table-cell">热量/kcal</view>
              <view class="table-cell">蛋白质/g</view>
              <view class="table-cell">脂肪/g</view>
              <view class="table-cell">碳水化合物/g</view>
            </view>
            <view class="table-row">
              <view class="table-cell">{{ foodData.name }}</view>
              <view class="table-cell">{{ foodData.amount }}</view>
              <view class="table-cell">{{ foodData.calories }}</view>
              <view class="table-cell">{{ foodData.protein }}</view>
              <view class="table-cell">{{ foodData.fat }}</view>
              <view class="table-cell">{{ foodData.carbs }}</view>
            </view>
          </scroll-view>
          <!-- 空状态 -->
          <view v-else class="empty-result">
            暂无检测结果
          </view>
        </view>
      </view>
      <view class="control">
        <view class="item btn success" @click="analysis">分析</view>
        <view class="item btn warning" @click="record">记录</view>
      </view>
    </view>
    <view v-if="showModal" class="modal-container">
      <view class="modal-content">
        <view class="center">
          <span style="font-size: 50rpx; padding: 20rpx;font-weight: bolder;margin-bottom: 20rpx;">分析结果</span>
        </view>
        <view class="rich-text-container">
          <scroll-view class="scroll-view" scroll-y="true">
            <view style="font-size: 40rpx; font-weight: bolder;margin-bottom: 20rpx;color: #C64E0B;">医生建议：</view>
            <rich-text :nodes="doctor()"></rich-text>
            <view style="font-size: 40rpx; font-weight: bolder;margin-bottom: 20rpx;color: #C64E0B;margin-top: 20rpx;">
              菜谱推荐：
            </view>
            <rich-text :nodes="food()"></rich-text>
          </scroll-view>
        </view>
        <view class="end">
          <view class="close-btn" @click="closeModal">关闭</view>
        </view>
      </view>
    </view>
    <Tab :tab="2"/>
  </view>
</template>

<script setup>
import Nav from "@/components/nav.vue";
import Tab from "@/components/tabbar.vue";
import {onMounted, ref} from 'vue';
import http from "@/utils/http";
import {getOpenId} from "@/utils/store";
import {marked} from "marked";

const foodRes = ref(undefined)
const doctorRes = ref(undefined)
const doctor = () => {
  return marked(doctorRes.value);
}
const food = () => {
  return marked(foodRes.value);
}
//
// const htmlContent = ref("### 1. 当前摄入是否合理\n" +
//     "\n" +
//     "- **能量**：当前摄入为980.0 kcal，目标为2200.0 kcal，明显低于目标。这表明您的能量摄入不足，可能会导致能量不足和身体机能受影响。\n" +
//     "- **碳水化合物**：当前摄入105.0 g，目标为250.0 g，碳水化合物摄入适中，但考虑到您的饮食偏好（低碳），可在合理范围内稍微调整。\n" +
//     "- **脂肪**：当前摄入32.0 g，目标为70.0 g，脂肪摄入较低，尤其是在高血压的饮食中，适量的健康脂肪是必要的。\n" +
//     "- **蛋白质**：当前摄入65.0 g，目标为150.0 g，蛋白质摄入明显不足，建议增加。\n" +
//     "\n" +
//     "### 2. 结合慢性病判断当前摄入是否存在风险\n" +
//     "\n" +
//     "您的慢性病是高血压，饮食应控制钠盐摄入并增加钾、钙、镁和膳食纤维。虽然当前的钠盐摄入未提供，但建议您务必保持在5g以下。由于您当前的能量和蛋白质摄入不足，可能导致身体缺乏必要的营养素，影响血压控制及整体健康。低脂肪的饮食可能导致饥饿感，进而影响饮食规律。\n" +
//     "\n" +
//     "### 3. 下一餐或接下来一天的饮食建议\n" +
//     "\n" +
//     "- **增加能量摄入**：在接下来的饮食中，应增加健康的碳水化合物来源，如全谷物、蔬菜和豆类，以提高能量摄入。\n" +
//     "- **增加蛋白质**：建议在下一餐中加入瘦肉、禽肉或鱼类，确保蛋白质的摄入量达到目标。\n" +
//     "- **健康脂肪**：可以适量增加橄榄油或菜籽油的使用，以补充健康脂肪。\n" +
//     "- **确保钠盐控制**：选择新鲜食材，避免加工食品，同时使用草药和香料替代盐调味。\n" +
//     "- **蔬菜和水果**：多摄入深色蔬菜（如菠菜、西兰花）和富含钾的水果（如香蕉、橙子），以帮助维持血压稳定。\n" +
//     "\n" +
//     "请根据以上建议调整您的饮食，并定期监测体重和血压，保持良好的饮食习惯。")
const showModal = ref(false)
const sysHeight = computed(() => {
  const info = uni.getStorageSync('systemInfo')
  let statusBarHeight = info.statusBarHeight * info.proportion
  let navigationBarHeight = info.navigationBarHeight * info.proportion
  return {
    headerHeight: 'height: ' + (statusBarHeight + navigationBarHeight + 144) + 'rpx',
    topHeight: 'top: ' + info.custom.top + 'px',
    btnHeight: 'height: ' + (info.custom.height * info.proportion) + 'rpx',
    paddingHeight: 'padding-top: ' + (statusBarHeight + navigationBarHeight + 20) + 'rpx'
  }
})
const openModal = () => {
  showModal.value = true;
}
const closeModal = () => {
  showModal.value = false;
}
const videoUrl = ref("");
const refreshVideoStream = () => {
  const timestamp = new Date().getTime();
  videoUrl.value = `http://172.20.10.11:5000/video_feed?_=${timestamp}`;
};

const foodData = ref(null);

const fetchDetections = async () => {
  try {
    const response = await http.post('http://172.20.10.3:5000/get_detections_json');
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

const analysis = async () => {
  await uni.showLoading({title: '分析中,请耐心等待…'})
  try {
    const res = await http.get("/analysis")
    uni.hideLoading()
    if (res.code !== 200) {
      return uni.showToast({title: res.message, icon: 'none', duration: 2000})
    }
    foodRes.value = res.data.food
    doctorRes.value = res.data.doctor
    openModal()
  } catch (e) {
    uni.hideLoading()
    return uni.showToast({title: '网络异常，请稍后再试', icon: 'none', duration: 1000})
  }

}
const record = async () => {
  if (!foodData.value) {
    return uni.showToast({title: '暂无记录，请确认', icon: 'none', duration: 2000})
  }
  const params = foodData.value

  params['user_openid'] = getOpenId()
  const res = await http.post("/records", params)

  if (res.code === 200) {
    return uni.showToast({title: '记录成功', icon: 'success', duration: 2000})
  }
}
onMounted(() => {
  refreshVideoStream();
  setInterval(fetchDetections, 2000);
});

</script>

<style lang="scss" scoped>
.container {
  width: 100vw;
  height: auto;
  min-height: 100vh;
  background: linear-gradient(180deg, #03ca6d 0%, #F6F6F6 100%);
}

.header {
  position: fixed;
  top: 0;
  width: 100vw;
  background: linear-gradient(180deg, #03ca6d 0%, #F6F6F6 100%);
}

.content {
  position: relative;
  width: 710rpx;
  height: auto;
  margin: 0 20rpx;
  z-index: 2;
}

.card {
  display: flex;
  flex-direction: column;
  width: 710rpx;
  height: auto;
  margin: 16rpx auto;
  padding: 16rpx;
  box-sizing: border-box;
  border-radius: 8rpx;
  background: #FFFFFF;

  .title {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 80rpx;
  }
}

.c1 {
  height: 30vh;
}

.c2 {
  height: 25vh;
}

.control {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin: 32rpx 0;

  .item {
    display: flex;
    color: #444444;
    font-size: 40rpx;
    border: 1rpx solid #03ca6d;
  }

  .btn {
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 320rpx;
    height: 100rpx;

    letter-spacing: 8rpx;
    border-radius: 8rpx;
  }

  .success {
    background: #409eff;
    border-color: #409eff;
  }

  .warning {
    background: #e6a23c;
    border-color: #e6a23c;
  }

  .circle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 130rpx;
    height: 130rpx;
    border-radius: 50%;
  }
}

.card-title {
  text-align: center;
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin: 16rpx 0 8rpx 16rpx;
}

.camera-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.table-container {
  padding: 16rpx;
}

.table-header,
.table-row {
  display: flex;
  justify-content: space-between;
  border-bottom: 1rpx solid #eee;
  font-size: 24rpx;
  color: #666;
}

.table-header {
  font-weight: bold;
  color: #333;
  background-color: #f9f9f9;
}

.table-cell {
  flex: 1;
  text-align: center;
  padding: 12rpx 0;
  min-width: 150rpx;
}

.empty-result {
  text-align: center;
  padding: 40rpx;
  color: #999;
}

.loading-text {
  text-align: center;
  padding: 20rpx;
  color: #999;
}


.modal-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 5px;
  margin: 30rpx;
}

.rich-text-container {
  width: 100%; /* 或者具体的宽度值 */
  height: 1000rpx; /* 或者具体的高度值 */
  overflow: hidden; /* 防止内容溢出 */
}

.scroll-view {
  width: 100%; /* 与容器宽度相同 */
  height: 100%; /* 与容器高度相同 */
}

.close-btn {
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 120rpx;
  height: 50rpx;
  margin-top: 20rpx;
  font-size: 26rpx;
  letter-spacing: 8rpx;
  border-radius: 8rpx;
  background: #409eff;
  border-color: #409eff;
}
</style>
