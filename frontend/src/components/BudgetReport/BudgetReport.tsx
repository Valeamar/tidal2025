import React from 'react';
import { AnalysisResponse } from '../../types';
import ProductAnalysisCard from './ProductAnalysisCard';
import OverallBudgetSummary from './OverallBudgetSummary';
import OptimizationRecommendations from './OptimizationRecommendations';
import DataQualityReport from './DataQualityReport';

interface BudgetReportProps {
    analysisResult: AnalysisResponse;
    onNewAnalysis: () => void;
}

const BudgetReport: React.FC<BudgetReportProps> = ({ analysisResult, onNewAnalysis }) => {
    return (
        <div className="space-y-6">
            {/* Header with action button */}
            <div className="bg-green-50 border border-green-200 rounded-md p-4">
                <div className="flex justify-between items-center">
                    <div>
                        <h3 className="text-lg font-medium text-green-800">Analysis Complete</h3>
                        <p className="text-green-700">
                            Your price analysis has been completed. Review the results below.
                        </p>
                    </div>
                    <button
                        onClick={onNewAnalysis}
                        className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700 transition-colors duration-200"
                    >
                        New Analysis
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
            <div className="space-y-4">
                <h2 className="text-2xl font-bold text-gray-900">Product Analysis</h2>
                {analysisResult.analyses.map((analysis, index) => (
                    <ProductAnalysisCard
                        key={`${analysis.productName}-${index}`}
                        analysis={analysis}
                    />
                ))}
            </div>
        </div>
    );
};

export default BudgetReport;