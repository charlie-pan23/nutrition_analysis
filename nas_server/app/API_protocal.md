


### API 协议
| 资源                     | URL 路径 (示例)                                                  | HTTP 方法  | 描述                             |
| :--------------------- | :----------------------------------------------------------- | :------- | :----------------------------- |
| **用户 (User)**          | `/users`                                                     | `POST`   | 添加新用户                          |
|                        | `/users`                                                     | `GET`    | 获取所有用户                         |
|                        | `/users/{openid}`                                            | `GET`    | 根据 OpenID 获取单个用户               |
|                        | `/users/{openid}`                                            | `PUT`    | 根据 OpenID 更新用户                 |
|                        | `/users/{openid}`                                            | `DELETE` | 根据 OpenID 删除用户                 |
| **食物 (Food)**          | `/foods`                                                     | `POST`   | 添加新食物                          |
|                        | `/foods`                                                     | `GET`    | 获取所有食物                         |
|                        | `/foods/{food_id}`                                           | `GET`    | 根据 ID 获取单个食物                   |
|                        | `/foods/name/{food_name}`                                    | `GET`    | 根据名称获取单个食物                     |
|                        | `/foods/{food_id}`                                           | `PUT`    | 根据 ID 更新食物                     |
|                        | `/foods/{food_id}`                                           | `DELETE` | 根据 ID 删除食物                     |
| **餐食类型 (Meal Type)**   | `/meal_types`                                                | `POST`   | 添加新餐食类型                        |
|                        | `/meal_types`                                                | `GET`    | 获取所有餐食类型                       |
|                        | `/meal_types/{type_id}`                                      | `GET`    | 根据 ID 获取单个餐食类型                 |
|                        | `/meal_types/name/{type_name}`                               | `GET`    | 根据名称获取单个餐食类型                   |
|                        | `/meal_types/by_time/{time_string}`                          | `GET`    | 根据 `description` 字段中的时间字符串模糊查询 |
| **饮食记录 (Meal Record)** | `/meal_records`                                              | `POST`   | 添加新的饮食记录                       |
|                        | `/meal_records/all`                                          | `GET`    | 获取所有饮食记录                       |
|                        | `/meal_records/{record_id}`                                  | `GET`    | 根据 ID 获取单个饮食记录                 |
|                        | `/meal_records/{record_id}`                                  | `PUT`    | 根据 ID 更新饮食记录                   |
|                        | `/meal_records/{record_id}`                                  | `DELETE` | 根据 ID 删除饮食记录                   |
|                        | `/meal_records/user/{user_openid}`                           | `GET`    | 获取某用户的所有饮食记录                   |
|                        | `/meal_records/user/{user_openid}/date/{meal_date}`          | `GET`    | 获取某用户在指定日期的饮食记录                |
|                        | `/meal_records/user/{user_openid}/meal_type/{meal_type_id}`  | `GET`    | 获取某用户在指定餐食类型的饮食记录              |
|                        | `/meal_records/user/{user_openid}/daily_summary/{meal_date}` | `GET`    | 获取某用户在指定日期的营养摄入汇总              |


### 小程序密钥信息

密钥 - 0dba341f543a35cd764eddcd120d864e   
AppID - wxf07a5d5ce93485ad
