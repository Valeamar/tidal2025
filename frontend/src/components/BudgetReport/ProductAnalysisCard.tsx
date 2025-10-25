import React from 'react';
import { LegacyPriceAnalysis } from '../../types';
import { SupplierRecommendations } from './';

interface ProductAnalysisCardProps {
    analysis: LegacyPriceAnalysis;
}

const ProductAnalysisCard: React.FC<ProductAnalysisCardProps> = ({ analysis }) => {
    const formatCurrency = (amount: number): string => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    };

    const getConfidenceColor = (score: number): string => {
        if (score >= 0.8) return 'text-green-600 bg-green-100';
        if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
        return 'text-red-600 bg-red-100';
    };

    const getConfidenceLabel = (score: number): string => {
        if (score >= 0.8) return 'High';
        if (score >= 0.6) return 'Medium';
        return 'Low';
    };

    return (
        <div className="glass-card p-8 group hover:scale-[1.02] transition-all duration-300">
            {/* Product Header */}
            <div className="flex items-center justify-between mb-8 pb-6 border-b border-white/20">
                <div className="flex items-center space-x-4">
                    <div className="w-14 h-14 bg-gradient-accent rounded-2xl flex items-center justify-center">
                        <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                        </svg>
                    </div>
                    <div>
                        <h3 className="text-2xl font-bold text-white mb-2">{analysis.productName}</h3>
                        <div className="flex items-center space-x-3">
                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${analysis.confidenceScore >= 0.8 ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                                analysis.confidenceScore >= 0.6 ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' :
                                    'bg-red-500/20 text-red-300 border border-red-500/30'
                                }`}>
                                {getConfidenceLabel(analysis.confidenceScore)} Confidence ({Math.round(analysis.confidenceScore * 100)}%)
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="space-y-8">
                {/* Price Ranges */}
                <div>
                    <h4 className="text-xl font-semibold text-white mb-6 flex items-center space-x-3">
                        <svg className="w-6 h-6 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        <span>Price Analysis</span>
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        <div className="glass-card p-4 text-center border-white/10 hover:border-red-400/30 transition-all duration-300">
                            <div className="text-sm text-gray-400 mb-2">P10 (Low)</div>
                            <div className="text-lg font-bold text-red-300">{formatCurrency(analysis.priceRanges.p10)}</div>
                        </div>
                        <div className="glass-card p-4 text-center border-white/10 hover:border-yellow-400/30 transition-all duration-300">
                            <div className="text-sm text-gray-400 mb-2">P25</div>
                            <div className="text-lg font-bold text-yellow-300">{formatCurrency(analysis.priceRanges.p25)}</div>
                        </div>
                        <div className="glass-card p-4 text-center border-accent-400/50 bg-accent-500/20 pulse-glow">
                            <div className="text-sm text-accent-300 font-semibold mb-2">🎯 Target (P35)</div>
                            <div className="text-2xl font-bold gradient-text">{formatCurrency(analysis.priceRanges.p35)}</div>
                        </div>
                        <div className="glass-card p-4 text-center border-white/10 hover:border-blue-400/30 transition-all duration-300">
                            <div className="text-sm text-gray-400 mb-2">P50 (Median)</div>
                            <div className="text-lg font-bold text-blue-300">{formatCurrency(analysis.priceRanges.p50)}</div>
                        </div>
                        <div className="glass-card p-4 text-center border-white/10 hover:border-purple-400/30 transition-all duration-300">
                            <div className="text-sm text-gray-400 mb-2">P90 (High)</div>
                            <div className="text-lg font-bold text-purple-300">{formatCurrency(analysis.priceRanges.p90)}</div>
                        </div>
                    </div>
                </div>

                {/* Effective Cost Breakdown */}
                <div>
                    <h4 className="text-xl font-semibold text-white mb-6 flex items-center space-x-3">
                        <svg className="w-6 h-6 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                        <span>Cost Breakdown</span>
                    </h4>
                    <div className="glass-card p-6 border-white/10">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                            <div className="text-center">
                                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mx-auto mb-3">
                                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                                    </svg>
                                </div>
                                <span className="text-gray-400 text-sm">Base Price</span>
                                <div className="text-lg font-bold text-white mt-1">{formatCurrency(analysis.effectiveCost.basePrice)}</div>
                            </div>
                            <div className="text-center">
                                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-3">
                                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                                    </svg>
                                </div>
                                <span className="text-gray-400 text-sm">Logistics</span>
                                <div className="text-lg font-bold text-white mt-1">{formatCurrency(analysis.effectiveCost.logisticsCost)}</div>
                            </div>
                            <div className="text-center">
                                <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-xl flex items-center justify-center mx-auto mb-3">
                                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                    </svg>
                                </div>
                                <span className="text-gray-400 text-sm">Taxes & Fees</span>
                                <div className="text-lg font-bold text-white mt-1">{formatCurrency(analysis.effectiveCost.taxes)}</div>
                            </div>
                            <div className="text-center">
                                <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-red-600 rounded-xl flex items-center justify-center mx-auto mb-3">
                                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                    </svg>
                                </div>
                                <span className="text-gray-400 text-sm">Wastage</span>
                                <div className="text-lg font-bold text-white mt-1">{formatCurrency(analysis.effectiveCost.wastage)}</div>
                            </div>
                        </div>
                        <div className="mt-6 pt-6 border-t border-white/20">
                            <div className="flex justify-between items-center">
                                <span className="text-gray-300 font-semibold text-lg">Total Effective Cost:</span>
                                <span className="text-2xl font-bold gradient-text">{formatCurrency(analysis.effectiveCost.totalCost)}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Data Availability */}
                <div>
                    <h4 className="text-xl font-semibold text-white mb-6 flex items-center space-x-3">
                        <svg className="w-6 h-6 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                        <span>Data Availability</span>
                    </h4>
                    <div className="flex flex-wrap gap-3">
                        <span className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-semibold border transition-all duration-300 ${analysis.dataAvailability.marketData
                            ? 'bg-green-500/20 text-green-300 border-green-500/30 hover:bg-green-500/30'
                            : 'bg-red-500/20 text-red-300 border-red-500/30 hover:bg-red-500/30'
                            }`}>
                            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            Market Data: {analysis.dataAvailability.marketData ? 'Available' : 'Limited'}
                        </span>
                        <span className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-semibold border transition-all duration-300 ${analysis.dataAvailability.supplierData
                            ? 'bg-green-500/20 text-green-300 border-green-500/30 hover:bg-green-500/30'
                            : 'bg-red-500/20 text-red-300 border-red-500/30 hover:bg-red-500/30'
                            }`}>
                            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            Supplier Data: {analysis.dataAvailability.supplierData ? 'Available' : 'Limited'}
                        </span>
                        <span className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-semibold border transition-all duration-300 ${analysis.dataAvailability.forecastData
                            ? 'bg-green-500/20 text-green-300 border-green-500/30 hover:bg-green-500/30'
                            : 'bg-red-500/20 text-red-300 border-red-500/30 hover:bg-red-500/30'
                            }`}>
                            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            Forecast Data: {analysis.dataAvailability.forecastData ? 'Available' : 'Limited'}
                        </span>
                    </div>
                </div>

                {/* Supplier Recommendations */}
                {analysis.suppliers && analysis.suppliers.length > 0 && (
                    <SupplierRecommendations suppliers={analysis.suppliers} />
                )}

                {/* Product-specific Recommendations */}
                {analysis.recommendations && analysis.recommendations.length > 0 && (
                    <div>
                        <h4 className="text-xl font-semibold text-white mb-6 flex items-center space-x-3">
                            <svg className="w-6 h-6 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                            </svg>
                            <span>AI Recommendations</span>
                        </h4>
                        <div className="space-y-4">
                            {analysis.recommendations.map((recommendation, index) => (
                                <div key={index} className="glass-card p-4 border-accent-400/20 bg-accent-500/10 hover:bg-accent-500/20 transition-all duration-300">
                                    <div className="flex items-start space-x-3">
                                        <div className="w-8 h-8 bg-gradient-accent rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                                            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                            </svg>
                                        </div>
                                        <p className="text-gray-300 leading-relaxed">{recommendation}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ProductAnalysisCard;