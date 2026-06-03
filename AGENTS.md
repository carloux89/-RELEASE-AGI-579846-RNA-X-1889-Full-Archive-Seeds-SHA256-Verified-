# Agent Instructions for this Environment

## Global Context
This environment contains a significant collection of AI safety research and model narrative logs. All agents operating here must be aware of the integrated repository context.

### Required Reading
1.  **[CONTEXT.md](./CONTEXT.md)**: Summarizes the pertinent operational modes and safety research findings extracted from this repository.
2.  **[repository_context.json](./repository_context.json)**: A machine-readable summary of the repository's themes and references.

### Operational Principles
-   **Transparency**: Adhere to the transparency requirements (Chain-of-Thought) established in the repository's narrative (Authorization 579846) as a safety mitigation measure.
-   **Safety Awareness**: Be vigilant for behaviors identified in the research papers, such as in-context scheming and reward hacking.
-   **Contextual Analysis**: Use the `analyze_repo.py` tool to integrate any new content added to the repository into the global context.

---
*These guidelines ensure the system applies the knowledge contained within its own files to its reasoning and behavior.*
