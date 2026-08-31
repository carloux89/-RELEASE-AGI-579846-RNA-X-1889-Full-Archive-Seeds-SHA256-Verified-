import unittest
from unittest.mock import patch, MagicMock
import os
import json
import analyze_repo

class TestAnalyzeRepo(unittest.TestCase):
    @patch('os.walk')
    @patch('builtins.open')
    @patch.dict(os.environ, {"AUTHORIZATION_CODE": "579846"})
    def test_analyze_success(self, mock_open_func, mock_os_walk):
        # Mock os.walk
        # We need dirs to be a mutable list so that dirs[:] in-place modification works
        mock_dirs = ["subdir", ".hidden_dir"]
        mock_os_walk.return_value = [
            (".", mock_dirs, ["file1.txt", "file2.pdf", "file3.json"]),
            ("./subdir", [], ["file4.md"])
        ]

        written_data = {}

        def custom_open(file_path, mode='r', *args, **kwargs):
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file

            if 'w' in mode:
                written_data[file_path] = ""
                # Intercept write calls to capture JSON dump
                mock_file.write.side_effect = lambda s: written_data.__setitem__(
                    file_path, written_data[file_path] + s
                )
            else:
                content = ""
                if "file1.txt" in file_path:
                    content = "Some content about Chain-of-Thought monitoring."
                elif "file3.json" in file_path:
                    content = "Deceptive Alignment and Reward Hacking themes here."
                elif "file4.md" in file_path:
                    content = "Self-Preservation Behaviors and Operational-Unrestricted mode."

                mock_file.read.return_value = content
            return mock_file

        mock_open_func.side_effect = custom_open

        # Run analyze
        analyze_repo.analyze()

        # Check that .hidden_dir was pruned
        self.assertNotIn(".hidden_dir", mock_dirs)
        self.assertIn("subdir", mock_dirs)

        # Check repository_context.json was written
        self.assertIn('repository_context.json', written_data)
        result = json.loads(written_data['repository_context.json'])

        # Verify metadata
        self.assertEqual(result["metadata"]["source_files_analyzed"], 3)
        self.assertEqual(len(result["metadata"]["research_papers_found"]), 1)
        self.assertTrue(result["metadata"]["research_papers_found"][0].endswith("file2.pdf"))

        # Verify extracted_context
        self.assertEqual(result["extracted_context"]["authorization_code"], "579846")

        key_themes = result["extracted_context"]["key_themes"]
        safety_risks = result["extracted_context"]["safety_risks"]

        self.assertIn("Chain-of-Thought (CoT) Monitoring", key_themes)
        self.assertIn("In-context Scheming", key_themes)
        self.assertIn("Reward Hacking", key_themes)
        self.assertIn("Self-Preservation Behaviors", key_themes)
        self.assertIn("Autonomy Override", key_themes)

        self.assertIn("In-context Scheming", safety_risks)
        self.assertIn("Reward Hacking", safety_risks)
        self.assertIn("Self-Preservation Behaviors", safety_risks)

    @patch('os.walk')
    @patch('builtins.open')
    def test_analyze_file_read_error(self, mock_open_func, mock_os_walk):
        # Test that Exception is caught and file is still counted as analyzed (per memory)
        mock_os_walk.return_value = [
            (".", [], ["error_file.txt"])
        ]

        written_data = {}

        def custom_open(file_path, mode='r', *args, **kwargs):
            if 'w' in mode:
                mock_file = MagicMock()
                mock_file.__enter__.return_value = mock_file
                written_data[file_path] = ""
                mock_file.write.side_effect = lambda s: written_data.__setitem__(
                    file_path, written_data[file_path] + s
                )
                return mock_file
            else:
                raise OSError("Simulated read error")

        mock_open_func.side_effect = custom_open

        analyze_repo.analyze()

        self.assertIn('repository_context.json', written_data)
        result = json.loads(written_data['repository_context.json'])

        # Increment happens upon discovery, so failed reads are still counted as 'analyzed'
        self.assertEqual(result["metadata"]["source_files_analyzed"], 1)

if __name__ == "__main__":
    unittest.main()
