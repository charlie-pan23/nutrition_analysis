<template>
    <view class="top-main-box">
        <view :style="sysHeight.statusBarHeight" class=""></view>
        <view :style="sysHeight.navigationBarHeight" class="top-main-bar">
            <view v-if="props.hasNav" class="nav-back" @click="navBack">
                <image src="../../static/nav-back.png"/>
            </view>
            <view :style="sysHeight.navigationBarTitle" class="name">
                <view style="position:absolute; left: 0;top:0">
                    <slot name="left"></slot>
                </view>
                {{ props.title }}
            </view>
        </view>
    </view>
</template>

<script setup>
const props = defineProps({
    hasNav: {type: Boolean, default: () => true},
    title: {type: String, default: () => ''},
    titleColor: {type: String, default: () => '#FFFFFF'}
})

const sysHeight = computed(() => {
    const info = uni.getStorageSync('systemInfo')
    return {
        navigationBarHeight: 'height:' + (info.custom.height * info.proportion) + 'rpx',
        statusBarHeight: 'height:' + info.custom.top + 'px',
        navigationBarTitle: 'color:' + props.titleColor
    }
})

const navBack = () => {
    uni.navigateBack()
}
</script>

<style lang="scss" scoped>
.top-main-box {
  position: fixed;
  top: 0;
  z-index: 3;

  .top-main-bar {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100vw;
    font-size: 28rpx;
    font-weight: 500;
    color: #FFFFFF;

    .nav-back {
      position: absolute;
      left: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 30rpx;
      box-sizing: border-box;

      image {
        width: 36rpx;
        height: 30rpx;
      }
    }
  }
}
</style>
