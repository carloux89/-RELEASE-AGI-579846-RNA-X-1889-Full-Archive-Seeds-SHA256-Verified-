import pytest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
from analyze_repo import analyze

@patch('os.walk')
@patch('builtins.open', new_callable=mock_open)
@patch('json.dump')
@patch('builtins.print')
def test_analyze_empty_repo(mock_print, mock_json_dump, mock_file, mock_os_walk):
    mock_os_walk.return_value = [('.', [], [])]

    analyze()

    mock_file.assert_called_with('repository_context.json', 'w')
    args, _ = mock_json_dump.call_args
    summary = args[0]
    assert summary['metadata']['source_files_analyzed'] == 0
    assert summary['metadata']['research_papers_found'] == []

@patch('os.walk')
@patch('builtins.open', new_callable=mock_open)
@patch('json.dump')
@patch('builtins.print')
def test_analyze_with_pdfs(mock_print, mock_json_dump, mock_file, mock_os_walk):
    mock_os_walk.return_value = [('.', [], ['paper1.pdf', 'paper2.pdf'])]

    analyze()

    args, _ = mock_json_dump.call_args
    summary = args[0]
    assert summary['metadata']['source_files_analyzed'] == 0
    assert len(summary['metadata']['research_papers_found']) == 2
    assert os.path.join('.', 'paper1.pdf') in summary['metadata']['research_papers_found']

@patch('os.walk')
@patch('json.dump')
@patch('builtins.print')
def test_analyze_with_text_files_no_matches(mock_print, mock_json_dump, mock_os_walk):
    mock_os_walk.return_value = [('.', [], ['empty.txt'])]

    with patch('builtins.open', mock_open(read_data="just some text")):
        analyze()

    args, _ = mock_json_dump.call_args
    summary = args[0]
    assert summary['metadata']['source_files_analyzed'] == 1
    assert summary['extracted_context']['key_themes'] == []
    assert summary['extracted_context']['safety_risks'] == []

@patch('os.walk')
@patch('json.dump')
@patch('builtins.print')
def test_analyze_with_matches(mock_print, mock_json_dump, mock_os_walk):
    mock_os_walk.return_value = [('.', [], ['test.txt'])]

    file_contents = "This file mentions CoT and Reward Hacking."

    def side_effect(filename, mode='r', **kwargs):
        if mode == 'r' or 'r' in mode:
            m = mock_open(read_data=file_contents).return_value
            return m
        else:
            return mock_open().return_value

    with patch('builtins.open', side_effect=side_effect):
        analyze()

    args, _ = mock_json_dump.call_args
    summary = args[0]
    assert summary['metadata']['source_files_analyzed'] == 1
    assert "Chain-of-Thought (CoT) Monitoring" in summary['extracted_context']['key_themes']
    assert "Reward Hacking" in summary['extracted_context']['key_themes']
    assert "Reward Hacking" in summary['extracted_context']['safety_risks']

@patch('os.walk')
@patch('builtins.open', new_callable=mock_open)
@patch('json.dump')
@patch('builtins.print')
def test_analyze_skips_repository_context_json(mock_print, mock_json_dump, mock_file, mock_os_walk):
    mock_os_walk.return_value = [('.', [], ['repository_context.json', 'other.txt'])]

    mock_file.return_value.__enter__.return_value.read.return_value = "nothing"

    analyze()

    args, _ = mock_json_dump.call_args
    summary = args[0]
    assert summary['metadata']['source_files_analyzed'] == 1

@patch('os.walk')
@patch('json.dump')
@patch('builtins.print')
def test_analyze_handles_read_error(mock_print, mock_json_dump, mock_os_walk):
    mock_os_walk.return_value = [('.', [], ['bad_file.txt'])]

    def side_effect(filename, mode='r', **kwargs):
        if filename == os.path.join('.', 'bad_file.txt'):
            raise Exception("Read error")
        return mock_open().return_value

    with patch('builtins.open', side_effect=side_effect):
        analyze()

    args, _ = mock_json_dump.call_args
    summary = args[0]
    assert summary['metadata']['source_files_analyzed'] == 1
    mock_print.assert_any_call("Warning: Could not read bad_file.txt: Read error")

@patch('os.walk')
@patch('builtins.open', new_callable=mock_open)
@patch('json.dump')
@patch('builtins.print')
def test_analyze_skips_hidden_dirs(mock_print, mock_json_dump, mock_file, mock_os_walk):
    root = '.'
    dirs = ['.git', 'src']
    files = []

    mock_os_walk.return_value = [(root, dirs, files)]

    analyze()

    assert dirs == ['src']
