import axios from 'axios';

const apiClient = axios.create({
    // Default to relative path '/' for production (single-link deployment)
    baseURL: import.meta.env.VITE_API_URL || '/',
});

apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default apiClient;
