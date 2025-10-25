import React, { useState } from 'react';
import ProductInputForm from '../components/ProductInputForm';
import { AnalysisRequest, AnalysisResponse } from '../types';
import { analyzeProducts } from '../services/api';

const PriceAnalysis: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFormSubmit = async (data: AnalysisRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await analyzeProducts(data);
      setAnalysisResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during analysis');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewAnalysis = () => {
    setAnalysisResult(null);
    setError(null);
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Agricultural Input Price Analysis
        </h1>
        <p className="text-gray-600">
          Enter your farm information and product requirements to get personalized 
          price analysis and optimization recommendations.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Analysis Error</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {analysisResult ? (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-medium text-green-800">Analysis Complete</h3>
                <p className="text-green-700">
                  Your price analysis has been completed successfully. Results will be displayed here once the backend is implemented.
                </p>
              </div>
              <button
                onClick={handleNewAnalysis}
                className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700 transition-colors duration-200"
              >
                New Analysis
              </button>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Analysis Results</h3>
            <div className="text-center py-8">
              <div className="text-gray-400 text-4xl mb-4">📊</div>
              <p className="text-gray-600">
                Results display will be implemented in task 8.3
              </p>
            </div>
          </div>
        </div>
      ) : (
        <ProductInputForm onSubmit={handleFormSubmit} isLoading={isLoading} />
      )}
    </div>
  );
};

export default PriceAnalysis;