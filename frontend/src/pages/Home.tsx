import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Floating Particles Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 bg-accent-400 rounded-full opacity-20 animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 6}s`,
              animationDuration: `${6 + Math.random() * 4}s`
            }}
          />
        ))}
      </div>

      {/* Hero Section */}
      <div className="relative z-10 container mx-auto px-6 pt-20 pb-32">
        <div className={`text-center transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          {/* Main Heading */}
          <div className="mb-8">
            <h1 className="text-6xl md:text-8xl font-bold mb-6 leading-tight">
              <span className="gradient-text">Farmer</span>
              <br />
              <span className="text-white">Budget</span>
              <br />
              <span className="gradient-text">Optimizer</span>
            </h1>
            <div className="w-24 h-1 bg-gradient-accent mx-auto mb-8 rounded-full"></div>
          </div>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed">
            Revolutionary AI-powered agricultural intelligence platform that transforms
            how farmers optimize their input costs and maximize profitability through
            <span className="text-accent-400 font-semibold"> real-time market analysis</span>.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
            <Link
              to="/analyze"
              className="group relative px-8 py-4 bg-gradient-accent text-white font-bold text-lg rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-glow-lg overflow-hidden"
            >
              <span className="relative z-10">Start Analysis</span>
              <div className="absolute inset-0 bg-gradient-to-r from-accent-600 to-primary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </Link>

            <button className="glass-button px-8 py-4 text-white font-semibold text-lg group">
              <span className="flex items-center gap-3">
                <svg className="w-6 h-6 group-hover:scale-110 transition-transform" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
                Watch Demo
              </span>
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="glass-card p-6 text-center group hover:scale-105 transition-all duration-300">
              <div className="text-3xl font-bold gradient-text mb-2">$2.5M+</div>
              <div className="text-gray-300">Savings Generated</div>
            </div>
            <div className="glass-card p-6 text-center group hover:scale-105 transition-all duration-300">
              <div className="text-3xl font-bold gradient-text mb-2">10,000+</div>
              <div className="text-gray-300">Farms Optimized</div>
            </div>
            <div className="glass-card p-6 text-center group hover:scale-105 transition-all duration-300">
              <div className="text-3xl font-bold gradient-text mb-2">98%</div>
              <div className="text-gray-300">Accuracy Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="relative z-10 container mx-auto px-6 pb-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Next-Generation <span className="gradient-text">Agricultural Intelligence</span>
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Harness the power of AI, real-time market data, and predictive analytics
            to make smarter purchasing decisions.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Feature 1 */}
          <div className="glass-card p-8 group hover:scale-105 transition-all duration-500 slide-in-left">
            <div className="relative mb-6">
              <div className="w-16 h-16 bg-gradient-accent rounded-2xl flex items-center justify-center mb-4 group-hover:rotate-12 transition-transform duration-300">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-4">Real-Time Price Analysis</h3>
              <p className="text-gray-300 leading-relaxed">
                Advanced algorithms analyze thousands of data points across multiple markets
                to provide instant, accurate pricing intelligence with confidence scoring.
              </p>
            </div>
            <div className="flex items-center text-accent-400 font-semibold group-hover:translate-x-2 transition-transform">
              Learn More
              <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>

          {/* Feature 2 */}
          <div className="glass-card p-8 group hover:scale-105 transition-all duration-500 slide-in-up" style={{ animationDelay: '0.2s' }}>
            <div className="relative mb-6">
              <div className="w-16 h-16 bg-gradient-accent rounded-2xl flex items-center justify-center mb-4 group-hover:rotate-12 transition-transform duration-300">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-4">AI-Powered Recommendations</h3>
              <p className="text-gray-300 leading-relaxed">
                Machine learning models trained on agricultural market patterns deliver
                personalized optimization strategies for timing, suppliers, and quantities.
              </p>
            </div>
            <div className="flex items-center text-accent-400 font-semibold group-hover:translate-x-2 transition-transform">
              Learn More
              <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>

          {/* Feature 3 */}
          <div className="glass-card p-8 group hover:scale-105 transition-all duration-500 slide-in-right" style={{ animationDelay: '0.4s' }}>
            <div className="relative mb-6">
              <div className="w-16 h-16 bg-gradient-accent rounded-2xl flex items-center justify-center mb-4 group-hover:rotate-12 transition-transform duration-300">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-4">Budget Optimization</h3>
              <p className="text-gray-300 leading-relaxed">
                Comprehensive cost analysis including logistics, taxes, and wastage factors
                to maximize your ROI and minimize unexpected expenses.
              </p>
            </div>
            <div className="flex items-center text-accent-400 font-semibold group-hover:translate-x-2 transition-transform">
              Learn More
              <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="relative z-10 container mx-auto px-6 pb-20 text-center">
        <div className="glass-card p-12 max-w-4xl mx-auto">
          <h3 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to <span className="gradient-text">Transform</span> Your Farm's Profitability?
          </h3>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of farmers who have already optimized their input costs and increased their margins.
          </p>
          <Link
            to="/analyze"
            className="inline-block px-12 py-4 bg-gradient-accent text-white font-bold text-xl rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-glow-lg pulse-glow"
          >
            Start Your Analysis Now
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;