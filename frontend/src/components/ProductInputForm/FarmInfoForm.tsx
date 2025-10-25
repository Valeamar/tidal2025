import React from 'react';
import { FarmInfo } from '../../types';

interface FarmInfoFormProps {
  farmInfo: FarmInfo;
  onChange: (farmInfo: FarmInfo) => void;
  errors: Record<string, string>;
}

const FarmInfoForm: React.FC<FarmInfoFormProps> = ({ farmInfo, onChange, errors }) => {
  const handleChange = (field: keyof FarmInfo['location'], value: string) => {
    onChange({
      ...farmInfo,
      location: {
        ...farmInfo.location,
        [field]: value
      }
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Farm Shipping Address</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="md:col-span-2">
          <label htmlFor="street" className="block text-sm font-medium text-gray-700 mb-2">
            Street Address *
          </label>
          <input
            type="text"
            id="street"
            value={farmInfo.location.streetAddress}
            onChange={(e) => handleChange('streetAddress', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 ${errors.streetAddress ? 'border-red-300' : 'border-gray-300'
              }`}
            placeholder="123 Farm Road"
          />
          {errors.streetAddress && (
            <p className="mt-1 text-sm text-red-600">{errors.streetAddress}</p>
          )}
        </div>

        <div>
          <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-2">
            City *
          </label>
          <input
            type="text"
            id="city"
            value={farmInfo.location.city}
            onChange={(e) => handleChange('city', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 ${errors.city ? 'border-red-300' : 'border-gray-300'
              }`}
            placeholder="Springfield"
          />
          {errors.city && (
            <p className="mt-1 text-sm text-red-600">{errors.city}</p>
          )}
        </div>

        <div>
          <label htmlFor="state" className="block text-sm font-medium text-gray-700 mb-2">
            State *
          </label>
          <input
            type="text"
            id="state"
            value={farmInfo.location.state}
            onChange={(e) => handleChange('state', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 ${errors.state ? 'border-red-300' : 'border-gray-300'
              }`}
            placeholder="Illinois"
          />
          {errors.state && (
            <p className="mt-1 text-sm text-red-600">{errors.state}</p>
          )}
        </div>

        <div>
          <label htmlFor="county" className="block text-sm font-medium text-gray-700 mb-2">
            County
          </label>
          <input
            type="text"
            id="county"
            value={farmInfo.location.county || ''}
            onChange={(e) => handleChange('county', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            placeholder="Sangamon County"
          />
        </div>

        <div>
          <label htmlFor="zipCode" className="block text-sm font-medium text-gray-700 mb-2">
            ZIP Code *
          </label>
          <input
            type="text"
            id="zipCode"
            value={farmInfo.location.zipCode}
            onChange={(e) => handleChange('zipCode', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 ${errors.zipCode ? 'border-red-300' : 'border-gray-300'
              }`}
            placeholder="62701"
          />
          {errors.zipCode && (
            <p className="mt-1 text-sm text-red-600">{errors.zipCode}</p>
          )}
        </div>

        <div>
          <label htmlFor="country" className="block text-sm font-medium text-gray-700 mb-2">
            Country *
          </label>
          <select
            id="country"
            value={farmInfo.location.country}
            onChange={(e) => handleChange('country', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 ${errors.country ? 'border-red-300' : 'border-gray-300'
              }`}
          >
            <option value="United States">United States</option>
            <option value="Canada">Canada</option>
            <option value="Mexico">Mexico</option>
          </select>
          {errors.country && (
            <p className="mt-1 text-sm text-red-600">{errors.country}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default FarmInfoForm;