import React from 'react';
import { LegacyOptimizationRecommendation } from '../../types';

interface OptimizationRecommendationsProps {
    recommendations: LegacyOptimizationRecommendation[];
}

const OptimizationRecommendations: React.FC<OptimizationRecommendationsProps> = ({ recommendations }) => {
    const formatCurrency = (amount: number): string => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    };

    const getRecommendationIcon = (type: string): string => {
        switch (type) {
            case 'timing':
                return '⏰';
            case 'bulk_discount':
                return '📦';
            case 'seasonal':
                return '🌱';
            case 'supplier':
                return '🏪';
            case 'risk_alert':
                return '⚠️';
            default:
                return '💡';
        }
    };

    const getRecommendationColor = (type: string): string => {
        switch (type) {
            case 'timing':
                return 'bg-blue-50 border-blue-200 text-blue-800';
            case 'bulk_discount':
                return 'bg-green-50 border-green-200 text-green-800';
            case 'seasonal':
                return 'bg-purple-50 border-purple-200 text-purple-800';
            case 'supplier':
                return 'bg-indigo-50 border-indigo-200 text-indigo-800';
            case 'risk_alert':
                return 'bg-red-50 border-red-200 text-red-800';
            default:
                return 'bg-gray-50 border-gray-200 text-gray-800';
        }
    };

    const getConfidenceColor = (confidence: number): string => {
        if (confidence >= 0.8) return 'text-green-600';
        if (confidence >= 0.6) return 'text-yellow-600';
        return 'text-red-600';
    };

    if (!recommendations || recommendations.length === 0) {
        return null;
    }

    return (
        <div className="bg-white rounded-lg shadow-md border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">Optimization Recommendations</h2>
                <p className="text-sm text-gray-600 mt-1">
                    AI-powered suggestions to help you save money and optimize your purchasing strategy
                </p>
            </div>

            <div className="px-6 py-4">
                <div className="space-y-4">
                    {recommendations.map((recommendation, index) => (
                        <div
                            key={index}
                            className={`border rounded-lg p-4 ${getRecommendationColor(recommendation.type)}`}
                        >
                            <div className="flex items-start space-x-3">
                                <div className="text-2xl">{getRecommendationIcon(recommendation.type)}</div>
                                <div className="flex-1">
                                    <div className="flex justify-between items-start mb-2">
                                        <h3 className="font-semibold text-lg">{recommendation.title}</h3>
                                        <div className="flex items-center space-x-2">
                                            {recommendation.potentialSavings && recommendation.potentialSavings > 0 && (
                                                <span className="bg-green-100 text-green-800 text-sm font-medium px-2 py-1 rounded">
                                                    Save {formatCurrency(recommendation.potentialSavings)}
                                                </span>
                                            )}
                                            <span className={`text-sm font-medium ${getConfidenceColor(recommendation.confidence)}`}>
                                                {Math.round(recommendation.confidence * 100)}% confidence
                                            </span>
                                        </div>
                                    </div>

                                    <p className="text-sm mb-3 leading-relaxed">
                                        {recommendation.description}
                                    </p>

                                    <div className="bg-white bg-opacity-50 rounded-md p-3 border border-current border-opacity-20">
                                        <div className="text-sm font-medium mb-1">Action Required:</div>
                                        <div className="text-sm">
                                            {recommendation.description}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default OptimizationRecommendations;