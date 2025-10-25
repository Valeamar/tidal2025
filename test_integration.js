// Simple integration test for frontend-backend communication
const axios = require('axios');

const BACKEND_URL = 'http://localhost:8000/api';
const FRONTEND_URL = 'http://localhost:3000';

async function testBackendHealth() {
  try {
    console.log('Testing backend health endpoint...');
    const response = await axios.get(`${BACKEND_URL}/health`);
    console.log('✅ Backend health check passed:', response.data);
    return true;
  } catch (error) {
    console.log('❌ Backend health check failed:', error.message);
    return false;
  }
}

async function testBackendAnalyze() {
  try {
    console.log('Testing backend analyze endpoint...');
    
    const testRequest = {
      products: [
        {
          name: "Corn Seeds",
          quantity: 100,
          max_price: 150.0,
          urgency: "medium"
        }
      ],
      farm_location: {
        state: "Iowa",
        county: "Polk",
        zip_code: "50309"
      }
    };
    
    const response = await axios.post(`${BACKEND_URL}/analyze`, testRequest);
    console.log('✅ Backend analyze endpoint passed');
    console.log('Response structure:', {
      product_analyses: response.data.product_analyses?.length || 0,
      overall_budget: !!response.data.overall_budget,
      data_quality_report: !!response.data.data_quality_report
    });
    return true;
  } catch (error) {
    console.log('❌ Backend analyze endpoint failed:', error.response?.data || error.message);
    return false;
  }
}

async function testFrontendAccess() {
  try {
    console.log('Testing frontend accessibility...');
    const response = await axios.get(FRONTEND_URL, { timeout: 5000 });
    console.log('✅ Frontend is accessible');
    return true;
  } catch (error) {
    console.log('❌ Frontend access failed:', error.message);
    return false;
  }
}

async function runIntegrationTests() {
  console.log('🚀 Starting integration tests...\n');
  
  const backendHealth = await testBackendHealth();
  console.log('');
  
  const backendAnalyze = await testBackendAnalyze();
  console.log('');
  
  const frontendAccess = await testFrontendAccess();
  console.log('');
  
  console.log('📊 Test Results:');
  console.log(`Backend Health: ${backendHealth ? '✅' : '❌'}`);
  console.log(`Backend Analyze: ${backendAnalyze ? '✅' : '❌'}`);
  console.log(`Frontend Access: ${frontendAccess ? '✅' : '❌'}`);
  
  const allPassed = backendHealth && backendAnalyze && frontendAccess;
  console.log(`\n${allPassed ? '🎉' : '⚠️'} Integration test ${allPassed ? 'PASSED' : 'FAILED'}`);
  
  if (allPassed) {
    console.log('\n✨ Your frontend and backend are successfully integrated!');
    console.log('🌐 Frontend: http://localhost:3000');
    console.log('🔧 Backend API: http://localhost:8000/api');
    console.log('📚 API Docs: http://localhost:8000/docs');
  }
}

// Run the tests
runIntegrationTests().catch(console.error);