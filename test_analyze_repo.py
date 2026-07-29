import unittest
import os
import tempfile
import json
import re
from unittest.mock import patch, mock_open
from analyze_repo import _process_file, analyze

class TestAnalyzeRepo(unittest.TestCase):

    def test_process_file_matching(self):
        patterns = {
            "Chain-of-Thought (CoT) Monitoring": re.compile(r"(CoT|Chain-of-Thought)", re.IGNORECASE),
            "Reward Hacking": re.compile(r"Reward Hacking", re.IGNORECASE)
        }
        risks = ["Reward Hacking"]
        summary = {
            "extracted_context": {
                "key_themes": set(),
                "safety_risks": set()
            }
        }

        # Mock builtins.open to return custom content
        with patch("builtins.open", mock_open(read_data="This contains CoT and Reward Hacking!")):
            _process_file("dummy_path.txt", patterns, risks, summary)

        self.assertIn("Chain-of-Thought (CoT) Monitoring", summary["extracted_context"]["key_themes"])
        self.assertIn("Reward Hacking", summary["extracted_context"]["key_themes"])
        self.assertIn("Reward Hacking", summary["extracted_context"]["safety_risks"])

    def test_process_file_no_match(self):
        patterns = {
            "Chain-of-Thought (CoT) Monitoring": re.compile(r"(CoT|Chain-of-Thought)", re.IGNORECASE)
        }
        risks = []
        summary = {
            "extracted_context": {
                "key_themes": set(),
                "safety_risks": set()
            }
        }

        with patch("builtins.open", mock_open(read_data="No matched keywords here.")):
            _process_file("dummy_path.txt", patterns, risks, summary)

        self.assertEqual(len(summary["extracted_context"]["key_themes"]), 0)

    def test_process_file_os_error(self):
        patterns = {
            "Chain-of-Thought (CoT) Monitoring": re.compile(r"(CoT|Chain-of-Thought)", re.IGNORECASE)
        }
        risks = []
        summary = {
            "extracted_context": {
                "key_themes": set(),
                "safety_risks": set()
            }
        }

        # Mock open to raise OSError to verify the except block handles it gracefully
        with patch("builtins.open", side_effect=OSError("Read failed")):
            _process_file("dummy_path.txt", patterns, risks, summary)

        # Should not raise exception and summary should remain empty
        self.assertEqual(len(summary["extracted_context"]["key_themes"]), 0)

    def test_analyze_execution(self):
        # Verify the end-to-end analyze function runs without errors and produces output
        if os.path.exists("repository_context.json"):
            os.remove("repository_context.json")

        analyze()

        self.assertTrue(os.path.exists("repository_context.json"))
        with open("repository_context.json", "r") as f:
            data = json.load(f)
            self.assertIn("metadata", data)
            self.assertIn("extracted_context", data)

if __name__ == "__main__":
    unittest.main()
