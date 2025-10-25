import React from 'react';

interface OverallBudget {
    totalCost: number;
    potentialSavings: number;
    confidenceScore: number;
}

interface OverallBudgetSummaryProps {
    budget: OverallBudget;
}

const OverallBudgetSummary: React.FC<OverallBudgetSummaryProps> = ({ budget }) => {
    const formatCurrency = (amount: number): string => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    };

    const getConfidenceColor = (score: number): string => {
        if (score >= 0.8) return 'text-green-600';
        if (score >= 0.6) return 'text-yellow-600';
        return 'text-red-600';
    };

    const getConfidenceLabel = (score: number): string => {
        if (score >= 0.8) return 'High';
        if (score >= 0.6) return 'Medium';
        return 'Low';
    };

    const savingsPercentage = budget.totalCost > 0
        ? (budget.potentialSavings / budget.totalCost) * 100
        : 0;

    return (
        <div className="bg-white rounded-lg shadow-md border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">Budget Summary</h2>
            </div>

            <div className="px-6 py-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Total Cost */}
                    <div className="text-center">
                        <div className="text-3xl font-bold text-gray-900 mb-2">
                            {formatCurrency(budget.totalCost)}
                        </div>
                        <div className="text-sm text-gray-500">Total Estimated Cost</div>
                        <div className="text-xs text-gray-400 mt-1">
                            Based on target prices (P35)
                        </div>
                    </div>

                    {/* Potential Savings */}
                    <div className="text-center">
                        <div className="text-3xl font-bold text-green-600 mb-2">
                            {formatCurrency(budget.potentialSavings)}
                        </div>
                        <div className="text-sm text-gray-500">Potential Savings</div>
                        <div className="text-xs text-gray-400 mt-1">
                            {savingsPercentage.toFixed(1)}% of total cost
                        </div>
                    </div>

                    {/* Confidence Score */}
                    <div className="text-center">
                        <div className={`text-3xl font-bold mb-2 ${getConfidenceColor(budget.confidenceScore)}`}>
                            {Math.round(budget.confidenceScore * 100)}%
                        </div>
                        <div className="text-sm text-gray-500">
                            {getConfidenceLabel(budget.confidenceScore)} Confidence
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                            Data quality score
                        </div>
                    </div>
                </div>

                {/* Additional Info */}
                <div className="mt-6 pt-6 border-t border-gray-200">
                    <div className="bg-blue-50 rounded-lg p-4">
                        <div className="flex items-start space-x-3">
                            <div className="text-blue-500 text-xl">💡</div>
                            <div>
                                <h3 className="text-sm font-medium text-blue-800 mb-1">Budget Insights</h3>
                                <p className="text-sm text-blue-700">
                                    This budget is based on current market analysis and AI-powered recommendations.
                                    Actual costs may vary based on timing, quantities, and supplier negotiations.
                                    {budget.potentialSavings > 0 && (
                                        <span className="block mt-1 font-medium">
                                            Follow the optimization recommendations below to achieve the estimated savings.
                                        </span>
                                    )}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OverallBudgetSummary;