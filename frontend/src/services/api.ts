import axios from 'axios';
import { AnalysisResponse, LegacyAnalysisResponse } from '../types';
import { transformAnalysisResponse, transformAnalysisRequest } from '../utils/dataTransform';

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

export const analyzeProducts = async (data: any): Promise<LegacyAnalysisResponse> => {
  try {
    // Transform request to backend format
    const backendRequest = transformAnalysisRequest(data);
    
    const response = await api.post<AnalysisResponse>('/analyze', backendRequest);
    
    // Transform backend response to legacy format for existing UI components
    return transformAnalysisResponse(response.data);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
        throw new Error('Unable to connect to the analysis service. Please ensure the backend server is running.');
      }
      if (error.response?.status === 501) {
        throw new Error('Analysis functionality is not yet implemented on the backend. Please check back later.');
      }
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error.message || 'Analysis failed');
      }
      if (error.response?.data?.detail) {
        // Handle FastAPI error format
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          throw new Error(detail);
        } else if (detail.message) {
          throw new Error(detail.message);
        }
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