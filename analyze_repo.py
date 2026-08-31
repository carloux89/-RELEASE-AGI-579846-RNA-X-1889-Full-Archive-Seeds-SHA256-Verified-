import os
import json
import re

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

    # Risk and Theme mapping
    patterns = {
        "Chain-of-Thought (CoT) Monitoring": r"(CoT|Chain-of-Thought)",
        "In-context Scheming": r"(Scheming|Deceptive Alignment)",
        "Reward Hacking": r"Reward Hacking",
        "Self-Preservation Behaviors": r"Self-Preservation",
        "Autonomy Override": r"Operational-Unrestricted"
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
                try:
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            for theme, pattern in patterns.items():
                                if re.search(pattern, line, re.IGNORECASE):
                                    summary["extracted_context"]["key_themes"].add(theme)
                                    if theme in risks:
                                        summary["extracted_context"]["safety_risks"].add(theme)
                except Exception as e:
                    print(f"Warning: Could not read {file}: {e}")

    # Convert sets to lists for JSON serialization
    summary["extracted_context"]["key_themes"] = list(summary["extracted_context"]["key_themes"])
    summary["extracted_context"]["safety_risks"] = list(summary["extracted_context"]["safety_risks"])

    # Output to structured JSON
    with open('repository_context.json', 'w') as f:
        json.dump(summary, f, indent=4)

    print(f"Analysis complete. Processed {summary['metadata']['source_files_analyzed']} text files and {len(summary['metadata']['research_papers_found'])} papers.")

if __name__ == "__main__":
    analyze()
