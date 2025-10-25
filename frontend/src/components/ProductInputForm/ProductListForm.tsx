import React from 'react';
import { ProductInput } from '../../types';

interface ProductListFormProps {
  products: ProductInput[];
  onChange: (products: ProductInput[]) => void;
  errors: Record<string, string>;
}

const ProductListForm: React.FC<ProductListFormProps> = ({ products, onChange, errors }) => {
  const addProduct = () => {
    onChange([...products, { name: '', quantity: 0, unit: '', specifications: '' }]);
  };

  const removeProduct = (index: number) => {
    if (products.length > 1) {
      const newProducts = products.filter((_, i) => i !== index);
      onChange(newProducts);
    }
  };

  const updateProduct = (index: number, field: keyof ProductInput, value: string | number) => {
    const newProducts = [...products];
    newProducts[index] = {
      ...newProducts[index],
      [field]: value
    };
    onChange(newProducts);
  };

  const commonUnits = [
    'lbs', 'kg', 'tons', 'gallons', 'liters', 'bags', 'boxes', 'cases', 'acres', 'hectares'
  ];

  return (
    <div className="glass-card p-8 group hover:scale-[1.02] transition-all duration-300">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-accent rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Agricultural Products</h2>
            <p className="text-gray-300">Add all inputs you need for your growing season</p>
          </div>
        </div>
        <button
          type="button"
          onClick={addProduct}
          className="glass-button px-6 py-3 text-white font-semibold hover:scale-105 transition-all duration-300 flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span>Add Product</span>
        </button>
      </div>

      <div className="space-y-6">
        {products.map((product, index) => (
          <div key={index} className="glass-card p-6 border-white/10 hover:border-accent-400/30 transition-all duration-300">
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-accent rounded-lg flex items-center justify-center text-white font-bold text-sm">
                  {index + 1}
                </div>
                <h3 className="text-lg font-semibold text-white">Product {index + 1}</h3>
              </div>
              {products.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeProduct(index)}
                  className="glass-button px-4 py-2 text-red-300 hover:text-red-200 hover:bg-red-500/20 transition-all duration-300 flex items-center space-x-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  <span>Remove</span>
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="lg:col-span-2">
                <label htmlFor={`product-name-${index}`} className="block text-sm font-medium text-gray-300 mb-3">
                  Product Name *
                </label>
                <input
                  type="text"
                  id={`product-name-${index}`}
                  value={product.name}
                  onChange={(e) => updateProduct(index, 'name', e.target.value)}
                  className={`modern-input w-full ${errors[`product_${index}_name`] ? 'border-red-400 bg-red-500/10' : ''
                    }`}
                  placeholder="e.g., Corn Seed, Fertilizer, Pesticide"
                />
                {errors[`product_${index}_name`] && (
                  <p className="mt-2 text-sm text-red-300 flex items-center space-x-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <span>{errors[`product_${index}_name`]}</span>
                  </p>
                )}
              </div>

              <div>
                <label htmlFor={`product-quantity-${index}`} className="block text-sm font-medium text-gray-300 mb-3">
                  Quantity *
                </label>
                <input
                  type="number"
                  id={`product-quantity-${index}`}
                  value={product.quantity || ''}
                  onChange={(e) => updateProduct(index, 'quantity', parseFloat(e.target.value) || 0)}
                  min="0"
                  step="0.01"
                  className={`modern-input w-full ${errors[`product_${index}_quantity`] ? 'border-red-400 bg-red-500/10' : ''
                    }`}
                  placeholder="100"
                />
                {errors[`product_${index}_quantity`] && (
                  <p className="mt-2 text-sm text-red-300 flex items-center space-x-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <span>{errors[`product_${index}_quantity`]}</span>
                  </p>
                )}
              </div>

              <div>
                <label htmlFor={`product-unit-${index}`} className="block text-sm font-medium text-gray-300 mb-3">
                  Unit *
                </label>
                <select
                  id={`product-unit-${index}`}
                  value={product.unit}
                  onChange={(e) => updateProduct(index, 'unit', e.target.value)}
                  className={`modern-input w-full ${errors[`product_${index}_unit`] ? 'border-red-400 bg-red-500/10' : ''
                    }`}
                >
                  <option value="">Select unit</option>
                  {commonUnits.map(unit => (
                    <option key={unit} value={unit}>{unit}</option>
                  ))}
                </select>
                {errors[`product_${index}_unit`] && (
                  <p className="mt-2 text-sm text-red-300 flex items-center space-x-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <span>{errors[`product_${index}_unit`]}</span>
                  </p>
                )}
              </div>

              <div className="lg:col-span-4">
                <label htmlFor={`product-specs-${index}`} className="block text-sm font-medium text-gray-300 mb-3">
                  Specifications <span className="text-gray-500">(Optional)</span>
                </label>
                <textarea
                  id={`product-specs-${index}`}
                  value={product.specifications || ''}
                  onChange={(e) => updateProduct(index, 'specifications', e.target.value)}
                  rows={3}
                  className="modern-input w-full resize-none"
                  placeholder="e.g., Organic certified, 10-10-10 NPK ratio, Round-up ready variety"
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 glass-card p-6 border-accent-400/20">
        <div className="flex items-start space-x-3">
          <svg className="w-5 h-5 text-accent-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div>
            <p className="text-gray-300 font-medium">* Required fields</p>
            <p className="mt-2 text-gray-400 text-sm leading-relaxed">
              Add all agricultural inputs you need for your growing season. Include seeds, fertilizers,
              pesticides, equipment, and any other supplies. Our AI will analyze market data to find
              the best prices and optimization opportunities.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductListForm;