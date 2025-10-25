import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <header className="bg-green-600 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <div className="text-white text-xl font-bold">
              🌾 Farmer Budget Optimizer
            </div>
          </Link>
          
          <nav className="hidden md:flex space-x-6">
            <Link 
              to="/" 
              className="text-white hover:text-green-200 transition-colors duration-200"
            >
              Home
            </Link>
            <Link 
              to="/analyze" 
              className="text-white hover:text-green-200 transition-colors duration-200"
            >
              Price Analysis
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;