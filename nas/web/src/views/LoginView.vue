<template>
  <div class="login-view">
    <h1>选择账号</h1>
    <el-row>
      <el-col :span="24">
        <el-scrollbar height="550px">
          <div
              class="user-list-container"
              :class="{ 'scrollable': users.length > 5 }"
          >
            <div
                v-for="user in users"
                :key="user.id"
                class="user-item"
                @click="selectUser(user)"
            >
              <div class="user-name">{{ user.name }}</div>
              <div class="user-id">{{ user.id }}</div>
            </div>
          </div>
        </el-scrollbar>
      </el-col>
    </el-row>
    <el-col :span="24" class="action-buttons" style="margin-top: 20px; ">
      <el-col :span="12">
        <el-button type="success" class="add-user-btn" @click="showForm = true">添加新用户</el-button>
      </el-col>
      <el-col :span="12">
        <el-button type="primary" class="manage-users-btn" @click="showManagement = true">管理用户</el-button>
      </el-col>
    </el-col>

    <!-- 添加用户模态框 -->
    <AddUser
        v-model="showForm"
        @cancel="showForm = false"
        @submit="handleNewUser"
    />
    <!-- 管理用户模态框 -->
    <el-dialog
        title="管理用户"
        v-model="showManagement"
        width="600px"
        @close="onManageClose"
    >
      <div class="management-content">
        <el-scrollbar height="400px">
          <div class="user-management-list">
            <div
                v-for="user in nonAdminUsers"
                :key="user.id"
                class="management-user-item"
            >
              <div class="user-info">
                <div class="user-name">{{ user.name }}</div>
                <div class="user-id">{{ user.id }}</div>
              </div>
              <el-button type="danger" size="mini" @click="deleteUser(user)">删除</el-button>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </el-dialog>
  </div>

</template>

<script>
import axios from 'axios';
import AddUser from '../components/AddUser.vue';


export default {
  components: {AddUser},
  data() {
    return {
      users: [],
      showForm: false,
      showManagement: false,
    }
  },
  async mounted() {
    await this.fetchUsers();

    // // 添加触屏滑动支持
    this.setupTouchScrolling();
  },
  computed: {
    nonAdminUsers() {
      return this.users.filter(user => user.role !== 'admin');
    }
  },
  methods: {
    async fetchUsers() {
      try {
        // 一种方式，直接再这个里面路径写死 localhost:5000
        const response = await axios.get('/api/users');
        this.users = response.data;
      } catch (error) {
        console.error('获取用户失败:', error);
        // 后备数据
        this.users = [
          {id: '550e8400-e29b-41d4-a716-446655440000', name: 'Admin'}

        ];
      }
    },
    async handleNewUser(userData) {
      try {
        const response = await axios.post('/api/users', userData);

        this.users.push({
          id: response.data.id,
          name: response.data.name
        });

        this.showForm = false;

        alert(`用户 ${response.data.name} 添加成功`);
      } catch (error) {
        console.error('添加用户失败:', error);
        alert(error.response?.data?.error || '添加用户失败');
      }
    },

    setupTouchScrolling() {
      const userList = this.$refs.userList;
      if (!userList) return;

      let startY = 0;
      let scrollTop = 0;

      userList.addEventListener('touchstart', (e) => {
        startY = e.touches[0].clientY;
        scrollTop = userList.scrollTop;
      });

      userList.addEventListener('touchmove', (e) => {
        const deltaY = e.touches[0].clientY - startY;
        userList.scrollTop = scrollTop - deltaY;
      });
    },

    async selectUser(user) {
      try {
        await axios.post('/api/login', {username: user.name});
        this.$router.push('/home');
      } catch (error) {
        console.error('登录失败:', error);
        alert('登录失败，请重试');
      }
    },
    deleteUser: async function (user) {
      const confirm = window.confirm(`确定要删除用户 "${user.name}" 吗？`);
      if (!confirm) return;

      try {
        await axios.delete(`/api/users/${user.id}`);

        // 从列表中移除
        this.users.splice(this.users.indexOf(user), 1);

        alert('用户删除成功');
      } catch (error) {
        console.error('删除用户失败:', error);
        alert(error.response?.data?.error || '删除用户失败');
      }
    },

  },

}
</script>

<style scoped>
h1 {
  font-size: 30px;
  font-weight: bold;
  margin-left: 15px;
  letter-spacing: 1px;
  font-family: "Segoe UI", sans-serif;
}

.login-view {
  padding: 2rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.user-list-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow: hidden;
}

.user-list-container.scrollable {
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #888 #f5f5f5;
}

/* 滚动条样式 */
.user-list-container.scrollable::-webkit-scrollbar {
  width: 8px;
}

.user-list-container.scrollable::-webkit-scrollbar-track {
  background: #f5f5f5;
  border-radius: 4px;
}

.user-list-container.scrollable::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.user-list-container.scrollable::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.user-item {
  padding: 1.5rem;
  background-color: #f5f5f5;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 80px;
}

.user-item:hover {
  background-color: #e0e0e0;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.user-name {
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 0.5rem;
  color: #333;
}

.user-id {
  font-size: 0.9rem;
  text-align: center;
  color: #666;
  word-break: break-all;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.add-user-btn, .manage-users-btn {
  flex: 1;
  padding: 1rem;
  border: none;
  border-radius: 8px;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;

  width: 80%;
  height: 80px;

}

.add-user-btn {
  background-color: #4CAF50;
  color: white;
}

.add-user-btn:hover {
  background-color: #388e3c;
}

.manage-users-btn {
  background-color: #2196F3;
  color: white;
}

.manage-users-btn:hover {
  background-color: #1976d2;
}

.management-content {
  padding: 1rem;
}

.user-management-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.management-user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.user-info .user-name {
  font-weight: bold;
  font-size: 1.1rem;
  color: #333;
}

.user-info .user-id {
  font-size: 0.9rem;
  color: #888;
}

.modal-content h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  text-align: center;
  color: #333;
}


.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
}


.form-actions button {
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.form-actions button:first-child {
  background-color: #f5f5f5;
  color: #000000;
}

.form-actions button:first-child:hover {
  background-color: #e0e0e0;
}

.form-actions button:last-child {
  background-color: #4CAF50;
  color: white;
}

.form-actions button:last-child:hover {
  background-color: #388e3c;
}

/* 触屏优化 */
.user-item {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

@media (max-width: 768px) {
  .user-item {
    padding: 1.2rem;
  }

  .user-name {
    font-size: 1.3rem;
  }

  .user-id {
    font-size: 0.8rem;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>