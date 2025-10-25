import {
  AnalysisResponse,
  LegacyAnalysisResponse,
  ProductAnalysisResult,
  LegacyPriceAnalysis,
  LegacySupplierRecommendation,
  LegacyOptimizationRecommendation,
  OptimizationRecommendation
} from '../types';

/**
 * Transform backend API response to legacy format for existing UI components
 * This allows us to maintain backward compatibility while transitioning to new API structure
 */
export const transformAnalysisResponse = (backendResponse: any): LegacyAnalysisResponse => {
  // Transform product analyses (handle snake_case from backend)
  const analyses: LegacyPriceAnalysis[] = backendResponse.product_analyses.map((productResult: any) => {
    // Transform suppliers
    const suppliers: LegacySupplierRecommendation[] = productResult.analysis.suppliers.map((supplier: any) => ({
      name: supplier.name,
      listPrice: supplier.price,
      moq: supplier.moq,
      contactInfo: supplier.contact_info,
      // Note: Backend doesn't have promotions or priceBreaks in current structure
      // These would need to be added to backend or handled differently
    }));

    // Transform optimization recommendations to simple strings for legacy format
    const recommendations: string[] = productResult.analysis.recommendations.map((rec: any) => rec.description);

    return {
      productName: productResult.product_name,
      priceRanges: {
        p10: productResult.analysis.effective_delivered_cost.p10 || 0,
        p25: productResult.analysis.effective_delivered_cost.p25 || 0,
        p35: productResult.analysis.effective_delivered_cost.p35 || 0,
        p50: productResult.analysis.effective_delivered_cost.p50 || 0,
        p90: productResult.analysis.effective_delivered_cost.p90 || 0,
      },
      effectiveCost: {
        basePrice: productResult.analysis.target_price || productResult.analysis.effective_delivered_cost.p35 || 0,
        logisticsCost: 0, // Backend doesn't separate these costs in current structure
        taxes: 0,
        wastage: 0,
        totalCost: productResult.individual_budget.total_cost,
      },
      confidenceScore: productResult.analysis.confidence_score,
      suppliers,
      recommendations,
      dataAvailability: {
        marketData: productResult.data_availability.price_data_found,
        supplierData: productResult.data_availability.supplier_data_found,
        forecastData: productResult.data_availability.forecast_data_available,
      },
    };
  });

  // Transform optimization recommendations
  const recommendations: LegacyOptimizationRecommendation[] = [];

  // Extract optimization recommendations from all products
  backendResponse.product_analyses.forEach((productResult: any) => {
    productResult.analysis.recommendations.forEach((rec: any) => {
      recommendations.push({
        type: mapOptimizationType(rec.type),
        title: getOptimizationTitle(rec.type),
        description: rec.description,
        potentialSavings: rec.potential_savings,
        confidence: rec.confidence || 0,
      });
    });
  });

  return {
    analyses,
    overallBudget: {
      totalCost: backendResponse.overall_budget.total_cost,
      potentialSavings: backendResponse.overall_budget.high - backendResponse.overall_budget.target,
      confidenceScore: backendResponse.data_quality_report.overall_data_coverage,
    },
    recommendations,
    dataQualityReport: {
      overallScore: backendResponse.data_quality_report.overall_data_coverage,
      missingDataSources: backendResponse.data_quality_report.limited_data_products,
      recommendations: [`${backendResponse.data_quality_report.no_data_products.length} products have limited data availability`],
    },
  };
};

/**
 * Map backend optimization types to legacy format
 */
const mapOptimizationType = (backendType: OptimizationRecommendation['type']): LegacyOptimizationRecommendation['type'] => {
  switch (backendType) {
    case 'TIMING':
      return 'timing';
    case 'BULK_DISCOUNT':
      return 'bulk_discount';
    case 'SEASONAL_OPTIMIZATION':
      return 'seasonal';
    case 'SUBSTITUTE':
    case 'GROUP_PURCHASE':
      return 'supplier';
    case 'SUPPLY_RISK':
    case 'ANOMALY_ALERT':
      return 'risk_alert';
    default:
      return 'supplier';
  }
};

/**
 * Generate user-friendly titles for optimization recommendations
 */
const getOptimizationTitle = (type: OptimizationRecommendation['type']): string => {
  switch (type) {
    case 'TIMING':
      return 'Optimal Purchase Timing';
    case 'BULK_DISCOUNT':
      return 'Volume Purchase Opportunity';
    case 'SEASONAL_OPTIMIZATION':
      return 'Seasonal Price Optimization';
    case 'SUBSTITUTE':
      return 'Product Substitution';
    case 'GROUP_PURCHASE':
      return 'Group Purchase Opportunity';
    case 'SUPPLY_RISK':
      return 'Supply Risk Alert';
    case 'ANOMALY_ALERT':
      return 'Price Anomaly Alert';
    default:
      return 'Optimization Opportunity';
  }
};

/**
 * Transform frontend request to backend format (camelCase to snake_case)
 */
export const transformAnalysisRequest = (frontendRequest: any): any => {
  // Handle both legacy and new request formats
  if (frontendRequest.farmInfo) {
    // Legacy format - transform to new format
    return {
      farm_location: {
        street_address: frontendRequest.farmInfo.street,
        city: frontendRequest.farmInfo.city,
        state: frontendRequest.farmInfo.state,
        county: frontendRequest.farmInfo.county || '',
        zip_code: frontendRequest.farmInfo.zipCode,
        country: frontendRequest.farmInfo.country,
      },
      products: frontendRequest.products.map((product: any) => ({
        id: product.id,
        name: product.name,
        quantity: product.quantity,
        unit: product.unit,
        specifications: product.specifications,
        preferred_brands: product.preferredBrands,
        max_price: product.maxPrice,
      })),
    };
  }

  // Transform camelCase to snake_case for backend
  return {
    farm_location: {
      street_address: frontendRequest.farmLocation.streetAddress,
      city: frontendRequest.farmLocation.city,
      state: frontendRequest.farmLocation.state,
      county: frontendRequest.farmLocation.county,
      zip_code: frontendRequest.farmLocation.zipCode,
      country: frontendRequest.farmLocation.country,
    },
    products: frontendRequest.products.map((product: any) => ({
      id: product.id,
      name: product.name,
      quantity: product.quantity,
      unit: product.unit,
      specifications: product.specifications,
      preferred_brands: product.preferredBrands,
      max_price: product.maxPrice,
    })),
  };
};