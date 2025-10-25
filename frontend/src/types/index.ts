// Core data interfaces for the Farmer Budget Optimizer

export interface ProductInput {
  id?: string;
  name: string;
  quantity: number;
  unit: string;
  specifications?: string;
  preferredBrands?: string[];
  maxPrice?: number;
}

export interface FarmInfo {
  location: {
    streetAddress: string;
    city: string;
    state: string;
    county: string;
    zipCode: string;
    country: string;
  };
  farmSize?: number;
  cropTypes?: string[];
}

export interface EffectiveCost {
  p10?: number;
  p25?: number;
  p35?: number;
  p50?: number;
  p90?: number;
}

export interface SupplierRecommendation {
  name: string;
  price: number;
  deliveryTerms?: string;
  leadTime?: number;
  reliability?: number;
  moq?: number;
  contactInfo?: string;
  location?: string;
}

export interface OptimizationRecommendation {
  type: 'BULK_DISCOUNT' | 'TIMING' | 'SUBSTITUTE' | 'GROUP_PURCHASE' | 'SEASONAL_OPTIMIZATION' | 'SUPPLY_RISK' | 'ANOMALY_ALERT';
  description: string;
  potentialSavings: number;
  actionRequired: string;
  confidence?: number;
}

export interface PriceAnalysis {
  productId: string;
  productName: string;
  effectiveDeliveredCost: EffectiveCost;
  targetPrice?: number;
  confidenceScore: number;
  suppliers: SupplierRecommendation[];
  recommendations: OptimizationRecommendation[];
  dataLimitations: string[];
}

export interface IndividualBudget {
  low: number;
  target: number;
  high: number;
  totalCost: number;
}

export interface DataAvailability {
  priceDataFound: boolean;
  supplierDataFound: boolean;
  forecastDataAvailable: boolean;
  sentimentDataAvailable: boolean;
  missingDataSections: string[];
}

export interface ProductAnalysisResult {
  productId: string;
  productName: string;
  analysis: PriceAnalysis;
  individualBudget: IndividualBudget;
  dataAvailability: DataAvailability;
}

export interface OverallBudget {
  low: number;
  target: number;
  high: number;
  totalCost: number;
}

export interface DataQualityReport {
  overallDataCoverage: number;
  reliableProducts: string[];
  limitedDataProducts: string[];
  noDataProducts: string[];
}

// API Request/Response interfaces
export interface AnalyzeRequest {
  farmLocation: {
    streetAddress: string;
    city: string;
    state: string;
    county: string;
    zipCode: string;
    country: string;
  };
  products: Array<{
    name: string;
    quantity: number;
    unit: string;
    specifications?: string;
  }>;
}

export interface AnalyzeResponse {
  productAnalyses: ProductAnalysisResult[];
  overallBudget: OverallBudget;
  dataQualityReport: DataQualityReport;
  generatedAt: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
}

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
    retryable: boolean;
  };
  requestId?: string;
  timestamp: string;
}