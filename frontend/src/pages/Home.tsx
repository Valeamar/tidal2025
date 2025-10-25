import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to Farmer Budget Optimizer
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI-powered agricultural input price optimization system that helps farmers 
          plan their growing season expenses by finding optimal prices for agricultural inputs.
        </p>
        
        <Link 
          to="/analyze"
          className="inline-block bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors duration-200"
        >
          Start Price Analysis
        </Link>
      </div>

      <div className="grid md:grid-cols-3 gap-8 mt-16">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="text-green-600 text-3xl mb-4">📊</div>
          <h3 className="text-xl font-semibold mb-2">Price Analysis</h3>
          <p className="text-gray-600">
            Get real-time market data and price analysis for agricultural inputs 
            with confidence scores and recommendations.
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="text-green-600 text-3xl mb-4">🎯</div>
          <h3 className="text-xl font-semibold mb-2">Smart Recommendations</h3>
          <p className="text-gray-600">
            Receive AI-powered recommendations for optimal timing, suppliers, 
            and bulk purchasing opportunities.
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="text-green-600 text-3xl mb-4">💰</div>
          <h3 className="text-xl font-semibold mb-2">Budget Optimization</h3>
          <p className="text-gray-600">
            Optimize your agricultural input budget with detailed cost analysis 
            and seasonal planning insights.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Home;