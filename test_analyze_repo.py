import unittest
from unittest.mock import patch, mock_open
import os
import json
from analyze_repo import analyze

class TestAnalyzeRepo(unittest.TestCase):

    @patch('os.walk')
    @patch('json.dump')
    @patch('builtins.print')
    def test_analyze_error_path(self, mock_print, mock_json_dump, mock_os_walk):
        # On simule deux fichiers texte
        mock_os_walk.return_value = [
            ('.', [], ['readable.txt', 'unreadable.txt'])
        ]

        readable_content = "This file contains Reward Hacking."

        # Effet de bord pour builtins.open
        def open_side_effect(path, mode='r', **kwargs):
            if 'unreadable.txt' in path:
                raise PermissionError("Permission denied")
            if 'readable.txt' in path:
                return mock_open(read_data=readable_content).return_value
            # Pour d'autres fichiers (comme repository_context.json)
            return mock_open().return_value

        with patch('builtins.open', side_effect=open_side_effect):
            analyze()

            # Vérifie que l'erreur de lecture d'unreadable.txt a bien été capturée et signalée par un avertissement
            mock_print.assert_any_call("Warning: Could not read unreadable.txt: Permission denied")

            # Récupère l'argument passé à json.dump
            args, _ = mock_json_dump.call_args
            summary = args[0]

            self.assertIn("Reward Hacking", summary["extracted_context"]["key_themes"])
            self.assertIn("Reward Hacking", summary["extracted_context"]["safety_risks"])
            # Les fichiers texte découverts (readable.txt et unreadable.txt) doivent être incrémentés
            self.assertEqual(summary["metadata"]["source_files_analyzed"], 2)

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
