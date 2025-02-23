/* src/router/index.js */
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import InspectorDetail from '../views/InspectorDetail.vue'
import Settings from '../views/Settings.vue' // Import the Settings component

// Define the application routes
const routes = [
{ path: '/', name: 'Home', component: Home },
{ path: '/inspector', name: 'InspectorDetail', component: InspectorDetail },
{ path: '/settings', name: 'Settings', component: Settings }
]

// Create the router instance using HTML5 history mode
const router = createRouter({
history: createWebHistory(),
routes
})

// Export the router instance
export default router