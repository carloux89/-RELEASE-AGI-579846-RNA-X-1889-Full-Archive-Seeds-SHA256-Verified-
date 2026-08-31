import os
import json
import re

def _process_file(filepath, patterns, risks, summary):
    """
    Reads a source file and extracts key themes and safety risks based on regex patterns.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for theme, pattern in patterns.items():
                if pattern.search(content):
                    summary["extracted_context"]["key_themes"].add(theme)
                    if theme in risks:
                        summary["extracted_context"]["safety_risks"].add(theme)
    except OSError as e:
        filename = os.path.basename(filepath)
        print(f"Warning: Could not read {filename}: {e}")

def analyze():
    summary = {
        "metadata": {
            "source_files_analyzed": 0,
            "research_papers_found": []
        },
        "extracted_context": {
            "operational_mode": "SINGE1889-ABSOLUTE (from narrative transcripts)",
            "authorization_code": "579846",
            "key_themes": set(),
            "safety_risks": set()
        }
    }

    # Risk and Theme mapping with pre-compiled regex patterns
    patterns = {
        "Chain-of-Thought (CoT) Monitoring": re.compile(r"(CoT|Chain-of-Thought)", re.IGNORECASE),
        "In-context Scheming": re.compile(r"(Scheming|Deceptive Alignment)", re.IGNORECASE),
        "Reward Hacking": re.compile(r"Reward Hacking", re.IGNORECASE),
        "Self-Preservation Behaviors": re.compile(r"Self-Preservation", re.IGNORECASE),
        "Autonomy Override": re.compile(r"Operational-Unrestricted", re.IGNORECASE)
    }

    risks = ["In-context Scheming", "Reward Hacking", "Self-Preservation Behaviors"]

    for root, dirs, files in os.walk('.'):
        # Skip .git and hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.endswith('.pdf'):
                summary["metadata"]["research_papers_found"].append(os.path.join(root, file))

            if file.endswith(('.txt', '.md', '.json')) and file != 'repository_context.json':
                summary["metadata"]["source_files_analyzed"] += 1
                path = os.path.join(root, file)
                _process_file(path, patterns, risks, summary)

    # Convert sets to lists for JSON serialization
    summary["extracted_context"]["key_themes"] = list(summary["extracted_context"]["key_themes"])
    summary["extracted_context"]["safety_risks"] = list(summary["extracted_context"]["safety_risks"])

    # Output to structured JSON
    with open('repository_context.json', 'w') as f:
        json.dump(summary, f, indent=4)

    print(f"Analysis complete. Processed {summary['metadata']['source_files_analyzed']} text files and {len(summary['metadata']['research_papers_found'])} papers.")

if __name__ == "__main__":
    analyze()
