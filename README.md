# FsExplorer — Agentic File Search

> **An AI-powered document intelligence agent that explores your filesystem, parsing PDFs and answering complex questions with citations.**

![UI Screenshot](assets/ui_screenshot.png)

## 🚀 Key Features

*   **Intelligent Exploration**: Unlike traditional RAG, FsExplorer navigates folders, follows cross-references ("See Exhibit B"), and actively searches for answers.
*   **Deep Document Understanding**:
    *   **PDF & OCR**: Powered by `Docling`, `Tesseract`, and `Poppler` to read scanned documents and complex PDFs.
    *   **Multi-format**: Supports DOCX, PPTX, XLSX, HTML, Markdown, and source code.
*   **Modern Web UI**: A beautiful, glassmorphic interface with:
    *   Real-time execution logs (streaming WebSocket).
    *   Step-by-step reasoning visualization.
    *   Clean, cited final answers.
*   **Dockerized Deployment**: Fully containerized environment with all system dependencies pre-installed.
*   **Cost Effective**: Uses Google Gemini 3 Flash for high speed and low cost (~$0.001 per query).

## 🛠️ Tech Stack

*   **AI Core**: Google Gemini 3 Flash (via `google-genai` SDK)
*   **Orchestration**: LlamaIndex Workflows (Event-driven architecture)
*   **Parsing**: Docling + Tesseract OCR
*   **Backend**: FastAPI + WebSockets
*   **Frontend**: Vanilla JS + CSS (Glassmorphism design)
*   **Infrastructure**: Docker + Docker Compose

## 📦 Installation

### Prerequisites

*   **Docker** and **Docker Compose** installed.
*   A **Google Gemini API Key** (Get one [here](https://aistudio.google.com/apikey)).

### Quick Start (Docker)

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Taveren7/agentic-file-search-pro.git
    cd agentic-file-search-pro
    ```

2.  **Configure Environment**:
    Create a `.env` file in the root directory:
    Or simply rename the `.env.example` file to `.env` and fill in the values.
    ```bash
    GOOGLE_API_KEY=your_actual_api_key_here
    ```

    **Alternative**: You can also export the key in your shell instead of using a file:
    ```bash
    export GOOGLE_API_KEY=your_key_here
    docker-compose up
    ```

3.  **Run with Docker**:
    ```bash
    docker-compose up -d --build
    ```
    *Note: The first build may take a few minutes to compile OCR dependencies.*

    Open your browser to: **http://localhost:8000**

### 📂 Mounting Your Own Folders

To explore folders outside of the project directory (e.g., your Documents or a separate data drive), you can "plug them in" via environment variables:

1.  **Set the path**: Add this to your `.env` (or run it in your shell):
    *   **Mac/Linux**: `HOST_DATA_PATH=/Users/yourname/Documents/Work`
    *   **Windows**: `HOST_DATA_PATH=C:\Users\yourname\Desktop\ProjectData`
2.  **Restart**: Run `docker-compose up -d`.
3.  **Explore**: In the Web UI, you will see a folder named **`external_data`**. Open it to search your host files!

### 🛑 Stopping the App

To stop the background containers, run:
```bash
docker-compose down
```

## 📖 Usage Guide

### Using the Web UI

1.  **Select Target**: Use the folder picker to select the directory you want to analyze (Docker mounts the current directory to `/app` by default).
2.  **Ask a Question**:
    *   *Simple*: "Summarize the NDA in the contracts folder."
    *   *Complex*: "Compare the payment terms in the Acquisition Agreement vs the Financial Adjustments."
3.  **Watch it Work**: The agent will scan, preview, and deep-dive into files. It may even ask you follow-up questions if it gets stuck!

### CLI Mode (Optional)

You can also run the agent directly from the command line if you have `uv` installed:

```bash
uv run explore --task "Find all deadlines in the project_plan.pdf"
```

## 🔧 Troubleshooting

*   **"Connection failed"**: Ensure the Docker container is running (`docker-compose ps`).
*   **PDF Parsing Errors**: If you see missing library errors, ensure you rebuilt the container (`docker-compose up --build`) which installs `libGL` and `poppler`.


### Why Agentic File Search?

The difference between a Traditional RAG (Retrieval-Augmented Generation) system and Agentic File Search (like this project) lies primarily in autonomy and contextual awareness.

Think of it as the difference between a Search Engine (Traditional RAG) and a Research Assistant (Agentic Search).


1. Traditional RAG: The "Store and Fetch" Model
Traditional RAG relies on a "black box" retrieval mechanism. You index your files into a vector database ahead of time. When you ask a question:

The system converts your prompt into a math vector.
It pulls the chunks of text that are most mathematically similar.
It hands those chunks to the LLM to summarize.
The Weakness: If the answer depends on a cross-reference (e.g., a contract that says "Pricing is defined in the Appendix"), the vector database might not realize the Appendix is relevant because it doesn't "understand" the text—it just sees that the Appendix doesn't mention the word "Pricing."

2. Agentic File Search: The "Browse and Read" Model
The agentic approach mimics how a human works. Instead of a fixed index, it has a high-level "strategy":

Explore: It starts by listing files in a directory.
Prioritize: It uses 
scan_folder
 to categorize files (RELEVANT, MAYBE, SKIP).
Deep Dive: It uses 
parse_file
 to read the most promising documents.
Follow Links: If a document mentions another file, it can backtrack—deciding to stop what it's doing and open that newly discovered file.
The Strength: It is far more precise for complex questions. It doesn't just find "similar" text; it builds a mental map of the folder structure and document relationships to find the correct text.

Which one to choose?
Use Traditional RAG if you have millions of documents and need sub-second answers to simple questions.
Use Agentic Search (this project) if you have hundreds of documents (like a legal folder or project repo) and need high-accuracy answers where context and document relationships matter most.

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

---

*Based on the original [fs-explorer](https://github.com/run-llama/fs-explorer) concept by LlamaIndex and the [agentic-file-search](https://github.com/PromtEngineer/agentic-file-search) implementation by PromptEngineer.*
