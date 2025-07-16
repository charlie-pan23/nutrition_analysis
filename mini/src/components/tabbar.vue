<template>
    <view class="tabbar">
        <view class="bar-top">
            <view class="menu m1">
                <image src="/static/tab/index-a.png" v-if="tab === 1" />
                <image src="/static/tab/index.png" v-else @click="checkPage(1)" />
                <text :class="{ 'active' : tab === 1 }">历史</text>
            </view>
            <view class="menu m3">
                <image src="/static/tab/home-a.svg" v-if="tab === 2" />
                <image src="/static/tab/home.svg" v-else @click="checkPage(2)" />
            </view>
            <view class="menu m2">
                <image src="/static/tab/user-a.png" v-if="tab === 3" />
                <image src="/static/tab/user.png" v-else @click="checkPage(3)" />
                <text :class="{ 'active' : tab === 3 }">我的</text>
            </view>
        </view>
    </view>
</template>

<script setup>
const props = defineProps({
    tab: {type: [String,Number], default: () => 1}
})

const checkPage = (index) => {
    let path = ''
    if (index === 1) {
        path = '/pages/history/history'
    } else if (index === 2) {
        path = '/pages/index/index'
    } else {
        path = '/pages/mine/mine'
    }
    uni.redirectTo({
        url: path
    })
}
</script>

<style lang="scss" scoped>
.tabbar {
  position: fixed;
  bottom: 0;
  width: 100vw;
  height: 170rpx;
  background: transparent;
  .bar-top {
    display: flex;
    margin-top: 40rpx;
    position: relative;
    width: 100%;
    height: 130rpx;
    z-index: -1;
    &:after {
      position: absolute;
      content: '';
      width: 100%;
      height: 130rpx;
      bottom: 0;
      z-index: -1;
      border-radius: 80% 80% 0 0;
      background: #03ca6d;
    }
    .menu {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      width: 33.33%;
      font-size: 26rpx;
      color: #333333;
      box-sizing: border-box;

      image {
        display: flex;
        width: 60rpx;
        height: 60rpx;
      }
      text {
        display: flex;
        margin-top: 8rpx;
      }
        .active {
            color: #C64E0B;
        }
    }

    .m1 {
      padding-left: 100rpx;
    }

    .m2 {
      padding-right: 100rpx;
    }

    .m3 {
      position: relative;
      image {
        position: absolute;
        top: -40rpx;
        width: 120rpx;
        height: 120rpx;
      }
    }
  }
}
</style>
