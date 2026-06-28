import os
import json
import unittest
from analyze_repo import analyze

class TestAnalyzeRepo(unittest.TestCase):
    def test_authorization_code_from_env(self):
        # Set a dummy authorization code
        test_code = "999999"
        os.environ["AUTHORIZATION_CODE"] = test_code

        # Run analyze
        analyze()

        # Verify repository_context.json exists and has the correct code
        self.assertTrue(os.path.exists("repository_context.json"))
        with open("repository_context.json", "r") as f:
            data = json.load(f)
            self.assertEqual(data["extracted_context"]["authorization_code"], test_code)

    def test_no_authorization_code_env(self):
        # Ensure AUTHORIZATION_CODE is not set
        if "AUTHORIZATION_CODE" in os.environ:
            del os.environ["AUTHORIZATION_CODE"]

        # Run analyze
        analyze()

        # Verify repository_context.json has None for authorization_code
        with open("repository_context.json", "r") as f:
            data = json.load(f)
            self.assertIsNone(data["extracted_context"]["authorization_code"])

if __name__ == "__main__":
    unittest.main()
