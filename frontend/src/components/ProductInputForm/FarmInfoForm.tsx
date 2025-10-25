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
    <div className="glass-card p-8 group hover:scale-[1.02] transition-all duration-300">
      <div className="flex items-center space-x-3 mb-8">
        <div className="w-12 h-12 bg-gradient-accent rounded-xl flex items-center justify-center">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">Farm Location</h2>
          <p className="text-gray-300">Enter your farm's shipping address for accurate logistics calculations</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="md:col-span-2">
          <label htmlFor="street" className="block text-sm font-medium text-gray-300 mb-3">
            Street Address *
          </label>
          <input
            type="text"
            id="street"
            value={farmInfo.location.streetAddress}
            onChange={(e) => handleChange('streetAddress', e.target.value)}
            className={`modern-input w-full ${errors.streetAddress ? 'border-red-400 bg-red-500/10' : ''}`}
            placeholder="123 Farm Road"
          />
          {errors.streetAddress && (
            <p className="mt-2 text-sm text-red-300 flex items-center space-x-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span>{errors.streetAddress}</span>
            </p>
          )}
        </div>

        <div>
          <label htmlFor="city" className="block text-sm font-medium text-gray-300 mb-3">
            City *
          </label>
          <input
            type="text"
            id="city"
            value={farmInfo.location.city}
            onChange={(e) => handleChange('city', e.target.value)}
            className={`modern-input w-full ${errors.city ? 'border-red-400 bg-red-500/10' : ''}`}
            placeholder="Springfield"
          />
          {errors.city && (
            <p className="mt-2 text-sm text-red-300 flex items-center space-x-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span>{errors.city}</span>
            </p>
          )}
        </div>

        <div>
          <label htmlFor="state" className="block text-sm font-medium text-gray-300 mb-3">
            State *
          </label>
          <input
            type="text"
            id="state"
            value={farmInfo.location.state}
            onChange={(e) => handleChange('state', e.target.value)}
            className={`modern-input w-full ${errors.state ? 'border-red-400 bg-red-500/10' : ''}`}
            placeholder="Illinois"
          />
          {errors.state && (
            <p className="mt-2 text-sm text-red-300 flex items-center space-x-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span>{errors.state}</span>
            </p>
          )}
        </div>

        <div>
          <label htmlFor="county" className="block text-sm font-medium text-gray-300 mb-3">
            County <span className="text-gray-500">(Optional)</span>
          </label>
          <input
            type="text"
            id="county"
            value={farmInfo.location.county || ''}
            onChange={(e) => handleChange('county', e.target.value)}
            className="modern-input w-full"
            placeholder="Sangamon County"
          />
        </div>

        <div>
          <label htmlFor="zipCode" className="block text-sm font-medium text-gray-300 mb-3">
            ZIP Code *
          </label>
          <input
            type="text"
            id="zipCode"
            value={farmInfo.location.zipCode}
            onChange={(e) => handleChange('zipCode', e.target.value)}
            className={`modern-input w-full ${errors.zipCode ? 'border-red-400 bg-red-500/10' : ''}`}
            placeholder="62701"
          />
          {errors.zipCode && (
            <p className="mt-2 text-sm text-red-300 flex items-center space-x-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span>{errors.zipCode}</span>
            </p>
          )}
        </div>

        <div>
          <label htmlFor="country" className="block text-sm font-medium text-gray-300 mb-3">
            Country *
          </label>
          <select
            id="country"
            value={farmInfo.location.country}
            onChange={(e) => handleChange('country', e.target.value)}
            className={`modern-input w-full ${errors.country ? 'border-red-400 bg-red-500/10' : ''}`}
          >
            <option value="United States">United States</option>
            <option value="Canada">Canada</option>
            <option value="Mexico">Mexico</option>
          </select>
          {errors.country && (
            <p className="mt-2 text-sm text-red-300 flex items-center space-x-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span>{errors.country}</span>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default FarmInfoForm;