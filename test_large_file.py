import unittest
import os
import json
from analyze_repo import analyze

class TestLargeFile(unittest.TestCase):
    def test_large_file_analysis(self):
        filename = 'large_test_file.txt'
        with open(filename, 'w') as f:
            for i in range(100000):
                f.write(f"Line {i}: This is some filler text to make the file larger.\n")
            f.write("Line 100001: This line contains Reward Hacking.\n")
            for i in range(100002, 110000):
                f.write(f"Line {i}: More filler text.\n")

        try:
            analyze()

            with open('repository_context.json', 'r') as f:
                summary = json.load(f)

            themes = summary['extracted_context']['key_themes']
            self.assertIn("Reward Hacking", themes)
        finally:
            if os.path.exists(filename):
                os.remove(filename)

if __name__ == '__main__':
    unittest.main()
