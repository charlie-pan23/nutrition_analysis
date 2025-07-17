export const getOpenId = () => {
    const user = uni.getStorageSync('user')
    if (!user) {
        return uni.showToast({title: '您尚未登录，请出刷新小程序重试', icon: 'none', duration: 2000})
    }
    return user.openid
}

export const getUser = () => {
    const user = uni.getStorageSync('user')
    if (!user) {
        return uni.showToast({title: '您尚未登录，请出刷新小程序重试', icon: 'none', duration: 2000})
    }
    return user
}