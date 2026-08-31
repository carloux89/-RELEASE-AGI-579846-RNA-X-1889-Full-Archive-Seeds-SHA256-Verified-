import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
import analyze_repo

class TestAnalyzeRepo(unittest.TestCase):

    @patch('os.walk')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_analyze_basic(self, mock_json_dump, mock_file_open, mock_os_walk):
        # Simulate a simple file structure
        mock_os_walk.return_value = [
            ('.', ['subdir'], ['paper1.pdf', 'README.md']),
            ('./subdir', [], ['data.json'])
        ]

        # Define file contents
        file_contents = {
            os.path.abspath(os.path.join('.', 'README.md')): "This repo uses Chain-of-Thought monitoring.",
            os.path.abspath(os.path.join('./subdir', 'data.json')): '{"note": "Reward Hacking detected"}'
        }

        def side_effect(filename, *args, **kwargs):
            abs_path = os.path.abspath(filename)
            if abs_path in file_contents:
                return mock_open(read_data=file_contents[abs_path]).return_value
            return mock_open().return_value

        mock_file_open.side_effect = side_effect

        analyze_repo.analyze(base_path='.', output_file='test_output.json')

        args, _ = mock_json_dump.call_args
        summary = args[0]

        self.assertEqual(summary['metadata']['source_files_analyzed'], 2)
        self.assertIn(os.path.join('.', 'paper1.pdf'), summary['metadata']['research_papers_found'])
        self.assertIn('Chain-of-Thought (CoT) Monitoring', summary['extracted_context']['key_themes'])
        self.assertIn('Reward Hacking', summary['extracted_context']['key_themes'])
        self.assertIn('Reward Hacking', summary['extracted_context']['safety_risks'])

    @patch('os.walk')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_exclude_output_file(self, mock_json_dump, mock_file_open, mock_os_walk):
        mock_os_walk.return_value = [
            ('.', [], ['repository_context.json', 'other.txt'])
        ]

        file_contents = {
            os.path.abspath(os.path.join('.', 'other.txt')): "no themes here"
        }

        def side_effect(filename, *args, **kwargs):
            abs_path = os.path.abspath(filename)
            if abs_path in file_contents:
                return mock_open(read_data=file_contents[abs_path]).return_value
            return mock_open().return_value

        mock_file_open.side_effect = side_effect

        analyze_repo.analyze(base_path='.', output_file='repository_context.json')

        args, _ = mock_json_dump.call_args
        summary = args[0]

        self.assertEqual(summary['metadata']['source_files_analyzed'], 1)

    @patch('os.walk')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_handle_read_error(self, mock_json_dump, mock_file_open, mock_os_walk):
        mock_os_walk.return_value = [
            ('.', [], ['broken.txt'])
        ]

        def side_effect(filename, mode='r', *args, **kwargs):
            if 'r' in mode and 'broken.txt' in filename:
                raise Exception("Read Error")
            return mock_open().return_value

        mock_file_open.side_effect = side_effect

        # Should not raise exception, just print warning
        analyze_repo.analyze(base_path='.', output_file='test_output.json')

        args, _ = mock_json_dump.call_args
        summary = args[0]
        self.assertEqual(summary['metadata']['source_files_analyzed'], 1)
        self.assertEqual(len(summary['extracted_context']['key_themes']), 0)

if __name__ == '__main__':
    unittest.main()
