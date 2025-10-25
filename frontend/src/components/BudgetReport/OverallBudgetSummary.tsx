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
        <div className="glass-card p-8 group hover:scale-[1.02] transition-all duration-300">
            <div className="flex items-center space-x-4 mb-8">
                <div className="w-14 h-14 bg-gradient-accent rounded-2xl flex items-center justify-center">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                    </svg>
                </div>
                <div>
                    <h2 className="text-3xl font-bold text-white">Budget Summary</h2>
                    <p className="text-gray-300">AI-powered cost analysis and optimization insights</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Total Cost */}
                <div className="glass-card p-6 text-center group hover:scale-105 transition-all duration-300 border-white/10">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v2" />
                        </svg>
                    </div>
                    <div className="text-4xl font-bold text-white mb-3">
                        {formatCurrency(budget.totalCost)}
                    </div>
                    <div className="text-gray-300 font-medium mb-1">Total Estimated Cost</div>
                    <div className="text-xs text-gray-400">
                        Based on target prices (P35)
                    </div>
                </div>

                {/* Potential Savings */}
                <div className="glass-card p-6 text-center group hover:scale-105 transition-all duration-300 border-accent-400/30 bg-accent-500/10">
                    <div className="w-12 h-12 bg-gradient-accent rounded-xl flex items-center justify-center mx-auto mb-4">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                        </svg>
                    </div>
                    <div className="text-4xl font-bold gradient-text mb-3">
                        {formatCurrency(budget.potentialSavings)}
                    </div>
                    <div className="text-gray-300 font-medium mb-1">Potential Savings</div>
                    <div className="text-xs text-accent-400 font-semibold">
                        {savingsPercentage.toFixed(1)}% of total cost
                    </div>
                </div>

                {/* Confidence Score */}
                <div className="glass-card p-6 text-center group hover:scale-105 transition-all duration-300 border-white/10">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4 ${budget.confidenceScore >= 0.8 ? 'bg-gradient-to-r from-green-500 to-green-600' :
                            budget.confidenceScore >= 0.6 ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' :
                                'bg-gradient-to-r from-red-500 to-red-600'
                        }`}>
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                    </div>
                    <div className={`text-4xl font-bold mb-3 ${getConfidenceColor(budget.confidenceScore)}`}>
                        {Math.round(budget.confidenceScore * 100)}%
                    </div>
                    <div className="text-gray-300 font-medium mb-1">
                        {getConfidenceLabel(budget.confidenceScore)} Confidence
                    </div>
                    <div className="text-xs text-gray-400">
                        Data quality score
                    </div>
                </div>
            </div>

            {/* Additional Info */}
            <div className="mt-8 pt-8 border-t border-white/20">
                <div className="glass-card p-6 border-accent-400/20 bg-accent-500/10">
                    <div className="flex items-start space-x-4">
                        <div className="w-10 h-10 bg-gradient-accent rounded-xl flex items-center justify-center flex-shrink-0">
                            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-white mb-2">Budget Insights</h3>
                            <p className="text-gray-300 leading-relaxed">
                                This budget is based on current market analysis and AI-powered recommendations.
                                Actual costs may vary based on timing, quantities, and supplier negotiations.
                                {budget.potentialSavings > 0 && (
                                    <span className="block mt-2 font-medium text-accent-400">
                                        💡 Follow the optimization recommendations below to achieve the estimated savings.
                                    </span>
                                )}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OverallBudgetSummary;