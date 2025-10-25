import React from 'react';
import { PriceAnalysis } from '../../types';
import { SupplierRecommendations } from './';

interface ProductAnalysisCardProps {
    analysis: PriceAnalysis;
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
        <div className="bg-white rounded-lg shadow-md border border-gray-200">
            {/* Product Header */}
            <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex justify-between items-start">
                    <div>
                        <h3 className="text-xl font-semibold text-gray-900">{analysis.productName}</h3>
                        <div className="mt-2 flex items-center space-x-4">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getConfidenceColor(analysis.confidenceScore)}`}>
                                {getConfidenceLabel(analysis.confidenceScore)} Confidence ({Math.round(analysis.confidenceScore * 100)}%)
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="px-6 py-4 space-y-6">
                {/* Price Ranges */}
                <div>
                    <h4 className="text-lg font-medium text-gray-900 mb-3">Price Analysis</h4>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        <div className="text-center">
                            <div className="text-sm text-gray-500">P10 (Low)</div>
                            <div className="text-lg font-semibold text-gray-900">{formatCurrency(analysis.priceRanges.p10)}</div>
                        </div>
                        <div className="text-center">
                            <div className="text-sm text-gray-500">P25</div>
                            <div className="text-lg font-semibold text-gray-900">{formatCurrency(analysis.priceRanges.p25)}</div>
                        </div>
                        <div className="text-center bg-blue-50 rounded-lg p-2">
                            <div className="text-sm text-blue-600 font-medium">Target (P35)</div>
                            <div className="text-xl font-bold text-blue-700">{formatCurrency(analysis.priceRanges.p35)}</div>
                        </div>
                        <div className="text-center">
                            <div className="text-sm text-gray-500">P50 (Median)</div>
                            <div className="text-lg font-semibold text-gray-900">{formatCurrency(analysis.priceRanges.p50)}</div>
                        </div>
                        <div className="text-center">
                            <div className="text-sm text-gray-500">P90 (High)</div>
                            <div className="text-lg font-semibold text-gray-900">{formatCurrency(analysis.priceRanges.p90)}</div>
                        </div>
                    </div>
                </div>

                {/* Effective Cost Breakdown */}
                <div>
                    <h4 className="text-lg font-medium text-gray-900 mb-3">Cost Breakdown</h4>
                    <div className="bg-gray-50 rounded-lg p-4">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                                <span className="text-gray-500">Base Price:</span>
                                <div className="font-semibold">{formatCurrency(analysis.effectiveCost.basePrice)}</div>
                            </div>
                            <div>
                                <span className="text-gray-500">Logistics:</span>
                                <div className="font-semibold">{formatCurrency(analysis.effectiveCost.logisticsCost)}</div>
                            </div>
                            <div>
                                <span className="text-gray-500">Taxes & Fees:</span>
                                <div className="font-semibold">{formatCurrency(analysis.effectiveCost.taxes)}</div>
                            </div>
                            <div>
                                <span className="text-gray-500">Wastage:</span>
                                <div className="font-semibold">{formatCurrency(analysis.effectiveCost.wastage)}</div>
                            </div>
                        </div>
                        <div className="mt-3 pt-3 border-t border-gray-200">
                            <div className="flex justify-between items-center">
                                <span className="text-gray-700 font-medium">Total Effective Cost:</span>
                                <span className="text-lg font-bold text-gray-900">{formatCurrency(analysis.effectiveCost.totalCost)}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Data Availability */}
                <div>
                    <h4 className="text-lg font-medium text-gray-900 mb-3">Data Availability</h4>
                    <div className="flex flex-wrap gap-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${analysis.dataAvailability.marketData ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                            Market Data: {analysis.dataAvailability.marketData ? 'Available' : 'Limited'}
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${analysis.dataAvailability.supplierData ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                            Supplier Data: {analysis.dataAvailability.supplierData ? 'Available' : 'Limited'}
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${analysis.dataAvailability.forecastData ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
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
                        <h4 className="text-lg font-medium text-gray-900 mb-3">Recommendations</h4>
                        <div className="space-y-2">
                            {analysis.recommendations.map((recommendation, index) => (
                                <div key={index} className="bg-blue-50 border border-blue-200 rounded-md p-3">
                                    <p className="text-blue-800 text-sm">{recommendation}</p>
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