import unittest
import numpy as np
import pandas as pd
from scraper import slugify, extract_slug_from_url, normalize_furniture, normalize_room_type
from app import get_mode, get_fair_price, compute_property_value_scores, classify_competitiveness

class TestSpeedhomeApp(unittest.TestCase):
    
    def test_slugify(self):
        """Test slug generation helper"""
        self.assertEqual(slugify("Mont Kiara, KL"), "mont-kiara-kl")
        self.assertEqual(slugify("  Bangsar  "), "bangsar")
        self.assertEqual(slugify("Subang_Jaya!!!"), "subang-jaya")

    def test_extract_slug_from_url(self):
        """Test slug extraction from Speedhome URLs"""
        slug, page = extract_slug_from_url("https://speedhome.com/rent/mont-kiara?page=3")
        self.assertEqual(slug, "mont-kiara")
        self.assertEqual(page, 3)
        
        slug2, page2 = extract_slug_from_url("https://speedhome.com/sewa/bangsar")
        self.assertEqual(slug2, "bangsar")
        self.assertEqual(page2, 1)

    def test_normalize_furniture(self):
        """Test furnishing data normalization"""
        self.assertEqual(normalize_furniture("FULLY_FURNISHED"), "Fully Furnished")
        self.assertEqual(normalize_furniture("partially furnished"), "Partially Furnished")
        self.assertEqual(normalize_furniture(None), "Unfurnished")
        self.assertEqual(normalize_furniture(""), "Unfurnished")

    def test_normalize_room_type(self):
        """Test room type categorization based on bedrooms and descriptions"""
        self.assertEqual(normalize_room_type(0, "STUDIO"), "Studio")
        self.assertEqual(normalize_room_type(2, "CONDO"), "2 BR")
        self.assertEqual(normalize_room_type(None, None), "N/A")

    def test_get_mode(self):
        """Test statistical mode aggregator"""
        prices = pd.Series([1500, 1800, 1500, 2000, 1500])
        self.assertEqual(get_mode(prices), 1500)

    def test_get_fair_price(self):
        """Test Fair Price weighted calculation formula"""
        # Fair Price = (Median * 0.7) + (Mean * 0.3)
        prices = pd.Series([1000, 1500, 2000, 2500, 3000])  # Median = 2000, Mean = 2000
        self.assertEqual(get_fair_price(prices), 2000)

    def test_compute_property_value_scores(self):
        """Test multi-metric property investment scoring algorithm"""
        metrics_a = {
            'yield': 5.5,
            'rent_per_sqft': 2.0,
            'volume': 100,
            'size': 1000
        }
        metrics_b = {
            'yield': 4.5,
            'rent_per_sqft': 3.0,
            'volume': 50,
            'size': 800
        }
        score_a, score_b = compute_property_value_scores(metrics_a, metrics_b)
        self.assertTrue(score_a > score_b)
        self.assertEqual(score_a, 100)  # Area A dominates all metrics, should score 100

    def test_classify_competitiveness(self):
        """Test price competitiveness status generator"""
        # Deviasi = ((Mean - Fair) / Fair) * 100
        status, color = classify_competitiveness(900, 1000)  # Deviasi = -10% (Undervalued)
        self.assertEqual(status, "🟢 Undervalued")

if __name__ == '__main__':
    unittest.main()
