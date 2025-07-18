import {createRouter, createWebHistory} from 'vue-router'
import StandbyView from './views/StandbyView.vue'
import LoginView from './views/LoginView.vue'
import Home from "./views/Home.vue";
import Layout from "./layout/Layout.vue";

const routes = [
    {
        path: '/home',
        component: Layout,
        children: [
            {path: '/home', name: 'home', component: Home},
        ]
    },
    {path: '/', name: 'standby', component: StandbyView},
    {path: '/login', name: 'login', component: LoginView},
    // {path: '/camera', name: 'camera', component: Camera},
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
