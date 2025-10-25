// Core data types for the Farmer Budget Optimizer

export interface ProductInput {
  name: string;
  quantity: number;
  unit: string;
  specifications?: string;
}

export interface FarmInfo {
  street: string;
  city: string;
  state: string;
  county?: string;
  zipCode: string;
  country: string;
}

export interface PriceRanges {
  p10: number;
  p25: number;
  p35: number;
  p50: number;
  p90: number;
}

export interface EffectiveCost {
  basePrice: number;
  logisticsCost: number;
  taxes: number;
  wastage: number;
  totalCost: number;
}

export interface SupplierRecommendation {
  name: string;
  listPrice?: number;
  promotions?: string[];
  moq?: number;
  priceBreaks?: Array<{
    quantity: number;
    price: number;
  }>;
  contactInfo?: string;
}

export interface PriceAnalysis {
  productName: string;
  priceRanges: PriceRanges;
  effectiveCost: EffectiveCost;
  confidenceScore: number;
  suppliers: SupplierRecommendation[];
  recommendations: string[];
  dataAvailability: {
    marketData: boolean;
    supplierData: boolean;
    forecastData: boolean;
  };
}

export interface OptimizationRecommendation {
  type: 'timing' | 'bulk_discount' | 'seasonal' | 'supplier' | 'risk_alert';
  title: string;
  description: string;
  potentialSavings?: number;
  confidence: number;
}

export interface AnalysisRequest {
  farmInfo: FarmInfo;
  products: ProductInput[];
}

export interface AnalysisResponse {
  analyses: PriceAnalysis[];
  overallBudget: {
    totalCost: number;
    potentialSavings: number;
    confidenceScore: number;
  };
  recommendations: OptimizationRecommendation[];
  dataQualityReport: {
    overallScore: number;
    missingDataSources: string[];
    recommendations: string[];
  };
}