import axios from 'axios';
import { AnalysisRequest, AnalysisResponse } from '../types';

// Get API URL from environment or use default
const getApiUrl = (): string => {
  // In React, environment variables are available at build time
  // For now, we'll use the default since backend isn't ready yet
  return 'http://localhost:8000/api';
};

// Create axios instance with base configuration
const api = axios.create({
  baseURL: getApiUrl(),
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens if needed
api.interceptors.request.use(
  (config) => {
    // Add auth token here if needed in the future
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors here
    if (error.response?.status === 401) {
      // Handle unauthorized access
      console.error('Unauthorized access');
    } else if (error.response?.status >= 500) {
      // Handle server errors
      console.error('Server error:', error.response.data);
    }
    return Promise.reject(error);
  }
);

// API functions

export const analyzeProducts = async (data: AnalysisRequest): Promise<AnalysisResponse> => {
  try {
    const response = await api.post<AnalysisResponse>('/analyze', data);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
        throw new Error('Unable to connect to the analysis service. Please ensure the backend server is running.');
      }
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error.message || 'Analysis failed');
      }
      throw new Error(`Analysis failed: ${error.message}`);
    }
    throw new Error('An unexpected error occurred during analysis');
  }
};

export const checkHealth = async (): Promise<{ status: string; timestamp: string }> => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Health check failed');
  }
};

export default api;