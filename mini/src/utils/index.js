/**
 * uuid
 */
export const uuid = () => {
    const s = []
    const hexDigits = '0123456789abcdef'
    for (let i = 0; i < 32; i++) {
        s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1)
    }
    s[14] = '4' // bits 12-15 of the time_hi_and_version field to 0010
    s[19] = hexDigits.substr((s[19] & 0x3) | 0x8, 1) // bits 6-7 of the clock_seq_hi_and_reserved to 01
    s[8] = s[13] = s[18] = s[23]
    return s.join('')
}

/**
 * 页面栈
 */
export const prePage = (preIndex = 1) => {
    const pages = getCurrentPages()
    const prePage = pages[pages.length - (preIndex + 1)]

    return prePage.$vm
}

/**
 * 判空
 */
export const isNotNull = (val) => {
    return val !== 'null' && val !== null &&
        val !== 'undefined' &&
        val !== undefined &&
        val !== ''
}

/**
 * toast
 */
export const msg = (title = '', param = {}) => {
    if (!title) return
    uni.showToast({
        title,
        duration: param.duration || 2000,
        mask: param.mask || false,
        icon: param.icon || 'none'
    })
}

/**
 * confirm
 */
export const confirm = (title = '', content = '', confirm, cancel) => {
    uni.showModal({
        title: title,
        content: content,
        success: function (res) {
            if (res.confirm) {
                if (confirm) {
                    confirm()
                }
            } else {
                if (cancel) {
                    cancel()
                }
            }
        }
    })
}

export const formatDate = (value) => {
    let date = new Date(value)
    let month = date.getMonth() + 1
    if (month < 10) {
        month = '0' + month
    }
    let day = date.getDate()
    if (day < 10) {
        day = '0' + day
    }
    let hours = date.getHours()
    if (hours < 10) {
        hours = '0' + hours
    }
    let minutes = date.getMinutes()
    if (minutes < 10) {
        minutes = '0' + minutes
    }
    return date.getFullYear() + '-' + month + '-' + day + ' ' + hours + ':' + minutes
}

export const numToString = (value) => {
    let strings = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
        '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']
    return strings[value]
}

export const checkMobile = (mobile) => {
    return /^1[2|3|4|5|6|7|8|9][0-9]{9}$/.test(mobile)
}

export const secretMobile = (phone) => {
    // 将手机号前三位保持不变，后四位用 * 替换
    return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}
const colorList = ['#909399', '#3c9cff', '#f9ae3d', '#5ac725', '#f56c6c', '#398ade', '#f1a532', '#53c21d', '#e45656', '#767a82']

export const getColor = (status) => {
    status = Number(status)
    if (status < 0) {
        getColor(status + 10)
    }
    return colorList[status % 10]
}

/**
 * 对象深拷贝
 */
export const deepClone = (data) => {
    const type = getObjType(data)
    let obj
    if (type === 'array') {
        obj = []
    } else if (type === 'object') {
        obj = {}
    } else {
        // 不再具有下一层次
        return data
    }
    if (type === 'array') {
        for (let i = 0, len = data.length; i < len; i++) {
            obj.push(deepClone(data[i]))
        }
    } else if (type === 'object') {
        for (const key in data) {
            obj[key] = deepClone(data[key])
        }
    }
    return obj
}

export const getObjType = (obj) => {
    const toString = Object.prototype.toString
    const map = {
        '[object Boolean]': 'boolean',
        '[object Number]': 'number',
        '[object String]': 'string',
        '[object Function]': 'function',
        '[object Array]': 'array',
        '[object Date]': 'date',
        '[object RegExp]': 'regExp',
        '[object Undefined]': 'undefined',
        '[object Null]': 'null',
        '[object Object]': 'object'
    }
    return map[toString.call(obj)]
}

export const getParams = (urlString) => {
    console.log(urlString)
    // 提取查询字符串
    const queryStartIndex = urlString.indexOf('?') + 1
    const query = urlString.slice(queryStartIndex)

// 解析查询字符串为对象
    const params = {}
    query.split('&').forEach((part) => {
        const [key, value] = part.split('=')
        params[key] = decodeURIComponent(value)
    })
    return params
}


export const mealTypeEnum = {
    '1': '早餐',
    '2': '午餐',
    '3': '晚餐',
    '4': '夜宵',
    '5': '加餐',
}