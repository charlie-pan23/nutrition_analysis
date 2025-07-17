<script setup>
import {onHide, onLaunch, onShow} from '@dcloudio/uni-app'
import http from '@/utils/http'
import {msg} from '@/utils'

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

  uni.login({
    success(res) {
      if (res.code) {
        console.log('code:', res.code)
        //发起网络请求
        http.get('http://172.20.10.3:5000/wx_login/' + res.code).then(res => {
          if (!res.code === 200) {
            return uni.showToast({title: '登录出错，请稍后再试', icon: 'none', duration: 2000})
          }
          uni.setStorageSync('user', res.user)
        })
      } else {
        console.log('登录失败！' + res.errMsg)
      }
    }
  })
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
