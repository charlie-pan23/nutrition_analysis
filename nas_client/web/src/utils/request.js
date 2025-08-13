import axios from 'axios'
import {ElMessageBox, ElNotification} from "element-plus";

axios.defaults.timeout = 50000

// HTTP request 拦截器
axios.interceptors.request.use(
  config => {
    // get参数编码
    let url = config.url
    if (config.method === 'get' && config.params) {
      url += '?'
      const keys = Object.keys(config.params)
      for (const key of keys) {
        if (config.params[key] !== '') {
          url += `${key}=${encodeURIComponent(config.params[key])}&`
        }
      }
      if (url) {
        url = url.substring(0, url.length - 1)
      }
      config.params = {}
    }
    config.url = url
    return config
  },
  error => {
    return Promise.reject(error)
  },
)

// 响应拦截
axios.interceptors.response.use(response => {
    if (response.status >= 200 && response.status < 300) {
      return Promise.resolve(response)
    } else {
      return Promise.reject(response)
    }
  },
  // 服务器状态码不是200的情况
  error => {
    // 不用reject， 因为用了就要在try catch中捕获异常，增加代码可维护性
    return Promise.resolve(error.response)
  },
)

const http = {
  /** request 请求
   * @param  {object} config 请求参数
   */
  request: function (config) {
    return new Promise((resolve, reject) => {
      axios.request(config).then(response => {
        resolve(response.data)
      }).catch(error => {
        reject(error)
      })
    })
  },

  /** get 请求
   * @param  {string} url 接口地址
   * @param  {object} params 请求参数
   * @param  {object} config 参数
   */
  get: function (url, params = {}, config = {}) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'get',
        url: url,
        params: params,
        ...config,
      }).then(response => {
        resolve(response.data)
      }).catch(error => {
        reject(error)
      })
    })
  },

  /** post 请求
   * @param  {string} url 接口地址
   * @param  {object} data 请求参数
   * @param  {object} config 参数
   */
  post: function (url, data = {}, config = {}) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'post',
        url: url,
        data: data,
        ...config,
      }).then(response => {
        resolve(response.data)
      }).catch(error => {
        reject(error)
      })
    })
  },
  postParams: function (url, params = {}, config = {}) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'post',
        url: url,
        params,
        ...config,
      }).then(response => {
        resolve(response.data)
      }).catch(error => {
        reject(error)
      })
    })
  },

  /** put 请求
   * @param  {string} url 接口地址
   * @param  {object} data 请求参数
   * @param  {object} config 参数
   */
  put: function (url, data = {}, config = {}) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'put',
        url: url,
        data: data,
        ...config,
      }).then(response => {
        resolve(response.data)
      }).catch(error => {
        reject(error)
      })
    })
  },

  /** patch 请求
   * @param  {string} url 接口地址
   * @param  {object} data 请求参数
   * @param  {object} config 参数
   */
  patch: function (url, data = {}, config = {}) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'patch',
        url: url,
        data: data,
        ...config,
      }).then(response => {
        resolve(response.data)
      }).catch(error => {
        reject(error)
      })
    })
  },

  /** delete 请求
   * @param  {string} url 接口地址
   * @param  {object} data 请求参数
   * @param  {object} config 参数
   */
  delete: function (url, data = {}, config = {}) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'delete',
        url: url,
        data: data,
        ...config,
      }).then(response => {
        resolve(response.data)
      }).catch(error => {
        reject(error)
      })
    })
  },
}

export default http
