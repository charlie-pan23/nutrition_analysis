import http from '@/utils/http'
import { uuid } from '@/utils/index'

export async function getMescrollData(url,mescroll) {
  // 被组合式函数封装和管理的状态
  const list = ref([])
  const data ={
    num:mescroll.num,
    size: mescroll.size
  }
  await http.get(url,data).then(res => {
    const list = res.data.records || [] // 当前页数据
    if(mescroll.num == 1) list.value = []; //如果是第一页需手动制空列表
    list.value = list.value.concat(list); //追加新数据
    mescroll.endSuccess(list.length); // 请求成功, 结束加载
  }).catch(err => {
    if (list.value.length == 0) mescroll.showEmpty()

    mescroll.endErr(); // 请求失败, 结束加载

  })
  return list
}