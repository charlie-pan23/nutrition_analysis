import http from './http'
import { msg } from '@/utils/index'

export const login = async () => {
  return new Promise((resolve) => {
    uni.login({
      provider: 'weixin', //使用微信登录
      success: function (res) {
        if (res.code) {
          http.get('/anon/login', {
            code: res.code
          }).then((loginRes) => {
            if (loginRes.success) {
              uni.setStorageSync('token', loginRes.data.token)
              resolve()
            }
          })
        }
      },
      fail: function (err) {
        console.log(err)
        msg(err)
      }
    })
  })
}

export const getMaCode = () => {
  return new Promise((resolve) => {
    uni.login({
      success: function (res) {
        if (res.code) {
          resolve(res.code)
        } else {
          resolve('')
        }
      }
    })
  })
}
