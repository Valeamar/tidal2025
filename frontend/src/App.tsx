import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Home from './pages/Home';
import PriceAnalysis from './pages/PriceAnalysis';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analyze" element={<PriceAnalysis />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;