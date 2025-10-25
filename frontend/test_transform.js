// Simple test to verify data transformation
const { transformAnalysisRequest } = require('./src/utils/dataTransform.ts');

// Test data that matches what the frontend form would send
const testRequest = {
  farmLocation: {
    streetAddress: "123 Farm Road",
    city: "Des Moines",
    state: "Iowa",
    county: "", // Empty county to test the fix
    zipCode: "50309",
    country: "USA"
  },
  products: [
    {
      name: "Corn Seeds",
      quantity: 100,
      unit: "bags",
      specifications: "High-yield variety"
      // Note: maxPrice and preferredBrands are not set (undefined)
    }
  ]
};

try {
  const transformed = transformAnalysisRequest(testRequest);
  console.log('✅ Transformation successful:');
  console.log(JSON.stringify(transformed, null, 2));
} catch (error) {
  console.log('❌ Transformation failed:', error.message);
}