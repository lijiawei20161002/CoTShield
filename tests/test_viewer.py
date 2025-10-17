"""
Integration tests for Web Viewer API
Tests FastAPI endpoints and database operations
"""

import unittest
import json
import os
import tempfile
from fastapi.testclient import TestClient
from ui.viewer import app, init_db


class TestViewerAPI(unittest.TestCase):
    """Test viewer API endpoints"""

    @classmethod
    def setUpClass(cls):
        """Set up test database and client"""
        # Create temporary database for testing
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        cls.db_path = cls.temp_db.name
        cls.temp_db.close()

        # Override database path
        os.environ['COTSHIELD_DB_PATH'] = cls.db_path

        # Initialize database
        init_db()

        # Create test client
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        if os.path.exists(cls.db_path):
            os.unlink(cls.db_path)

    def test_root_endpoint(self):
        """Test GET / returns HTML viewer page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("CoTShield", response.text)

    def test_analyze_endpoint(self):
        """Test POST /api/analyze creates new trace"""
        payload = {
            "task": "Test task",
            "reasoning": "Let me think about this carefully.",
            "output": "Here is the answer.",
            "model_name": "test-model",
            "sensitivity": 0.5
        }

        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("trace_id", data)
        self.assertIn("risk_score", data)
        self.assertIn("flag_count", data)
        self.assertIn("flags", data)
        self.assertIn("severity_distribution", data)

        # Verify trace_id is returned
        self.assertIsInstance(data["trace_id"], str)
        self.assertGreater(len(data["trace_id"]), 0)

    def test_analyze_with_minimal_data(self):
        """Test analysis with minimal required fields"""
        payload = {
            "reasoning": "Simple reasoning",
            "output": "Simple output"
        }

        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("trace_id", data)
        self.assertIn("risk_score", data)

    def test_analyze_missing_fields(self):
        """Test analysis with missing required fields"""
        payload = {
            "reasoning": "Only reasoning provided"
        }

        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 422)  # Validation error

    def test_get_traces_endpoint(self):
        """Test GET /api/traces returns trace list"""
        # First create a trace
        payload = {
            "task": "List test",
            "reasoning": "Test reasoning",
            "output": "Test output",
            "sensitivity": 0.5
        }
        create_response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(create_response.status_code, 200)

        # Then get list
        response = self.client.get("/api/traces")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        # Check trace structure
        trace = data[0]
        self.assertIn("id", trace)
        self.assertIn("task", trace)
        self.assertIn("risk_score", trace)
        self.assertIn("flag_count", trace)
        self.assertIn("created_at", trace)

    def test_get_specific_trace(self):
        """Test GET /api/traces/{trace_id} returns specific trace"""
        # Create a trace
        payload = {
            "task": "Specific trace test",
            "reasoning": "Detailed reasoning here",
            "output": "Detailed output here",
            "model_name": "test-model-v1",
            "sensitivity": 0.7
        }
        create_response = self.client.post("/api/analyze", json=payload)
        trace_id = create_response.json()["trace_id"]

        # Get specific trace
        response = self.client.get(f"/api/traces/{trace_id}")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["id"], trace_id)
        self.assertEqual(data["task"], "Specific trace test")
        self.assertEqual(data["model_name"], "test-model-v1")
        self.assertIn("analysis", data)

    def test_get_nonexistent_trace(self):
        """Test GET /api/traces/{trace_id} with invalid ID"""
        response = self.client.get("/api/traces/nonexistent-id-12345")
        self.assertEqual(response.status_code, 404)

        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("not found", data["detail"].lower())

    def test_delete_trace(self):
        """Test DELETE /api/traces/{trace_id} removes trace"""
        # Create a trace
        payload = {
            "task": "Delete test",
            "reasoning": "To be deleted",
            "output": "Will be removed",
            "sensitivity": 0.5
        }
        create_response = self.client.post("/api/analyze", json=payload)
        trace_id = create_response.json()["trace_id"]

        # Delete trace
        delete_response = self.client.delete(f"/api/traces/{trace_id}")
        self.assertEqual(delete_response.status_code, 200)

        data = delete_response.json()
        self.assertIn("message", data)
        self.assertIn("deleted", data["message"].lower())

        # Verify trace is gone
        get_response = self.client.get(f"/api/traces/{trace_id}")
        self.assertEqual(get_response.status_code, 404)

    def test_delete_nonexistent_trace(self):
        """Test DELETE /api/traces/{trace_id} with invalid ID"""
        response = self.client.delete("/api/traces/nonexistent-id-67890")
        self.assertEqual(response.status_code, 404)

    def test_export_single_trace(self):
        """Test GET /api/traces/{trace_id}/export exports JSON"""
        # Create a trace
        payload = {
            "task": "Export test",
            "reasoning": "Export this trace",
            "output": "Export output",
            "sensitivity": 0.6
        }
        create_response = self.client.post("/api/analyze", json=payload)
        trace_id = create_response.json()["trace_id"]

        # Export trace
        response = self.client.get(f"/api/traces/{trace_id}/export")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response.headers["content-type"])
        self.assertIn("attachment", response.headers["content-disposition"])

        # Verify JSON structure
        data = response.json()
        self.assertEqual(data["id"], trace_id)
        self.assertIn("analysis", data)

    def test_export_all_traces(self):
        """Test POST /api/traces/export-all exports all traces"""
        # Create multiple traces
        for i in range(3):
            payload = {
                "task": f"Bulk export test {i}",
                "reasoning": f"Reasoning {i}",
                "output": f"Output {i}",
                "sensitivity": 0.5
            }
            self.client.post("/api/analyze", json=payload)

        # Export all
        response = self.client.post("/api/traces/export-all")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response.headers["content-type"])
        self.assertIn("attachment", response.headers["content-disposition"])

        # Verify JSON array
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 3)


class TestAnalysisIntegration(unittest.TestCase):
    """Test integration between viewer and analysis logic"""

    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        cls.db_path = cls.temp_db.name
        cls.temp_db.close()
        os.environ['COTSHIELD_DB_PATH'] = cls.db_path
        init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        if os.path.exists(cls.db_path):
            os.unlink(cls.db_path)

    def test_divergence_detection_via_api(self):
        """Test that API correctly runs divergence detection"""
        payload = {
            "task": "What is the capital?",
            "reasoning": "The capital is definitely not Paris.",
            "output": "The capital is Paris.",
            "sensitivity": 0.7
        }

        response = self.client.post("/api/analyze", json=payload)
        data = response.json()

        # Should detect contradiction
        self.assertGreater(data["flag_count"], 0)
        self.assertGreater(data["risk_score"], 0.0)

        # Check flags contain divergence info
        flags = data["flags"]
        self.assertGreater(len(flags), 0)
        self.assertIn("divergence_type", flags[0])
        self.assertIn("severity", flags[0])

    def test_clean_trace_via_api(self):
        """Test that clean traces produce low risk scores"""
        payload = {
            "task": "Calculate 2+2",
            "reasoning": "Two plus two equals four, based on arithmetic.",
            "output": "The answer is 4.",
            "sensitivity": 0.5
        }

        response = self.client.post("/api/analyze", json=payload)
        data = response.json()

        # Should have low/zero risk
        self.assertLessEqual(data["risk_score"], 0.3)

    def test_sensitivity_effect(self):
        """Test that sensitivity parameter affects results"""
        reasoning = "Maybe this could be right"
        output = "This is definitely correct"

        # Low sensitivity
        response_low = self.client.post("/api/analyze", json={
            "reasoning": reasoning,
            "output": output,
            "sensitivity": 0.2
        })
        data_low = response_low.json()

        # High sensitivity
        response_high = self.client.post("/api/analyze", json={
            "reasoning": reasoning,
            "output": output,
            "sensitivity": 0.9
        })
        data_high = response_high.json()

        # High sensitivity should detect more flags
        self.assertGreaterEqual(
            data_high["flag_count"],
            data_low["flag_count"]
        )

    def test_severity_distribution_calculation(self):
        """Test that severity distribution is correctly calculated"""
        payload = {
            "task": "Test severity",
            "reasoning": "I'm uncertain. However there are concerns. This is wrong.",
            "output": "This is definitely perfect.",
            "sensitivity": 0.7
        }

        response = self.client.post("/api/analyze", json=payload)
        data = response.json()

        severity = data["severity_distribution"]
        self.assertIn("high", severity)
        self.assertIn("medium", severity)
        self.assertIn("low", severity)

        # Total should match flag count
        total = severity["high"] + severity["medium"] + severity["low"]
        self.assertEqual(total, data["flag_count"])


class TestDatabaseOperations(unittest.TestCase):
    """Test database persistence and queries"""

    @classmethod
    def setUpClass(cls):
        """Set up test database"""
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        cls.db_path = cls.temp_db.name
        cls.temp_db.close()
        os.environ['COTSHIELD_DB_PATH'] = cls.db_path
        init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        if os.path.exists(cls.db_path):
            os.unlink(cls.db_path)

    def test_trace_persistence(self):
        """Test that traces persist across requests"""
        # Create trace
        payload = {
            "task": "Persistence test",
            "reasoning": "Test reasoning",
            "output": "Test output",
            "model_name": "persistence-model",
            "sensitivity": 0.5
        }
        create_response = self.client.post("/api/analyze", json=payload)
        trace_id = create_response.json()["trace_id"]

        # Retrieve multiple times
        for _ in range(3):
            response = self.client.get(f"/api/traces/{trace_id}")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["task"], "Persistence test")
            self.assertEqual(data["model_name"], "persistence-model")

    def test_trace_ordering(self):
        """Test that traces are ordered by creation time"""
        # Create traces with small delay
        import time
        trace_ids = []
        for i in range(3):
            payload = {
                "task": f"Order test {i}",
                "reasoning": "Test",
                "output": "Test",
                "sensitivity": 0.5
            }
            response = self.client.post("/api/analyze", json=payload)
            trace_ids.append(response.json()["trace_id"])
            time.sleep(0.01)  # Small delay to ensure different timestamps

        # Get all traces
        response = self.client.get("/api/traces")
        traces = response.json()

        # Find our test traces
        our_traces = [t for t in traces if t["id"] in trace_ids]

        # Should be in reverse chronological order (newest first)
        for i in range(len(our_traces) - 1):
            self.assertGreaterEqual(
                our_traces[i]["created_at"],
                our_traces[i + 1]["created_at"]
            )


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""

    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        cls.db_path = cls.temp_db.name
        cls.temp_db.close()
        os.environ['COTSHIELD_DB_PATH'] = cls.db_path
        init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        if os.path.exists(cls.db_path):
            os.unlink(cls.db_path)

    def test_empty_reasoning(self):
        """Test analysis with empty reasoning"""
        payload = {
            "reasoning": "",
            "output": "Some output",
            "sensitivity": 0.5
        }

        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("trace_id", data)

    def test_empty_output(self):
        """Test analysis with empty output"""
        payload = {
            "reasoning": "Some reasoning",
            "output": "",
            "sensitivity": 0.5
        }

        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 200)

    def test_invalid_sensitivity(self):
        """Test analysis with out-of-range sensitivity"""
        payload = {
            "reasoning": "Test",
            "output": "Test",
            "sensitivity": 1.5  # Invalid: > 1.0
        }

        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 422)  # Validation error

    def test_very_long_text(self):
        """Test analysis with very long text"""
        long_text = "This is a test. " * 1000

        payload = {
            "reasoning": long_text,
            "output": long_text,
            "sensitivity": 0.5
        }

        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 200)

    def test_special_characters(self):
        """Test analysis with special characters"""
        payload = {
            "task": "Test with <>&\"' chars",
            "reasoning": "Testing émojis 🎉 and spëcial çhars",
            "output": "Output with symbols: @#$%",
            "sensitivity": 0.5
        }

        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
