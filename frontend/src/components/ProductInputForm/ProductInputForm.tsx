import React, { useState } from 'react';
import { ProductInput, FarmInfo, AnalysisRequest } from '../../types';
import FarmInfoForm from './FarmInfoForm';
import ProductListForm from './ProductListForm';

interface ProductInputFormProps {
    onSubmit: (data: AnalysisRequest) => void;
    isLoading?: boolean;
}

const ProductInputForm: React.FC<ProductInputFormProps> = ({ onSubmit, isLoading = false }) => {
    const [farmInfo, setFarmInfo] = useState<FarmInfo>({
        location: {
            streetAddress: '',
            city: '',
            state: '',
            county: '',
            zipCode: '',
            country: 'United States'
        }
    });

    const [products, setProducts] = useState<ProductInput[]>([
        { name: '', quantity: 0, unit: '', specifications: '' }
    ]);

    const [errors, setErrors] = useState<Record<string, string>>({});

    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        // Validate farm info
        if (!farmInfo.location.streetAddress.trim()) {
            newErrors.streetAddress = 'Street address is required';
        }
        if (!farmInfo.location.city.trim()) {
            newErrors.city = 'City is required';
        }
        if (!farmInfo.location.state.trim()) {
            newErrors.state = 'State is required';
        }
        if (!farmInfo.location.zipCode.trim()) {
            newErrors.zipCode = 'ZIP code is required';
        }
        if (!farmInfo.location.country.trim()) {
            newErrors.country = 'Country is required';
        }

        // Validate products
        const validProducts = products.filter(p => p.name.trim() && p.quantity > 0 && p.unit.trim());
        if (validProducts.length === 0) {
            newErrors.products = 'At least one valid product is required';
        }

        products.forEach((product, index) => {
            if (product.name.trim() || product.quantity > 0 || product.unit.trim()) {
                if (!product.name.trim()) {
                    newErrors[`product_${index}_name`] = 'Product name is required';
                }
                if (product.quantity <= 0) {
                    newErrors[`product_${index}_quantity`] = 'Quantity must be greater than 0';
                }
                if (!product.unit.trim()) {
                    newErrors[`product_${index}_unit`] = 'Unit is required';
                }
            }
        });

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        const validProducts = products.filter(p => p.name.trim() && p.quantity > 0 && p.unit.trim());

        onSubmit({
            farmLocation: farmInfo.location,
            products: validProducts
        });
    };

    return (
        <div className="max-w-4xl mx-auto">
            <form onSubmit={handleSubmit} className="space-y-8 slide-in-up">
                <FarmInfoForm
                    farmInfo={farmInfo}
                    onChange={setFarmInfo}
                    errors={errors}
                />

                <ProductListForm
                    products={products}
                    onChange={setProducts}
                    errors={errors}
                />

                {errors.products && (
                    <div className="glass-card border-red-500/30 bg-red-500/10 p-6">
                        <div className="flex items-center space-x-3">
                            <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                            </svg>
                            <p className="text-red-300 font-medium">{errors.products}</p>
                        </div>
                    </div>
                )}

                <div className="flex justify-center pt-6">
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="group relative px-12 py-4 bg-gradient-accent text-white font-bold text-lg rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-glow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none overflow-hidden"
                    >
                        <span className="relative z-10 flex items-center space-x-3">
                            {isLoading ? (
                                <>
                                    <div className="spinner"></div>
                                    <span>Analyzing Market Data...</span>
                                </>
                            ) : (
                                <>
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                    <span>Start AI Analysis</span>
                                </>
                            )}
                        </span>
                        {!isLoading && (
                            <div className="absolute inset-0 bg-gradient-to-r from-accent-600 to-primary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default ProductInputForm;