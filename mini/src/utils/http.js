import {login} from '@/utils/ma'

const baseURL = 'https://poker.good7080.com/admin'
// const baseURL = 'http://192.168.1.130:9886/admin'
// const baseURL = 'http://localhost:9866/admin'

// 添加拦截器
const httpInterceptor = {
    // 拦截前触发
    invoke(options) {
        // 1. 非 http 开头需拼接地址
        if (!options.url.startsWith('http')) {
            options.url = baseURL + options.url
        }
        // 2. 请求超时, 默认 60s
        options.timeout = 10000
        // 3. 添加小程序端请求头标识
        options.header = {
            ...options.header,
            'ma-appid': uni.getAccountInfoSync().miniProgram.appId, // 将小程序appid添加到头部
        }
        // 4. 添加 token 请求头标识
        const token = uni.getStorageSync('token')
        if (token) {
            options.header['token'] = token
        }
    },
}
uni.addInterceptor('request', httpInterceptor)
uni.addInterceptor('uploadFile', httpInterceptor)

let retry = 0
const request = async (method, url, data, headers) => {
    let header = {
        'content-type': headers && headers.contentType || 'application/json',
    }
    header = Object.assign(header, headers)
    const option = {
        method,
        url,
        data,
        header
    }

    const resp = await uni.request(option)
    if ((resp.data.code === 401) && retry < 2) {
        retry++
        await login()
        if (!headers) headers = {}
        headers['token'] = await uni.getStorageSync('token')
        return await request(method, url, data, headers)
    }
    return resp.data
}

export default {
    get: (url, data, headers) => {
        return request('GET', url, data, headers)
    },
    post: (url, data, headers) => {
        return request('POST', url, data, headers)
    },
    postForm: (url, data, headers = {
        contentType: 'application/x-www-form-urlencoded',
    }) => {
        return request('POST', url, data, headers)
    },
    put: (url, data, headers) => {
        return request('PUT', url, data, headers)
    },
    delete: (url, data, headers) => {
        return request('DELETE', url, data, headers)
    },
}
