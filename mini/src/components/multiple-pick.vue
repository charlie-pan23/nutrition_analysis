<template>
  <u-popup :show="pickShow" mode="bottom" :round="10" closeOnClickOverlay @close="onCancel">
    <view class="multiple-pick-content">
      <view class="top">
        <view class="cancel" @tap="onCancel">取消</view>
        <view class="confirm" @tap="onConfirm">确认</view>
      </view>
      <view class="list-container">
        <view class="item-container">
          <view class="item" :class="{'selected': isSelected(item), 'disabled': isDisabled(item)}"
                v-for="(item, index) in list" :key="index" @tap="onClick(item, index)">
            <view>
              {{ keyName ? item[keyName] : item }}
            </view>
            <u-icon v-if="isSelected(item)" name="checkmark" :color="isDisabled(item) ? '#959595' : '#2979ff'"size="18">
            </u-icon>
          </view>
        </view>
      </view>
    </view>
  </u-popup>
</template>

<script>
export default {
  name: "multiplePick",
  data() {
    return {
      pickShow: false,
      selecteds: []
    };
  },
  props: {
    /**
     * 开启单选
     */
    single: Boolean,
    /**
     * 可选最多项
     */
    max: Number,
    /**
     * 超出最大项提示
     */
    maxMessage: String,
    /**
     * 数据集合
     */
    list: Array,
    /**
     * 默认选择
     */
    defaults: Array,
    /**
     * 主键名，如果没有，则识别为字符串数组
     */
    keyName: String,
    /**
     * 禁用属性名，前提是有keyName
     */
    disabledKey: String,
    /**
     * 禁用值，前提是有disabledKey
     */
    disabledValue: String
  },
  watch: {
    defaults: {
      handler(n) {
        // 不能直接赋值，否则selecteds变化时会改变默认值
        this.selecteds = n.slice(0, n.length);
      },
      immediate: true
    }
  },
  methods: {
    /**
     * 当前项是否禁用
     */
    isDisabled(item) {
      return this.keyName && this.disabledKey && this.disabledValue && item[this.disabledKey] === this.disabledValue;
    },
    /**
     * 当前项是否选中
     */
    isSelected(item) {
      return this.selecteds.includes(this.keyName ? item[this.keyName] : item);
    },
    /**
     * 打开选择器
     */
    show() {
      this.pickShow = true;
    },
    /**
     * 关闭选择器
     */
    close() {
      this.pickShow = false;
    },
    /**
     * 数据项点击监听
     */
    onClick(item, index) {
      if (this.isDisabled(item)) {
        // 如果是禁用的，不执行
        return;
      }
      // 获取当前项值
      const value = this.keyName ? item[this.keyName] : item;
      if (this.single) {
        // 开启单选
        this.selecteds = [];
        this.selecteds.push(value);
      } else {
        // 获取当前项在已选中的集合中的位置
        const i = this.selecteds.indexOf(value);
        // 存在则删除，不存在则添加
        if (i !== -1) {
          this.selecteds.splice(i, 1);
        } else {
          if (this.max && this.selecteds.length >= this.max) {
            // 如果有最大值且已选超过最大值
            if (this.maxMessage) {
              // 有提示提示内容
              uni.showToast({
                icon: 'none',
                title: this.maxMessage
              });
              return;
            }
            // 否则删掉最旧的数据
            this.selecteds.shift();
          }
          this.selecteds.push(value);
        }
      }
    },
    /**
     * 确认按钮事件
     */
    onConfirm() {
      this.$emit('confirm', this.selecteds);
    },
    /**
     * 取消按钮事件
     */
    onCancel() {
      // 重新赋值选中的集合
      this.selecteds = this.defaults.slice(0, this.defaults.length);
      this.pickShow = false;
      this.$emit('cancel');
    }
  }
}
</script>

<style lang="scss" scoped>
.multiple-pick-content {
  padding: 20px;
  box-sizing: border-box;
  min-height: 200px;
  max-height: 50vh;

  .top {
    padding: 0 0 10px 0;
    width: 100%;
    display: flex;
    justify-content: space-between;
    line-height: 32px;

    .cancel {
      color: #f43d18;
    }

    .confirm {
      color: #0066ff;
    }
  }

  .list-container {
    padding: 10px 0px 40px 0px;
    box-sizing: border-box;
    max-height: calc(50vh - 42px);
    height: 100%;
    overflow-y: auto;
  }

  .item-container {
    width: 100%;

    .item {
      padding: 10px 0;
      box-sizing: border-box;
      width: 100%;
      display: flex;
      justify-content: space-between;

      &.selected {
        color: #2979ff !important;
      }

      &.disabled {
        color: #959595 !important;
      }
    }
  }
}
</style>
