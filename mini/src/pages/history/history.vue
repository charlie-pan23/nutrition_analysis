<template>
  <view class="container">
    <Nav :has-nav="false" title="" title-color="#444444"></Nav>
    <!--        <view :style="sysHeight.headerHeight" class="header"></view>-->
    <view :style="sysHeight.paddingHeight" class="content">
      <view class="date" @click="showDate = true">
        <text>{{ currentDate }}</text>
        <up-icon color="#333333" name="arrow-down" size="20"></up-icon>
      </view>
      <up-datetime-picker
          v-model="dateValue"
          :closeOnClickOverlay="true"
          :show="showDate"
          mode="date"
          @cancel="showDate = false"
          @close="showDate = false"
          @confirm="confirmDate($event)"
      ></up-datetime-picker>
      <view class="main">
        <view class="charts">
          <qiun-data-charts
              :canvas2d="true"
              :chartData="chartData"
              :opts="opts"
              canvasId="PwUnmYfWUCHcDrUkAlAicICFNeEIaVNY"
              type="arcbar"
          />
        </view>
        <view class="card">
          <view class="card">
            <view v-for="n in 5" v-if="Object.keys(mealData).length > 0" class="card_intro">
              <template v-if="mealData[n] ">
                <view class="title cate">
                  <text>{{ mealTypeEnum[n] }}</text>
                </view>
                <template v-for="(attr, aIndex) in mealData[n]" :key="aIndex">
                  <view class="title">
                    <text>{{ attr.notes }}</text>
                  </view>
                  <template>
                    <view class="attr">
                      <view class="attr_item">
                        <text>热量</text>
                        <text>{{ attr.calories }}</text>
                      </view>
                    </view>
                    <view class="attr">
                      <view class="attr_item">
                        <text>碳水</text>
                        <text>{{ attr.carbs }}</text>
                      </view>
                    </view>
                    <view class="attr">
                      <view class="attr_item">
                        <text>脂肪</text>
                        <text>{{ attr.fat }}</text>
                      </view>
                    </view>
                    <view class="attr">
                      <view class="attr_item">
                        <text>蛋白质</text>
                        <text>{{ attr.protein }}</text>
                      </view>
                    </view>

                  </template>
                </template>
              </template>
            </view>
            <view v-else>
              <view class="data-empty">
                <text>暂无数据</text>
              </view>
            </view>
          </view>
        </view>
        <view style="height: 160rpx"></view>

      </view>
    </view>
    <Tab :tab="1"/>
  </view>
</template>

<script setup>
import Nav from "@/components/nav.vue";
import Tab from "@/components/tabbar.vue";
import http from "@/utils/http";
import {getOpenId} from "@/utils/store";
import {mealTypeEnum} from "@/utils";

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

const currentDate = ref(timestampToFormattedDate(new Date()))
const dateValue = ref(Date.now())
const showDate = ref(false)

const mealData = ref([])
const chartData = ref({})


onMounted(async () => {
  await getCal()
  await getDetail()
})

const getCal = async () => {
  const openid = getOpenId()
  const res = await http.get(`/records/daily_summary/${openid}/${currentDate.value}`)
  chartData.value = getChartData(res.total_calories, res.total_carbs, res.total_protein, res.total_fat)
}


const getDetail = async () => {
  const openid = getOpenId()
  const res = await http.get(`/records/daily/${openid}/${currentDate.value}`)


  const groupedData = res.reduce((acc, item) => {
    const key = item.meal_type_id;
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(item);
    return acc;
  }, {});

  console.log(JSON.stringify(groupedData))

  mealData.value = groupedData
}


const getChartData = (energy_kcal, carbohydrates, protein, fat) => {
  let res = {
    series: [
      {
        name: "能量",
        data: energy_kcal
      },
      {
        name: "碳水",
        data: carbohydrates
      },
      {
        name: "脂肪",
        data: fat
      },
      {
        name: "蛋白质",
        data: protein
      }
    ]
  };
  return JSON.parse(JSON.stringify(res));
}

// {"energy_kcal":19, "carbohydrates":19, "protein":19, "fat":19}


const confirmDate = async (e) => {
  dateValue.value = e.value
  showDate.value = false
  currentDate.value = timestampToFormattedDate(new Date(e.value))
  await getCal()
  await getDetail()
}

function timestampToFormattedDate(date) {
  return `${date.getFullYear()}-${('0' + (date.getMonth() + 1)).slice(-2)}-${('0' + date.getDate()).slice(-2)}`
}

const opts = ref({
  color: ["#EE6666", "#91CB74", "#FAC858", "#1890FF", "#73C0DE", "#3CA272", "#FC8452", "#9A60B4", "#ea7ccc"],
  padding: undefined,
  title: {
    name: "营养摄入",
    fontSize: 16,
    color: "#1890ff"
  },
  subtitle: {
    name: "单位:g",
    fontSize: 12,
    color: "#666666"
  },
  extra: {
    arcbar: {
      type: "circle",
      width: 12,
      backgroundColor: "#E9E9E9",
      startAngle: 1.5,
      endAngle: 0.25,
      gap: 2
    }
  }
})
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

.wrap {
  width: 100vw;
  z-index: 2;
}

.content {
  position: relative;
  //width: 710rpx;
  width: 100vw;
  height: auto;
  //margin: 0 20rpx;
}

.date {
  display: flex;
  align-items: center;
  width: 710rpx;
  height: 60rpx;
  margin: 16rpx auto;
  border-radius: 8rpx;
  border: 1rpx solid #03ca6d;
  padding: 0 16rpx;
  box-sizing: border-box;

  text {
    display: flex;
    align-items: center;
    height: 100%;
    color: #333333;
    font-size: 26rpx;
  }

  :deep(.u-icon) {
    display: flex;
    margin-left: auto;
  }
}

.main {
  width: 710rpx;
  height: auto;
  margin: 0 auto;
  padding: 16rpx;
  box-sizing: border-box;
  border-radius: 8rpx;
  background: #FFFFFF;

  .charts {
    width: 100%;
    height: 400rpx;
  }

  .card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 680rpx;
    border: 1rpx solid #f1f1f1;

    &_intro {
      display: flex;
      flex-direction: column;
      width: 100%;
      font-size: 26rpx;
      color: #444444;

      .title {
        display: flex;
        align-items: center;
        width: 100%;
        height: 80rpx;
        border-bottom: 1rpx solid #f2f2f2;

        text {
          padding-left: 24rpx;
          box-sizing: border-box;
        }
      }

      .cate {
        font-size: 28rpx;
        font-weight: 700;
      }

      .attr {
        display: flex;
        flex-direction: column;
        width: 100%;

        &_item {
          display: flex;
          align-items: center;
          width: 100%;
          height: 70rpx;
          border-bottom: 1rpx solid #f2f2f2;
          //&:last-child {
          //    border: none;
          //}
          text {
            display: flex;
            align-items: center;
            height: 100%;

            &:first-child {
              width: 280rpx;
              padding-left: 100rpx;
              box-sizing: border-box;
            }
          }
        }
      }
    }
  }
}

.data-empty {
  margin-top: 220rpx;
}

</style>
