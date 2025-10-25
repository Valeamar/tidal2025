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
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Agricultural Products</h2>
        <button
          type="button"
          onClick={addProduct}
          className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700 transition-colors duration-200"
        >
          + Add Product
        </button>
      </div>

      <div className="space-y-6">
        {products.map((product, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-800">Product {index + 1}</h3>
              {products.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeProduct(index)}
                  className="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Remove
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="lg:col-span-2">
                <label htmlFor={`product-name-${index}`} className="block text-sm font-medium text-gray-700 mb-2">
                  Product Name *
                </label>
                <input
                  type="text"
                  id={`product-name-${index}`}
                  value={product.name}
                  onChange={(e) => updateProduct(index, 'name', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 ${
                    errors[`product_${index}_name`] ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="e.g., Corn Seed, Fertilizer, Pesticide"
                />
                {errors[`product_${index}_name`] && (
                  <p className="mt-1 text-sm text-red-600">{errors[`product_${index}_name`]}</p>
                )}
              </div>

              <div>
                <label htmlFor={`product-quantity-${index}`} className="block text-sm font-medium text-gray-700 mb-2">
                  Quantity *
                </label>
                <input
                  type="number"
                  id={`product-quantity-${index}`}
                  value={product.quantity || ''}
                  onChange={(e) => updateProduct(index, 'quantity', parseFloat(e.target.value) || 0)}
                  min="0"
                  step="0.01"
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 ${
                    errors[`product_${index}_quantity`] ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="100"
                />
                {errors[`product_${index}_quantity`] && (
                  <p className="mt-1 text-sm text-red-600">{errors[`product_${index}_quantity`]}</p>
                )}
              </div>

              <div>
                <label htmlFor={`product-unit-${index}`} className="block text-sm font-medium text-gray-700 mb-2">
                  Unit *
                </label>
                <select
                  id={`product-unit-${index}`}
                  value={product.unit}
                  onChange={(e) => updateProduct(index, 'unit', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 ${
                    errors[`product_${index}_unit`] ? 'border-red-300' : 'border-gray-300'
                  }`}
                >
                  <option value="">Select unit</option>
                  {commonUnits.map(unit => (
                    <option key={unit} value={unit}>{unit}</option>
                  ))}
                </select>
                {errors[`product_${index}_unit`] && (
                  <p className="mt-1 text-sm text-red-600">{errors[`product_${index}_unit`]}</p>
                )}
              </div>

              <div className="lg:col-span-4">
                <label htmlFor={`product-specs-${index}`} className="block text-sm font-medium text-gray-700 mb-2">
                  Specifications (Optional)
                </label>
                <textarea
                  id={`product-specs-${index}`}
                  value={product.specifications || ''}
                  onChange={(e) => updateProduct(index, 'specifications', e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  placeholder="e.g., Organic certified, 10-10-10 NPK ratio, Round-up ready variety"
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 text-sm text-gray-600">
        <p>* Required fields</p>
        <p className="mt-1">
          Add all agricultural inputs you need for your growing season. Include seeds, fertilizers, 
          pesticides, equipment, and any other supplies.
        </p>
      </div>
    </div>
  );
};

export default ProductListForm;