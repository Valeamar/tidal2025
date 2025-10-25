import React from 'react';
import { SupplierRecommendation } from '../../types';

interface SupplierRecommendationsProps {
    suppliers: SupplierRecommendation[];
}

const SupplierRecommendations: React.FC<SupplierRecommendationsProps> = ({ suppliers }) => {
    const formatCurrency = (amount: number): string => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    };

    if (!suppliers || suppliers.length === 0) {
        return null;
    }

    return (
        <div>
            <h4 className="text-lg font-medium text-gray-900 mb-3">Supplier Recommendations</h4>
            <div className="space-y-3">
                {suppliers.map((supplier, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                        <div className="flex justify-between items-start mb-2">
                            <h5 className="font-semibold text-gray-900">{supplier.name}</h5>
                            {supplier.listPrice && (
                                <span className="text-lg font-bold text-green-600">
                                    {formatCurrency(supplier.listPrice)}
                                </span>
                            )}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                            {/* Left Column */}
                            <div className="space-y-2">
                                {supplier.moq && (
                                    <div className="flex justify-between">
                                        <span className="text-gray-500">Minimum Order:</span>
                                        <span className="font-medium">{supplier.moq.toLocaleString()} units</span>
                                    </div>
                                )}

                                {supplier.contactInfo && (
                                    <div className="flex justify-between">
                                        <span className="text-gray-500">Contact:</span>
                                        <span className="font-medium text-blue-600">{supplier.contactInfo}</span>
                                    </div>
                                )}
                            </div>

                            {/* Right Column */}
                            <div className="space-y-2">
                                {supplier.promotions && supplier.promotions.length > 0 && (
                                    <div>
                                        <span className="text-gray-500">Current Promotions:</span>
                                        <div className="mt-1">
                                            {supplier.promotions.map((promo, promoIndex) => (
                                                <span
                                                    key={promoIndex}
                                                    className="inline-block bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full mr-1 mb-1"
                                                >
                                                    {promo}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Price Breaks */}
                        {supplier.priceBreaks && supplier.priceBreaks.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-gray-200">
                                <span className="text-sm text-gray-500 mb-2 block">Volume Pricing:</span>
                                <div className="flex flex-wrap gap-2">
                                    {supplier.priceBreaks.map((priceBreak, breakIndex) => (
                                        <div
                                            key={breakIndex}
                                            className="bg-blue-50 text-blue-800 text-xs px-2 py-1 rounded border border-blue-200"
                                        >
                                            {priceBreak.quantity.toLocaleString()}+ units: {formatCurrency(priceBreak.price)}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default SupplierRecommendations;