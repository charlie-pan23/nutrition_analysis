<template>
  <view class="container">
    <Nav :has-nav="false" title="" title-color="#444444"></Nav>
    <view :style="sysHeight.paddingHeight" class="content">
      <view class="card">
        <view class="name">{{ user.nickname }}</view>
        <view class="info">
          <view class="item">
            <text>年龄</text>
            <view class="start">
              <text style="margin-right: 20rpx">{{ user.age }}</text>
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>
          <view class="item">
            <text>性别</text>
            <view class="start">
              <text style="margin-right: 20rpx">{{ user.gender }}</text>
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>
          <view class="item">
            <text>体重</text>
            <view class="start">
              <picker @change="bindWeightChange" :value="user.weight-1" :range="weightList"
                      style="margin-right: 10rpx">
                <view class="uni-input">{{ user.weight }}</view>
              </picker>
              公斤
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>
          <view class="item">
            <text>身高</text>
            <view class="start">
              <picker @change="bindHeightChange" :value="user.height-100" :range="heightList"
                      style="margin-right: 10rpx">
                <view class="uni-input">{{ user.height }}</view>
              </picker>
              厘米
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>
          <view class="item" @click="onMultiplePick('preferences')">
            <text>偏好</text>
            <view class="start">
              <text style="margin-right: 20rpx">{{ user.preferences }}</text>
              <multiple-pick ref="preferencesRef" :list="preferencesPickList" disabled-key="disabled"
                             disabled-value="1" :defaults="[]" @confirm="onMultiplePickConfirm"
                             :max="10" max-message="已超出最大选项"></multiple-pick>
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>
          <view class="item" @click="onMultiplePick('diseases')">
            <text>慢性病</text>
            <view class="start">
              <text style="margin-right: 20rpx">{{ user.diseases }}</text>
              <multiple-pick ref="diseasesRef" :list="diseasesPickList" disabled-key="disabled"
                             disabled-value="1" :defaults="[]" @confirm="onMultiplePickConfirm"
                             :max="10" max-message="已超出最大选项"></multiple-pick>
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>
          <view class="item" @click="onMultiplePick('allergies')">
            <text>过敏源</text>
            <view class="start">
              <text style="margin-right: 20rpx">{{ user.allergies }}</text>
              <multiple-pick ref="allergiesRef" :list="allergiesPickList" disabled-key="disabled"
                             disabled-value="1" :defaults="[]" @confirm="onMultiplePickConfirm"
                             :max="10" max-message="已超出最大选项"></multiple-pick>
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>
        </view>
      </view>
    </view>
    <Tab :tab="3"/>
  </view>
</template>

<script setup>
import Nav from "@/components/nav.vue";
import Tab from "@/components/tabbar.vue";
import {onMounted} from "vue";
import {getUser} from "@/utils/store";
import http from "@/utils/http";
import MultiplePick from "@/components/multiple-pick.vue";

const {proxy} = getCurrentInstance()
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
const user = ref({
  height: 170,
  age: 18,
  gender: '男',
  preferences: 'Empty',
  allergies: 'Empty',
  diseases: 'Empty'
})

const allergiesPickList = ref(['海鲜', '牛奶', '鸡蛋', '花生', '坚果', '大豆'])
const diseasesPickList = ref(['高血压', '糖尿病', '心脏病', '高血脂', '高尿酸'])
const preferencesPickList = ref(['蔬菜', '肉类', '水果', '鱼类', '主食', '素食', '辣口', '咸口'])
onMounted(() => {
  user.value = getUser()
})
const multiplePickType = ref();
const onMultiplePick = (type) => {
  proxy.$refs[type + 'Ref'].show();
  multiplePickType.value = type
}

const onMultiplePickConfirm = async (selectedList) => {
  console.log(selectedList);
  let value = ''
  if (selectedList.length > 0) {
    value = selectedList.join(',')
  }
  await saveUserInfo(multiplePickType.value, value);
  proxy.$refs[multiplePickType.value + 'Ref'].close();
}


const weightList = Array.from({length: 200}, (_, i) => i + 1);

const heightList = Array.from({length: 100}).map((_, i) => i + 100);

const bindHeightChange = async (val) => {
  await saveUserInfo('height', Number(val.detail.value) + 100);
}

const bindWeightChange = async (val) => {
  await saveUserInfo('weight', Number(val.detail.value) + 1);
}


async function saveUserInfo(type, val) {
  const data = {}
  data[type] = val
  // 更新用户信息
  const resData = await http.put('/users/' + user.value.openid, data)
  user.value = resData
  uni.setStorageSync('user', resData)
}

const showActionSheet = (type) => {
  let itemList = []
  switch (type) {
    case 'height':
      itemList = heightList
      break;
    default:
      itemList = ['选项A', '选项B', '选项C']
      break;
  }

  uni.showActionSheet({
    itemList: itemList,
    success: async function (res) {
      console.log('用户选择了第' + res.tapIndex + '个选项');
      console.log(itemList[res.tapIndex])
      await saveUserInfo(type.value, itemList[res.tapIndex]);

    },
    fail: function (res) {
      console.log(res.errMsg);
    }
  });
}
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
  position: relative;
  display: flex;
  flex-direction: column;
  width: 710rpx;
  height: auto;
  margin: 16rpx auto;
  padding: 16rpx 0;
  box-sizing: border-box;
  border-radius: 8rpx;
  background: #FFFFFF;
  margin-top: 116rpx;

  .avatar {
    position: absolute;
    top: -100rpx;
    left: 305rpx;
    width: 100rpx;
    height: 100rpx;

    image {
      width: 100%;
      height: 100%;
      border-radius: 50%;
    }
  }

  .name {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100rpx;
    font-size: 30rpx;
    color: #444444;
    font-weight: 700;
    border-bottom: 1rpx solid #f1f1f1;
  }

  .info {
    display: flex;
    flex-direction: column;
    font-size: 26rpx;
    color: #444444;
    padding-bottom: 100rpx;
    box-sizing: border-box;

    .item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      height: 80rpx;
      border-bottom: 1rpx solid #f1f1f1;

      text {
        padding-left: 16rpx;
      }

      :deep(.u-icon) {
        display: flex;
        margin-left: auto;
        padding-right: 16rpx;
      }
    }
  }
}
</style>
