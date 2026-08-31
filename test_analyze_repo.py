import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
import json

# Import the module to test
import analyze_repo

class TestAnalyzeRepo(unittest.TestCase):

    @patch('os.walk')
    @patch('os.path.getsize')
    @patch('builtins.open', new_callable=mock_open, read_data="Reward Hacking found in this file.")
    @patch('json.dump')
    def test_file_size_check_under_limit(self, mock_json_dump, mock_file_open, mock_getsize, mock_os_walk):
        # Configure mocks
        mock_os_walk.return_value = [
            ('.', [], ['test_file.txt'])
        ]
        mock_getsize.return_value = 5 * 1024 * 1024 # 5 MB (under limit)

        # Run analyze
        analyze_repo.analyze()

        # Check if open was called with correct parameters
        mock_file_open.assert_any_call(os.path.join('.', 'test_file.txt'), 'r', encoding='utf-8', errors='ignore')

        # Retrieve the arguments passed to json.dump (the first call is repository_context.json)
        self.assertTrue(mock_json_dump.called)
        written_data = mock_json_dump.call_args[0][0]
        self.assertEqual(written_data["metadata"]["source_files_analyzed"], 1)
        self.assertIn("Reward Hacking", written_data["extracted_context"]["key_themes"])

    @patch('os.walk')
    @patch('os.path.getsize')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_file_size_check_over_limit(self, mock_json_dump, mock_file_open, mock_getsize, mock_os_walk):
        # Configure mocks
        mock_os_walk.return_value = [
            ('.', [], ['huge_file.txt'])
        ]
        mock_getsize.return_value = 15 * 1024 * 1024 # 15 MB (over limit)

        # Run analyze
        analyze_repo.analyze()

        # Open should NOT be called for huge_file.txt
        for call in mock_file_open.call_args_list:
            args, _ = call
            self.assertNotEqual(args[0], os.path.join('.', 'huge_file.txt'))

        # The file is still counted as source_files_analyzed but read attempt fails gracefully
        self.assertTrue(mock_json_dump.called)
        written_data = mock_json_dump.call_args[0][0]
        self.assertEqual(written_data["metadata"]["source_files_analyzed"], 1)

if __name__ == '__main__':
    unittest.main()
