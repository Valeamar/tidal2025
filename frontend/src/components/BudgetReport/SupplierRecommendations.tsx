import React from 'react';
import { LegacySupplierRecommendation } from '../../types';

interface SupplierRecommendationsProps {
    suppliers: LegacySupplierRecommendation[];
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
            <h4 className="text-xl font-semibold text-white mb-6 flex items-center space-x-3">
                <svg className="w-6 h-6 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <span>Supplier Recommendations</span>
            </h4>
            <div className="space-y-4">
                {suppliers.map((supplier, index) => (
                    <div key={index} className="glass-card p-6 border-white/10 hover:border-accent-400/30 hover:scale-[1.02] transition-all duration-300 group">
                        <div className="flex justify-between items-start mb-6">
                            <div className="flex items-center space-x-3">
                                <div className="w-12 h-12 bg-gradient-accent rounded-xl flex items-center justify-center">
                                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                    </svg>
                                </div>
                                <h5 className="text-xl font-bold text-white group-hover:text-accent-400 transition-colors">{supplier.name}</h5>
                            </div>
                            {supplier.listPrice && (
                                <div className="text-right">
                                    <div className="text-2xl font-bold gradient-text">
                                        {formatCurrency(supplier.listPrice)}
                                    </div>
                                    <div className="text-sm text-gray-400">List Price</div>
                                </div>
                            )}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Left Column */}
                            <div className="space-y-4">
                                {supplier.moq && (
                                    <div className="flex items-center justify-between p-3 glass-card border-white/5">
                                        <div className="flex items-center space-x-2">
                                            <svg className="w-4 h-4 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                                            </svg>
                                            <span className="text-gray-400">Minimum Order:</span>
                                        </div>
                                        <span className="font-semibold text-white">{supplier.moq.toLocaleString()} units</span>
                                    </div>
                                )}

                                {supplier.contactInfo && (
                                    <div className="flex items-center justify-between p-3 glass-card border-white/5">
                                        <div className="flex items-center space-x-2">
                                            <svg className="w-4 h-4 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                            </svg>
                                            <span className="text-gray-400">Contact:</span>
                                        </div>
                                        <span className="font-semibold text-accent-400">{supplier.contactInfo}</span>
                                    </div>
                                )}
                            </div>

                            {/* Right Column */}
                            <div className="space-y-4">
                                {supplier.promotions && supplier.promotions.length > 0 && (
                                    <div>
                                        <div className="flex items-center space-x-2 mb-3">
                                            <svg className="w-4 h-4 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                                            </svg>
                                            <span className="text-gray-400 font-medium">Current Promotions:</span>
                                        </div>
                                        <div className="flex flex-wrap gap-2">
                                            {supplier.promotions.map((promo, promoIndex) => (
                                                <span
                                                    key={promoIndex}
                                                    className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-orange-500/20 text-orange-300 border border-orange-500/30"
                                                >
                                                    🎉 {promo}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Price Breaks */}
                        {supplier.priceBreaks && supplier.priceBreaks.length > 0 && (
                            <div className="mt-6 pt-6 border-t border-white/20">
                                <div className="flex items-center space-x-2 mb-4">
                                    <svg className="w-5 h-5 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                    </svg>
                                    <span className="text-gray-300 font-semibold">Volume Pricing:</span>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                    {supplier.priceBreaks.map((priceBreak, breakIndex) => (
                                        <div
                                            key={breakIndex}
                                            className="glass-card p-3 border-accent-400/20 bg-accent-500/10 text-center hover:bg-accent-500/20 transition-all duration-300"
                                        >
                                            <div className="text-sm text-gray-400 mb-1">
                                                {priceBreak.quantity.toLocaleString()}+ units
                                            </div>
                                            <div className="text-lg font-bold text-accent-300">
                                                {formatCurrency(priceBreak.price)}
                                            </div>
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