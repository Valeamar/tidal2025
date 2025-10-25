"""
Test suite for PriceCalculator class

Tests the core functionality of price calculation and economic analysis.
"""

from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.price_calculator import PriceCalculator, PriceQuote, ProductCategory
from app.models import ProductInput, FarmLocation


class TestPriceCalculator:
    """Test cases for PriceCalculator functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = PriceCalculator()
        
        # Sample farm location
        self.farm_location = FarmLocation(
            street_address="123 Farm Road",
            city="Des Moines",
            state="IA",
            county="Polk",
            zip_code="50309",
            country="USA"
        )
        
        # Sample product input
        self.product_input = ProductInput(
            name="Corn Seed",
            quantity=100.0,
            unit="lb",
            specifications="Non-GMO hybrid"
        )
        
        # Sample price quotes
        self.sample_quotes = [
            PriceQuote(
                supplier="AgriSupply Co",
                product_name="Corn Seed Premium",
                base_price=45.50,
                unit="lb",
                moq=50,
                location="Iowa, IA",
                delivery_terms="FOB Farm",
                lead_time=7,
                reliability_score=0.9,
                purity_grade="Premium",
                pack_size="50lb bag",
                cached_at=datetime.now()
            ),
            PriceQuote(
                supplier="Farm Direct Seeds",
                product_name="Corn Seed Standard",
                base_price=42.00,
                unit="lb",
                moq=25,
                location="Illinois, IL",
                delivery_terms="Delivered",
                lead_time=14,
                reliability_score=0.8,
                purity_grade="Standard",
                pack_size="25lb bag",
                cached_at=datetime.now() - timedelta(hours=2)
            ),
            PriceQuote(
                supplier="Midwest Ag",
                product_name="Corn Seed Economy",
                base_price=38.75,
                unit="lb",
                moq=100,
                location="Nebraska, NE",
                delivery_terms="FOB Warehouse",
                lead_time=21,
                reliability_score=0.7,
                purity_grade="Economy",
                pack_size="bulk",
                cached_at=datetime.now() - timedelta(hours=6)
            )
        ]

    def test_effective_cost_calculation(self):
        """Test effective delivered cost calculation"""
        quote = self.sample_quotes[0]
        
        result = self.calculator.calculate_effective_delivered_cost(
            quote, self.farm_location, self.product_input
        )
        
        # Verify all cost components are present
        assert "base_price" in result
        assert "logistics_cost" in result
        assert "taxes_and_fees" in result
        assert "wastage_adjustment" in result
        assert "total_effective_cost" in result
        assert "cost_breakdown" in result
        
        # Verify costs are positive
        assert result["base_price"] > 0
        assert result["total_effective_cost"] > result["base_price"]
        
        # Verify cost breakdown has required components
        breakdown = result["cost_breakdown"]
        required_components = ["freight", "fuel_surcharge", "handling", "delivery_premium", 
                             "sales_tax", "regulatory_fees", "certification", "payment_processing"]
        for component in required_components:
            assert component in breakdown
            assert breakdown[component] >= 0

    def test_price_ranges_calculation(self):
        """Test price range calculation with percentiles"""
        # Calculate effective costs for all quotes
        effective_costs = []
        for quote in self.sample_quotes:
            cost_result = self.calculator.calculate_effective_delivered_cost(
                quote, self.farm_location, self.product_input
            )
            effective_costs.append(cost_result["total_effective_cost"])
        
        price_ranges = self.calculator.calculate_price_ranges(effective_costs)
        
        # Verify all percentiles are present
        assert price_ranges.p10 is not None
        assert price_ranges.p25 is not None
        assert price_ranges.p35 is not None
        assert price_ranges.p50 is not None
        assert price_ranges.p90 is not None
        
        # Verify percentiles are in ascending order
        assert price_ranges.p10 <= price_ranges.p25
        assert price_ranges.p25 <= price_ranges.p35
        assert price_ranges.p35 <= price_ranges.p50
        assert price_ranges.p50 <= price_ranges.p90

    def test_confidence_score_calculation(self):
        """Test confidence score calculation"""
        confidence = self.calculator.calculate_confidence_score(self.sample_quotes)
        
        # Confidence should be between 0 and 1
        assert 0.0 <= confidence <= 1.0
        
        # More quotes should generally give higher confidence
        single_quote_confidence = self.calculator.calculate_confidence_score([self.sample_quotes[0]])
        assert confidence >= single_quote_confidence

    def test_product_specification_analysis(self):
        """Test product specification analysis"""
        spec_analysis = self.calculator.analyze_product_specifications(
            self.product_input, self.sample_quotes
        )
        
        # Verify analysis components
        assert spec_analysis.canonical_spec is not None
        assert isinstance(spec_analysis.substitute_skus, list)
        assert spec_analysis.quality_adjustment > 0
        
        # Should identify most common purity grade
        assert spec_analysis.purity_grade in ["Premium", "Standard", "Economy"]

    def test_supplier_offer_evaluation(self):
        """Test supplier offer evaluation"""
        evaluations = self.calculator.evaluate_supplier_offers(
            self.sample_quotes, self.product_input.quantity
        )
        
        # Should return evaluation for each supplier
        assert len(evaluations) == len(self.sample_quotes)
        
        # Each evaluation should have required fields
        for eval_result in evaluations:
            assert "supplier" in eval_result
            assert "base_price" in eval_result
            assert "effective_price" in eval_result
            assert "moq_met" in eval_result
            assert "value_score" in eval_result
            
            # Value score should be between 0 and 1
            assert 0.0 <= eval_result["value_score"] <= 1.0
        
        # Results should be sorted by value score (descending)
        for i in range(len(evaluations) - 1):
            assert evaluations[i]["value_score"] >= evaluations[i + 1]["value_score"]

    def test_location_factors_calculation(self):
        """Test location factors calculation"""
        location_factors = self.calculator.calculate_location_factors(
            self.farm_location, self.sample_quotes
        )
        
        # Verify all factors are present and within reasonable ranges
        assert 0.5 <= location_factors.regional_market_density <= 1.5
        assert location_factors.distance_to_suppliers > 0
        assert 0.5 <= location_factors.local_competition_level <= 1.5
        assert 0.5 <= location_factors.transportation_infrastructure <= 1.5

    def test_seasonality_factors_calculation(self):
        """Test seasonality factors calculation"""
        seasonality = self.calculator.calculate_seasonality_factors(self.product_input)
        
        # Verify seasonality components
        assert 0.5 <= seasonality.current_season_multiplier <= 2.0
        assert 1 <= seasonality.optimal_purchase_month <= 12
        assert seasonality.seasonal_savings_potential >= 0
        assert 0.5 <= seasonality.planting_calendar_alignment <= 1.5

    def test_comprehensive_economic_analysis(self):
        """Test the main comprehensive analysis method"""
        analysis = self.calculator.perform_comprehensive_economic_analysis(
            self.product_input, self.sample_quotes, self.farm_location
        )
        
        # Verify analysis completion
        assert analysis["analysis_complete"] is True
        assert analysis["product_name"] == self.product_input.name
        
        # Verify all major analysis components are present
        required_sections = [
            "specification_analysis",
            "supplier_evaluations", 
            "location_factors",
            "seasonality_analysis",
            "price_analysis",
            "detailed_cost_breakdowns",
            "market_dynamics",
            "compliance_analysis",
            "optimization_recommendations"
        ]
        
        for section in required_sections:
            assert section in analysis
        
        # Verify price analysis has target price
        price_analysis = analysis["price_analysis"]
        assert "target_price" in price_analysis
        assert "confidence_score" in price_analysis
        assert 0.0 <= price_analysis["confidence_score"] <= 1.0
        
        # Verify optimization recommendations
        recommendations = analysis["optimization_recommendations"]
        assert isinstance(recommendations, list)
        
        # If recommendations exist, verify structure
        if recommendations:
            for rec in recommendations:
                assert "type" in rec
                assert "priority" in rec
                assert "description" in rec
                assert "potential_savings" in rec
                assert "action_required" in rec
                assert "confidence" in rec

    def test_product_categorization(self):
        """Test product categorization logic"""
        # Test different product types
        test_cases = [
            ("Corn Seed", ProductCategory.SEEDS),
            ("Nitrogen Fertilizer", ProductCategory.FERTILIZER),
            ("Herbicide Glyphosate", ProductCategory.PESTICIDES),
            ("Diesel Fuel", ProductCategory.FUEL),
            ("John Deere Tractor", ProductCategory.EQUIPMENT),
            ("Unknown Product", ProductCategory.OTHER)
        ]
        
        for product_name, expected_category in test_cases:
            category = self.calculator._categorize_product(product_name)
            assert category == expected_category

    def test_empty_quotes_handling(self):
        """Test handling of empty quote lists"""
        analysis = self.calculator.perform_comprehensive_economic_analysis(
            self.product_input, [], self.farm_location
        )
        
        # Should handle empty quotes gracefully
        assert analysis["analysis_complete"] is False
        assert "error" in analysis

    def test_outlier_removal(self):
        """Test outlier removal in price range calculation"""
        # Create data with outliers
        normal_prices = [40.0, 42.0, 41.5, 43.0, 42.5]
        outlier_prices = normal_prices + [100.0, 5.0]  # Add extreme outliers
        
        # Calculate ranges with and without outliers
        normal_ranges = self.calculator.calculate_price_ranges(normal_prices)
        outlier_ranges = self.calculator.calculate_price_ranges(outlier_prices)
        
        # Ranges should be similar (outliers removed)
        assert abs(normal_ranges.p50 - outlier_ranges.p50) < 2.0


if __name__ == "__main__":
    # Run basic functionality test
    test_calc = TestPriceCalculator()
    test_calc.setup_method()
    
    print("Testing PriceCalculator...")
    
    try:
        test_calc.test_effective_cost_calculation()
        print("✓ Effective cost calculation works")
        
        test_calc.test_price_ranges_calculation()
        print("✓ Price ranges calculation works")
        
        test_calc.test_confidence_score_calculation()
        print("✓ Confidence score calculation works")
        
        test_calc.test_comprehensive_economic_analysis()
        print("✓ Comprehensive economic analysis works")
        
        print("\nAll basic tests passed! PriceCalculator is working correctly.")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise