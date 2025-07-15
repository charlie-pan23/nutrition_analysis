<template>
    <view class="container">
        <Nav :has-nav="false" title="" title-color="#444444"></Nav>
        <!--        <view :style="sysHeight.headerHeight" class="header"></view>-->
        <view :style="sysHeight.paddingHeight" class="content">
            <view class="date" @click="showDate = true">
                <text>{{ currentDate }}</text>
                <up-icon name="arrow-down" color="#333333" size="20"></up-icon>
            </view>
            <up-datetime-picker
                    :closeOnClickOverlay="true"
                    :show="showDate"
                    v-model="dateValue"
                    @close="showDate = false"
                    @cancel="showDate = false"
                    @confirm="confirmDate($event)"
                    mode="date"
            ></up-datetime-picker>
            <view class="main">
                <view class="charts">
                    <qiun-data-charts
                        type="arcbar"
                        :opts="opts"
                        :chartData="chartData"
                        :canvas2d="true"
                        canvasId="PwUnmYfWUCHcDrUkAlAicICFNeEIaVNY"
                    />
                </view>
                <view class="card">
                    <view class="card_intro" v-for="(item, index) in list" :key="index">
                        <view class="title cate">
                            <text>{{ item.cate }}</text>
                        </view>
                        <template v-for="(attr, aIndex) in item.attr" :key="aIndex">
                            <view class="title">
                                <text>{{ attr.name }}</text>
                            </view>
                            <template v-for="(key, kIndex) in attr.item" :key="kIndex">
                                <view class="attr">
                                    <view class="attr_item">
                                        <text>{{ key.k }}</text>
                                        <text>{{ key.v }}</text>
                                    </view>
                                </view>
                            </template>
                        </template>
                    </view>
                </view>
            </view>
            <view style="height: 160rpx"></view>
            <Tab :tab="1" />
        </view>
    </view>
</template>

<script setup>
import Nav from "@/components/nav.vue";
import Tab from "@/components/tabbar.vue";

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

const currentDate = ref('请选择日期')
const dateValue = ref(Date.now())
const showDate = ref(false)

const list = ref([
    {
        cate: '早餐',
        attr: [
            {
                name: '鸡蛋',
                item: [
                    {
                        k: '热量',
                        v: '203kj'
                    },
                    {
                        k: '碳水',
                        v: '11g'
                    },
                    {
                        k: '脂肪',
                        v: '5g'
                    }
                ]
            },
            {
                name: '面包',
                item: [
                    {
                        k: '热量',
                        v: '100kj'
                    },
                    {
                        k: '碳水',
                        v: '20g'
                    },
                    {
                        k: '脂肪',
                        v: '3g'
                    }
                ]
            }
        ]
    },
    {
        cate: '午餐',
        attr: [
            {
                name: '汉堡',
                item: [
                    {
                        k: '热量',
                        v: '3000kj'
                    },
                    {
                        k: '碳水',
                        v: '50g'
                    },
                    {
                        k: '脂肪',
                        v: '45g'
                    }
                ]
            },
            {
                name: '可乐',
                item: [
                    {
                        k: '热量',
                        v: '100kj'
                    },
                    {
                        k: '碳水',
                        v: '30g'
                    },
                    {
                        k: '脂肪',
                        v: '0g'
                    }
                ]
            }
        ]
    },
    {
        cate: '晚餐',
        attr: [
            {
                name: '鱼',
                item: [
                    {
                        k: '热量',
                        v: '150kj'
                    },
                    {
                        k: '碳水',
                        v: '11g'
                    },
                    {
                        k: '脂肪',
                        v: '5g'
                    }
                ]
            },
            {
                name: '米饭',
                item: [
                    {
                        k: '热量',
                        v: '100kj'
                    },
                    {
                        k: '碳水',
                        v: '0g'
                    },
                    {
                        k: '脂肪',
                        v: '3g'
                    }
                ]
            }
        ]
    }
])
const chartData = ref({})

const opts =  ref({
    color: ["#1890FF","#91CB74","#FAC858","#EE6666","#73C0DE","#3CA272","#FC8452","#9A60B4","#ea7ccc"],
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

onMounted(() => {
    getServerData()
})

const getServerData = () => {
    //模拟从服务器获取数据时的延时
    setTimeout(() => {
        //模拟服务器返回数据，如果数据格式和标准格式不同，需自行按下面的格式拼接
        let res = {
            series: [
                {
                    name: "能量",
                    data: 0.8
                },
                {
                    name: "碳水",
                    data: 0.6
                },
                {
                    name: "蛋白质",
                    data: 0.45
                },
                {
                    name: "脂肪",
                    data: 0.3
                }
            ]
        };
        chartData.value = JSON.parse(JSON.stringify(res));
    }, 500);
}

const confirmDate = (e) => {
    dateValue.value = e.value
    showDate.value = false
    currentDate.value = timestampToFormattedDate(e.value)
}

function timestampToFormattedDate(timestamp) {
    const date = new Date(timestamp)
    return `${date.getFullYear()}-${('0' + (date.getMonth() + 1)).slice(-2)}-${('0' + date.getDate()).slice(-2)}`
}
</script>

<style lang="scss" scoped>
.container {
  width: 100vw;
  height: auto;
  min-height: 100vh;
  background: linear-gradient(180deg, #EEC6AF 0%, #F6F6F6 100%);
}
.header {
  position: fixed;
  top: 0;
  width: 100vw;
  background: linear-gradient(180deg, #EEC6AF 0%, #F6F6F6 100%);
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
  z-index: 2;
}

.date {
  display: flex;
  align-items: center;
  width: 710rpx;
  height: 60rpx;
  margin: 16rpx auto;
  border-radius: 8rpx;
  border: 1rpx solid #EEC6AF;
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
</style>
