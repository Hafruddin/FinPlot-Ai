import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestStockIntelligenceSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_stock_intelligence_unified_endpoint_tcs(self):
        """Test GET /api/stocks/TCS/intelligence returns comprehensive 20-factor report."""
        res = self.client.get("/api/stocks/TCS/intelligence")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["symbol"], "TCS")
        self.assertIn("company", data)
        self.assertIn("quote", data)
        self.assertIn("movement", data)
        self.assertIn("growth_loss", data)
        self.assertIn("technical", data)
        self.assertIn("news", data)
        self.assertIn("factors", data)
        self.assertIn("signal", data)
        self.assertIn("prediction", data)
        self.assertIn("why_moving", data)
        self.assertIn("risks", data)
        self.assertIn("sources", data)

        # Verify 20 Factors
        factors = data["factors"]
        self.assertEqual(len(factors), 20)
        factor_names = [f["name"] for f in factors]
        self.assertIn("Company Earnings", factor_names)
        self.assertIn("Currency Exchange (USD/INR)", factor_names)
        self.assertIn("Crude Oil Prices", factor_names)
        self.assertIn("Investor & Institutional Sentiment", factor_names)

        # Verify Factor Relevance Engine
        # For TCS (IT company), Crude Oil must be NOT RELEVANT and Currency must be HIGH
        for f in factors:
            if f["name"] == "Crude Oil Prices":
                self.assertEqual(f["relevance"], "NOT RELEVANT")
                self.assertEqual(f["status"], "NOT RELEVANT")
            if f["name"] == "Currency Exchange (USD/INR)":
                self.assertEqual(f["relevance"], "HIGH")

        # Verify Early Signal Engine
        sig = data["signal"]
        self.assertIn("signal", sig)
        self.assertIn("signal_score", sig)
        self.assertIn("supporting_factors", sig)
        self.assertIn("risk_factors", sig)
        self.assertIn("prediction_horizon", sig)
        self.assertIn(sig["signal"], ["EARLY BULLISH", "BULLISH", "NEUTRAL", "BEARISH", "EARLY BEARISH"])

        # Verify ML Prediction Engine & Backtesting
        pred = data["prediction"]
        self.assertIn("signal", pred)
        self.assertIn("calibrated_probability_pct", pred)
        self.assertIn("validation_metrics", pred)
        metrics = pred["validation_metrics"]
        self.assertGreater(metrics["accuracy"], 0.50)
        self.assertGreater(metrics["precision"], 0.50)
        self.assertGreater(metrics["f1_score"], 0.50)
        self.assertGreater(metrics["roc_auc"], 0.50)

    def test_stock_intelligence_for_different_sectors(self):
        """Test stocks across IT, Banking, Energy, Auto."""
        test_symbols = ["RELIANCE", "HDFCBANK", "MARUTI", "INFY"]
        for sym in test_symbols:
            res = self.client.get(f"/api/stocks/{sym}/intelligence")
            self.assertEqual(res.status_code, 200)
            d = res.json()
            self.assertEqual(d["symbol"], sym)
            self.assertEqual(len(d["factors"]), 20)
            self.assertIn("why_moving", d)
            self.assertTrue(len(d["why_moving"]["positive_contributing_factors"]) > 0 or len(d["why_moving"]["negative_contributing_factors"]) > 0)

    def test_modular_stock_subendpoints(self):
        """Verify individual endpoints defined in Part 37."""
        endpoints = [
            "/api/stocks/TCS/quote",
            "/api/stocks/TCS/company",
            "/api/stocks/TCS/financials",
            "/api/stocks/TCS/news",
            "/api/stocks/TCS/events",
            "/api/stocks/TCS/technical",
            "/api/stocks/TCS/macro",
            "/api/stocks/TCS/sector",
            "/api/stocks/TCS/regulatory",
            "/api/stocks/TCS/commodities",
            "/api/stocks/TCS/currency",
            "/api/stocks/TCS/factors",
            "/api/stocks/TCS/signal",
            "/api/stocks/TCS/prediction"
        ]
        for ep in endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 200, f"Failed endpoint: {ep}")

    def test_news_price_correlation_engine(self):
        """Ensure no illegal certainty claims ('definitely caused')."""
        res = self.client.get("/api/stocks/TCS/intelligence")
        d = res.json()
        summary = d["why_moving"]["summary"]
        self.assertNotIn("definitely", summary.lower())
        self.assertNotIn("guaranteed", summary.lower())

if __name__ == "__main__":
    unittest.main()
