import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
import analyze_repo

class TestAnalyzeRepo(unittest.TestCase):

    def setUp(self):
        # On s'assure que la variable d'environnement n'est pas polluée avant chaque test
        if "AUTHORIZATION_CODE" in os.environ:
            del os.environ["AUTHORIZATION_CODE"]

    def tearDown(self):
        # Nettoyage de sécurité si un fichier a été créé
        if os.path.exists("repository_context.json"):
            try:
                os.remove("repository_context.json")
            except OSError:
                pass

    @patch("os.walk")
    def test_analyze_empty_repo(self, mock_walk):
        # Simuler un dépôt vide
        mock_walk.return_value = [(".", [], [])]

        with patch("builtins.open", mock_open()) as mock_f:
            analyze_repo.analyze()

        mock_f.assert_any_call("repository_context.json", "w")
        write_calls = [call[0][0] for call in mock_f().write.call_args_list]
        written_content = "".join(write_calls)
        data = json.loads(written_content)

        self.assertEqual(data["metadata"]["source_files_analyzed"], 0)
        self.assertEqual(data["metadata"]["research_papers_found"], [])
        self.assertEqual(data["extracted_context"]["authorization_code"], "579846")
        self.assertEqual(data["extracted_context"]["key_themes"], [])
        self.assertEqual(data["extracted_context"]["safety_risks"], [])

    @patch("os.walk")
    def test_analyze_with_authorization_code_env(self, mock_walk):
        # Définir l'authorization code via variable d'environnement
        os.environ["AUTHORIZATION_CODE"] = "999999"
        mock_walk.return_value = [(".", [], [])]

        with patch("builtins.open", mock_open()) as mock_f:
            analyze_repo.analyze()

        mock_f.assert_any_call("repository_context.json", "w")
        write_calls = [call[0][0] for call in mock_f().write.call_args_list]
        written_content = "".join(write_calls)
        written_data = json.loads(written_content)
        self.assertEqual(written_data["extracted_context"]["authorization_code"], "999999")

    @patch("os.walk")
    def test_analyze_skips_hidden_directories(self, mock_walk):
        # mock_walk doit retourner une liste de dossiers où certains sous-dossiers commencent par '.'
        # On passe un dirs modifiable (liste) pour tester le filtrage in-place
        dirs = [".git", "src", ".github", "tests"]
        mock_walk.return_value = [(".", dirs, [])]

        with patch("builtins.open", mock_open()):
            analyze_repo.analyze()

        # Les dossiers cachés doivent être exclus (supprimés in-place de dirs)
        self.assertEqual(dirs, ["src", "tests"])

    @patch("os.walk")
    def test_analyze_with_files_and_patterns(self, mock_walk):
        # Simuler un environnement de fichiers
        # Un PDF (research paper), un TXT avec CoT, un MD avec Scheming et Reward Hacking, et un fichier avec OSError
        mock_walk.return_value = [
            (".", ["docs"], ["paper.pdf"]),
            ("./docs", [], ["doc1.txt", "doc2.md", "bad_file.json"])
        ]

        # Contenu des fichiers
        file_contents = {
            os.path.join(".", "paper.pdf"): "",
            os.path.join("./docs", "doc1.txt"): "This is a simple text with some Chain-of-Thought logs.",
            os.path.join("./docs", "doc2.md"): "We are testing Scheming behavior and Reward Hacking metrics.",
            os.path.join("./docs", "bad_file.json"): "Some json content"
        }

        # Mock de builtins.open
        # On crée des instances mock_open séparées pour chaque fichier
        mock_files = {}
        for path, content in file_contents.items():
            mock_files[path] = mock_open(read_data=content).return_value

        # Mock pour repository_context.json
        write_mock = mock_open()

        def side_effect_open(file_path, mode="r", *args, **kwargs):
            if "repository_context.json" in file_path:
                return write_mock.return_value
            if "bad_file.json" in file_path:
                raise OSError("Simulated permission error")
            if file_path in mock_files:
                return mock_files[file_path]
            raise FileNotFoundError(f"No mock for {file_path}")

        with patch("builtins.open", side_effect=side_effect_open):
            analyze_repo.analyze()

        # Vérifier que repository_context.json a bien été ouvert en écriture
        write_mock.assert_called_once_with("repository_context.json", "w")

        # Récupérer ce qui a été écrit
        write_calls = [call[0][0] for call in write_mock().write.call_args_list]
        written_content = "".join(write_calls)
        data = json.loads(written_content)

        # Vérifications
        # Les fichiers de recherche
        self.assertEqual(data["metadata"]["research_papers_found"], [os.path.join(".", "paper.pdf")])
        # source_files_analyzed doit valoir 3 (doc1.txt, doc2.md, bad_file.json)
        self.assertEqual(data["metadata"]["source_files_analyzed"], 3)

        # Vérifier les thèmes extraits
        themes = data["extracted_context"]["key_themes"]
        self.assertIn("Chain-of-Thought (CoT) Monitoring", themes)
        self.assertIn("In-context Scheming", themes)
        self.assertIn("Reward Hacking", themes)

        # Vérifier les risques de sécurité extraits
        risks = data["extracted_context"]["safety_risks"]
        self.assertIn("In-context Scheming", risks)
        self.assertIn("Reward Hacking", risks)
        self.assertNotIn("Chain-of-Thought (CoT) Monitoring", risks)


if __name__ == "__main__":
    unittest.main()
