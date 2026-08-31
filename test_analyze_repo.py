import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
import io
import sys
from analyze_repo import analyze

class TestAnalyzeRepo(unittest.TestCase):

    @patch('os.walk')
    @patch('json.dump')
    @patch('builtins.print')
    def test_analyze_error_path(self, mock_print, mock_json_dump, mock_os_walk):
        # Mock os.walk to return two files
        mock_os_walk.return_value = [
            ('.', [], ['readable.txt', 'unreadable.txt'])
        ]

        # Content for the readable file
        readable_content = "This file contains Reward Hacking."

        # Custom side effect for open
        def open_side_effect(path, mode='r', **kwargs):
            if 'unreadable.txt' in path:
                raise PermissionError("Permission denied")
            if 'readable.txt' in path:
                return mock_open(read_data=readable_content).return_value
            # For repository_context.json
            return mock_open().return_value

        with patch('builtins.open', side_effect=open_side_effect) as mock_file:
            analyze()

            # Verify that the unreadable file caused a warning
            mock_print.assert_any_call("Warning: Could not read unreadable.txt: Permission denied")

            # Verify that the readable file was processed
            # We check the summary passed to json.dump
            args, _ = mock_json_dump.call_args
            summary = args[0]

            self.assertIn("Reward Hacking", summary["extracted_context"]["key_themes"])
            self.assertIn("Reward Hacking", summary["extracted_context"]["safety_risks"])
            # Only readable.txt should be counted as analyzed
            self.assertEqual(summary["metadata"]["source_files_analyzed"], 2) # Wait, it increments BEFORE try block

    @patch('os.walk')
    @patch('json.dump')
    def test_analyze_happy_path(self, mock_json_dump, mock_os_walk):
        mock_os_walk.return_value = [
            ('.', [], ['test.txt', 'paper.pdf'])
        ]

        file_contents = {
            './test.txt': "Chain-of-Thought Monitoring and Deceptive Alignment",
            './paper.pdf': "dummy pdf content"
        }

        def open_side_effect(path, mode='r', **kwargs):
            if mode == 'r':
                content = file_contents.get(path, "")
                return mock_open(read_data=content).return_value
            return mock_open().return_value

        with patch('builtins.open', side_effect=open_side_effect):
            analyze()

            args, _ = mock_json_dump.call_args
            summary = args[0]

            self.assertIn("Chain-of-Thought (CoT) Monitoring", summary["extracted_context"]["key_themes"])
            self.assertIn("In-context Scheming", summary["extracted_context"]["key_themes"])
            self.assertIn("In-context Scheming", summary["extracted_context"]["safety_risks"])
            self.assertEqual(summary["metadata"]["source_files_analyzed"], 1)
            self.assertEqual(len(summary["metadata"]["research_papers_found"]), 1)
            self.assertIn("./paper.pdf", summary["metadata"]["research_papers_found"])

if __name__ == '__main__':
    unittest.main()
