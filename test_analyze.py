import unittest
import os
import json
from analyze_repo import analyze

class TestAnalyze(unittest.TestCase):
    def test_basic_analysis(self):
        # Create a dummy file with some themes
        with open('test_theme.txt', 'w') as f:
            f.write("This file contains Reward Hacking and some CoT.")

        analyze()

        with open('repository_context.json', 'r') as f:
            summary = json.load(f)

        themes = summary['extracted_context']['key_themes']
        self.assertIn("Reward Hacking", themes)
        self.assertIn("Chain-of-Thought (CoT) Monitoring", themes)

        # Cleanup
        os.remove('test_theme.txt')

if __name__ == '__main__':
    unittest.main()
