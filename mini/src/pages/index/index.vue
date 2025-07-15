<template>
    <view class="container">
        <Nav :has-nav="false" title="" title-color="#444444"></Nav>
        <view :style="sysHeight.paddingHeight" class="content">
            <view class="card c1">
                <view class="title">yolo vision</view>
            </view>
            <view class="card c2">
                <view class="title">实时分析</view>
            </view>
            <view class="control">
                <view class="item btn">分析</view>
                <view class="item circle">讲话</view>
                <view class="item btn">记录</view>
            </view>
        </view>
        <Tab :tab="2" />
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
        font-size: 26rpx;
        border: 1rpx solid  #EEC6AF;
    }

    .btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 200rpx;
        height: 60rpx;
        letter-spacing: 8rpx;
        border-radius: 8rpx;
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
</style>
