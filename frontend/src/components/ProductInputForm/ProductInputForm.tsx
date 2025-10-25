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
        <form onSubmit={handleSubmit} className="space-y-8">
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
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                    <p className="text-red-600 text-sm">{errors.products}</p>
                </div>
            )}

            <div className="flex justify-end">
                <button
                    type="submit"
                    disabled={isLoading}
                    className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200"
                >
                    {isLoading ? 'Analyzing...' : 'Analyze Prices'}
                </button>
            </div>
        </form>
    );
};

export default ProductInputForm;