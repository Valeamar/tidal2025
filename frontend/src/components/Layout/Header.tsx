import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="relative z-50">
      <div className="backdrop-blur-xl bg-black/20 border-b border-white/10">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="w-10 h-10 bg-gradient-accent rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div className="text-white">
                <div className="text-xl font-bold gradient-text">FarmOptimizer</div>
                <div className="text-xs text-gray-400 -mt-1">AI-Powered Agriculture</div>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              <Link
                to="/"
                className={`relative px-4 py-2 rounded-lg transition-all duration-300 ${isActive('/')
                  ? 'text-accent-400 bg-white/10'
                  : 'text-white hover:text-accent-400 hover:bg-white/5'
                  }`}
              >
                Home
                {isActive('/') && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-accent rounded-full"></div>
                )}
              </Link>
              <Link
                to="/analyze"
                className={`relative px-4 py-2 rounded-lg transition-all duration-300 ${isActive('/analyze')
                  ? 'text-accent-400 bg-white/10'
                  : 'text-white hover:text-accent-400 hover:bg-white/5'
                  }`}
              >
                Analysis
                {isActive('/analyze') && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-accent rounded-full"></div>
                )}
              </Link>

              {/* CTA Button */}
              <Link
                to="/analyze"
                className="glass-button px-6 py-2 text-white font-semibold hover:scale-105 transition-all duration-300"
              >
                Get Started
              </Link>
            </nav>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden glass-button p-2 text-white"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-white/20">
            <div className="container mx-auto px-6 py-4 space-y-4">
              <Link
                to="/"
                onClick={() => setIsMenuOpen(false)}
                className={`block px-4 py-2 rounded-lg transition-all duration-300 ${isActive('/')
                  ? 'text-accent-400 bg-white/10'
                  : 'text-white hover:text-accent-400 hover:bg-white/5'
                  }`}
              >
                Home
              </Link>
              <Link
                to="/analyze"
                onClick={() => setIsMenuOpen(false)}
                className={`block px-4 py-2 rounded-lg transition-all duration-300 ${isActive('/analyze')
                  ? 'text-accent-400 bg-white/10'
                  : 'text-white hover:text-accent-400 hover:bg-white/5'
                  }`}
              >
                Analysis
              </Link>
              <Link
                to="/analyze"
                onClick={() => setIsMenuOpen(false)}
                className="block glass-button px-4 py-2 text-white font-semibold text-center"
              >
                Get Started
              </Link>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;