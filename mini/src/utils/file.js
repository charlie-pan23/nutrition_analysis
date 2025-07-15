import http from '@/utils/http'
import { uuid } from '@/utils/index'

export const uploadFile = (bucket, prefix, file, fileType) => {
  return new Promise(async (resolve, reject) => {
    const params = { bucket, prefix }
    const res = await http.get('/oss/policy', params)
    const fileName = uuid() + '.' + fileType
    const formData = {
      key: res.data.dir + '/' + fileName,
      policy: res.data.policy,
      OSSAccessKeyId: res.data.accessKeyId,
      success_action_status: '200',
      signature: res.data.signature
    }
    uni.uploadFile({
      url: res.data.host,
      filePath: file,
      name: 'file',
      formData,
      success: () => {
        return resolve(res.data.host + '/' + formData.key)
      },
      fail: (error) => {
        return reject(error)
      },
    })
  })

}