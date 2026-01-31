import axios from 'axios';

// Default to localhost:8000 if env not set
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'multipart/form-data', // Default for uploads, but axios handles it
    },
    timeout: 300000, // 5 minute timeout for large files/slow VLM
});

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);
