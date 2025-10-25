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
export const transformAnalysisResponse = (backendResponse: AnalysisResponse): LegacyAnalysisResponse => {
  // Transform product analyses
  const analyses: LegacyPriceAnalysis[] = backendResponse.productAnalyses.map((productResult: ProductAnalysisResult) => {
    // Transform suppliers
    const suppliers: LegacySupplierRecommendation[] = productResult.analysis.suppliers.map(supplier => ({
      name: supplier.name,
      listPrice: supplier.price,
      moq: supplier.moq,
      contactInfo: supplier.contactInfo,
      // Note: Backend doesn't have promotions or priceBreaks in current structure
      // These would need to be added to backend or handled differently
    }));

    // Transform optimization recommendations to simple strings for legacy format
    const recommendations: string[] = productResult.analysis.recommendations.map(rec => rec.description);

    return {
      productName: productResult.productName,
      priceRanges: {
        p10: productResult.analysis.effectiveDeliveredCost.p10 || 0,
        p25: productResult.analysis.effectiveDeliveredCost.p25 || 0,
        p35: productResult.analysis.effectiveDeliveredCost.p35 || 0,
        p50: productResult.analysis.effectiveDeliveredCost.p50 || 0,
        p90: productResult.analysis.effectiveDeliveredCost.p90 || 0,
      },
      effectiveCost: {
        basePrice: productResult.analysis.targetPrice || productResult.analysis.effectiveDeliveredCost.p35 || 0,
        logisticsCost: 0, // Backend doesn't separate these costs in current structure
        taxes: 0,
        wastage: 0,
        totalCost: productResult.individualBudget.totalCost,
      },
      confidenceScore: productResult.analysis.confidenceScore,
      suppliers,
      recommendations,
      dataAvailability: {
        marketData: productResult.dataAvailability.priceDataFound,
        supplierData: productResult.dataAvailability.supplierDataFound,
        forecastData: productResult.dataAvailability.forecastDataAvailable,
      },
    };
  });

  // Transform optimization recommendations
  const recommendations: LegacyOptimizationRecommendation[] = [];
  
  // Extract optimization recommendations from all products
  backendResponse.productAnalyses.forEach(productResult => {
    productResult.analysis.recommendations.forEach(rec => {
      recommendations.push({
        type: mapOptimizationType(rec.type),
        title: getOptimizationTitle(rec.type),
        description: rec.description,
        potentialSavings: rec.potentialSavings,
        confidence: rec.confidence || 0,
      });
    });
  });

  return {
    analyses,
    overallBudget: {
      totalCost: backendResponse.overallBudget.totalCost,
      potentialSavings: backendResponse.overallBudget.high - backendResponse.overallBudget.target,
      confidenceScore: backendResponse.dataQualityReport.overallDataCoverage,
    },
    recommendations,
    dataQualityReport: {
      overallScore: backendResponse.dataQualityReport.overallDataCoverage,
      missingDataSources: backendResponse.dataQualityReport.limitedDataProducts,
      recommendations: [`${backendResponse.dataQualityReport.noDataProducts.length} products have limited data availability`],
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
 * Transform frontend request to backend format
 */
export const transformAnalysisRequest = (frontendRequest: any): any => {
  // Handle both legacy and new request formats
  if (frontendRequest.farmInfo) {
    // Legacy format - transform to new format
    return {
      farmLocation: {
        streetAddress: frontendRequest.farmInfo.street,
        city: frontendRequest.farmInfo.city,
        state: frontendRequest.farmInfo.state,
        county: frontendRequest.farmInfo.county || '',
        zipCode: frontendRequest.farmInfo.zipCode,
        country: frontendRequest.farmInfo.country,
      },
      products: frontendRequest.products,
    };
  }
  
  // Already in new format
  return frontendRequest;
};