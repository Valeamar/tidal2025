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

    const getRecommendationIcon = (type: string): JSX.Element => {
        switch (type) {
            case 'timing':
                return <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>;
            case 'bulk_discount':
                return <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>;
            case 'seasonal':
                return <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>;
            case 'supplier':
                return <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>;
            case 'risk_alert':
                return <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>;
            default:
                return <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>;
        }
    };

    const getRecommendationGradient = (type: string): string => {
        switch (type) {
            case 'timing':
                return 'from-blue-500 to-blue-600';
            case 'bulk_discount':
                return 'from-green-500 to-green-600';
            case 'seasonal':
                return 'from-purple-500 to-purple-600';
            case 'supplier':
                return 'from-indigo-500 to-indigo-600';
            case 'risk_alert':
                return 'from-red-500 to-red-600';
            default:
                return 'from-gray-500 to-gray-600';
        }
    };

    const getRecommendationBorder = (type: string): string => {
        switch (type) {
            case 'timing':
                return 'border-blue-400/30 bg-blue-500/10';
            case 'bulk_discount':
                return 'border-green-400/30 bg-green-500/10';
            case 'seasonal':
                return 'border-purple-400/30 bg-purple-500/10';
            case 'supplier':
                return 'border-indigo-400/30 bg-indigo-500/10';
            case 'risk_alert':
                return 'border-red-400/30 bg-red-500/10';
            default:
                return 'border-gray-400/30 bg-gray-500/10';
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
        <div className="glass-card p-8 group hover:scale-[1.02] transition-all duration-300">
            <div className="flex items-center space-x-4 mb-8">
                <div className="w-14 h-14 bg-gradient-accent rounded-2xl flex items-center justify-center pulse-glow">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                </div>
                <div>
                    <h2 className="text-3xl font-bold text-white">Optimization Recommendations</h2>
                    <p className="text-gray-300">
                        AI-powered suggestions to maximize your savings and optimize purchasing strategy
                    </p>
                </div>
            </div>

            <div className="space-y-6">
                {recommendations.map((recommendation, index) => (
                    <div
                        key={index}
                        className={`glass-card p-6 ${getRecommendationBorder(recommendation.type)} hover:scale-[1.02] transition-all duration-300 group/card`}
                    >
                        <div className="flex items-start space-x-4">
                            <div className={`w-12 h-12 bg-gradient-to-r ${getRecommendationGradient(recommendation.type)} rounded-xl flex items-center justify-center text-white flex-shrink-0 group-hover/card:scale-110 transition-transform duration-300`}>
                                {getRecommendationIcon(recommendation.type)}
                            </div>
                            <div className="flex-1">
                                <div className="flex flex-col md:flex-row md:justify-between md:items-start mb-4 space-y-2 md:space-y-0">
                                    <h3 className="text-xl font-bold text-white group-hover/card:text-accent-400 transition-colors">
                                        {recommendation.title}
                                    </h3>
                                    <div className="flex flex-wrap items-center gap-3">
                                        {recommendation.potentialSavings && recommendation.potentialSavings > 0 && (
                                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-green-500/20 text-green-300 border border-green-500/30">
                                                💰 Save {formatCurrency(recommendation.potentialSavings)}
                                            </span>
                                        )}
                                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${recommendation.confidence >= 0.8 ? 'bg-green-500/20 text-green-300 border-green-500/30' :
                                                recommendation.confidence >= 0.6 ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30' :
                                                    'bg-red-500/20 text-red-300 border-red-500/30'
                                            }`}>
                                            📊 {Math.round(recommendation.confidence * 100)}% confidence
                                        </span>
                                    </div>
                                </div>

                                <p className="text-gray-300 leading-relaxed mb-4">
                                    {recommendation.description}
                                </p>

                                <div className="glass-card p-4 border-accent-400/20 bg-accent-500/10">
                                    <div className="flex items-start space-x-3">
                                        <div className="w-6 h-6 bg-gradient-accent rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                                            <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                            </svg>
                                        </div>
                                        <div>
                                            <div className="text-sm font-semibold text-accent-300 mb-1">Recommended Action:</div>
                                            <div className="text-sm text-gray-300 leading-relaxed">
                                                {recommendation.description}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default OptimizationRecommendations;