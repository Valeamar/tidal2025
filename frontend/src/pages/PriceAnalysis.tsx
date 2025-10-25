import React, { useState } from 'react';
import ProductInputForm from '../components/ProductInputForm';
import { BudgetReport } from '../components/BudgetReport';
import { LegacyAnalysisResponse } from '../types';
import { analyzeProducts } from '../services/api';

const PriceAnalysis: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<LegacyAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFormSubmit = async (data: any) => {
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
    <div className="min-h-screen">
      <div className="container mx-auto px-6 py-12">
        <div className="text-center mb-12 slide-in-up">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            <span className="gradient-text">Price Analysis</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Enter your farm information and product requirements to get personalized
            AI-powered price analysis and optimization recommendations.
          </p>
        </div>

        {error && (
          <div className="glass-card border-red-500/30 bg-red-500/10 p-6 mb-8 max-w-4xl mx-auto slide-in-up">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-red-300 mb-2">Analysis Error</h3>
                <p className="text-red-200">{error}</p>
              </div>
            </div>
          </div>
        )}

        {analysisResult ? (
          <BudgetReport
            analysisResult={analysisResult}
            onNewAnalysis={handleNewAnalysis}
          />
        ) : (
          <ProductInputForm onSubmit={handleFormSubmit} isLoading={isLoading} />
        )}
      </div>
    </div>
  );
};

export default PriceAnalysis;