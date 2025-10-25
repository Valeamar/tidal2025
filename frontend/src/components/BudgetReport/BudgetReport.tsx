import React from 'react';
import { LegacyAnalysisResponse } from '../../types';
import ProductAnalysisCard from './ProductAnalysisCard';
import OverallBudgetSummary from './OverallBudgetSummary';
import OptimizationRecommendations from './OptimizationRecommendations';
import DataQualityReport from './DataQualityReport';

interface BudgetReportProps {
    analysisResult: LegacyAnalysisResponse;
    onNewAnalysis: () => void;
}

const BudgetReport: React.FC<BudgetReportProps> = ({ analysisResult, onNewAnalysis }) => {
    return (
        <div className="max-w-6xl mx-auto space-y-8 slide-in-up">
            {/* Header with action button */}
            <div className="glass-card p-8 border-accent-400/30 bg-gradient-to-r from-accent-500/20 to-primary-500/20">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
                    <div className="flex items-center space-x-4">
                        <div className="w-16 h-16 bg-gradient-accent rounded-2xl flex items-center justify-center pulse-glow">
                            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <div>
                            <h3 className="text-2xl font-bold text-white mb-2">Analysis Complete</h3>
                            <p className="text-gray-300">
                                Your AI-powered price analysis has been completed. Review the comprehensive results below.
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onNewAnalysis}
                        className="glass-button px-8 py-3 text-white font-semibold hover:scale-105 transition-all duration-300 flex items-center space-x-3"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        <span>New Analysis</span>
                    </button>
                </div>
            </div>

            {/* Overall Budget Summary */}
            <OverallBudgetSummary budget={analysisResult.overallBudget} />

            {/* Data Quality Report */}
            <DataQualityReport report={analysisResult.dataQualityReport} />

            {/* Optimization Recommendations */}
            {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
                <OptimizationRecommendations recommendations={analysisResult.recommendations} />
            )}

            {/* Individual Product Analyses */}
            <div className="space-y-6">
                <div className="text-center">
                    <h2 className="text-4xl font-bold text-white mb-4">
                        <span className="gradient-text">Product Analysis</span>
                    </h2>
                    <p className="text-gray-300 text-lg">
                        Detailed breakdown of each agricultural input with market intelligence
                    </p>
                </div>
                <div className="space-y-6">
                    {analysisResult.analyses.map((analysis, index) => (
                        <ProductAnalysisCard
                            key={`${analysis.productName}-${index}`}
                            analysis={analysis}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default BudgetReport;