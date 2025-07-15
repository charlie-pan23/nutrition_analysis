<script setup>
import { onHide, onLaunch, onShow } from '@dcloudio/uni-app'
import http from '@/utils/http'
import { msg } from '@/utils'

onLaunch(async () => {
  uni.getSystemInfo({
    success: e => {
      const systemInfo = e
      systemInfo.proportion = (750 / e.windowWidth)
      let navigationBarHeight
      let custom = {}
      custom = wx.getMenuButtonBoundingClientRect()
      navigationBarHeight = custom.bottom + custom.top - e.statusBarHeight * systemInfo.proportion
      systemInfo.custom = custom
      systemInfo.navigationBarHeight = navigationBarHeight
      systemInfo.topHeight = e.statusBarHeight * systemInfo.proportion + navigationBarHeight
      uni.setStorageSync('systemInfo', systemInfo)
    }
  })
  // await getUser()
})
onShow(() => {
  console.log('App Show')
})
onHide(() => {
  console.log('App Hide')
})

const getUser = async () => {
  const res = await http.get('/user/info')
  if (!res.success) {
    return msg(res.msg)
  }
  uni.setStorageSync('userInfo', res.data)
  return res.data
}
</script>

<style lang="scss">
@import "uview-plus/index.scss";
/*每个页面公共css */
</style>
