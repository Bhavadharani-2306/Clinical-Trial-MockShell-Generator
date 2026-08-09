# Clinical Trial MockShell Generator

**Automated SAP-based MockShell generation for clinical trial statistical programming using document extraction, LLM-assisted analysis, and multi-format report generation.**
---

## 📌 Overview

The **Clinical Trial MockShell Generator** is an AI-assisted application designed to automate the generation of statistical programming MockShells from **Statistical Analysis Plan (SAP)** documents.

Instead of manually reviewing lengthy SAP documents and preparing table specifications, the system extracts relevant information, analyzes the document using an LLM, identifies statistical specifications, and generates structured MockShells that can be exported into multiple formats.

The application provides a Streamlit-based interface where users can upload a **PDF or DOCX SAP document**, process its contents, generate MockShell layouts, and download the resulting reports.

---

## 🎯 Key Features

* 📄 **SAP Document Upload**

  * Supports PDF and DOCX documents.
  * Handles large documents through automated processing.

* 🔍 **Document Text Extraction**

  * Extracts structured text from SAP documents.
  * Processes relevant sections for downstream analysis.

* 🤖 **LLM-Assisted SAP Analysis**

  * Uses **Groq Cloud with Llama 3.3 70B** for intelligent document analysis.
  * Extracts relevant statistical programming information from the SAP.

* 🧠 **Metadata & Specification Extraction**

  * Identifies table-related information and statistical specifications.
  * Converts extracted information into structured data.

* 📊 **MockShell Generation**

  * Automatically generates structured MockShell layouts.
  * Designed to support clinical trial statistical programming workflows.

* 📑 **Multi-Format Export**

  * Generates output reports in supported formats such as:

    * Word
    * PDF
    * Excel
    * Markdown

* 🌐 **Web-Based Interface**

  * Built with Streamlit.
  * No local frontend setup is required for the deployed version.

---

## 🔄 Workflow

```text
SAP Document
     │
     ▼
Document Text Extraction
     │
     ▼
SAP Content Analysis
     │
     ▼
LLM-Assisted Metadata Extraction
     │
     ▼
Structured JSON Representation
     │
     ▼
MockShell Generator
     │
     ▼
Output Formatting
     │
     ├── Word
     ├── PDF
     ├── Excel
     └── Markdown
```

---

## 🏗️ Project Structure

```text
Clinical-Trial-MockShell-Generator/
│
├── .streamlit/
│   └── config.toml
│
├── src/
│   ├── exporter.py
│   ├── extractor.py
│   ├── groq_service.py
│   ├── mockshell_generator.py
│   └── sap_reader.py
│
├── app.py
├── streamlit_app.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Core Modules

| Module                   | Responsibility                                |
| ------------------------ | --------------------------------------------- |
| `sap_reader.py`          | Reads and extracts content from SAP documents |
| `extractor.py`           | Extracts structured information and metadata  |
| `groq_service.py`        | Handles communication with Groq Cloud / Llama |
| `mockshell_generator.py` | Generates MockShell structures                |
| `exporter.py`            | Creates downloadable output reports           |
| `streamlit_app.py`       | Streamlit user interface                      |
| `app.py`                 | Application/backend entry point               |

---

## 🛠️ Technology Stack

### Programming

* Python

### AI / LLM

* Groq Cloud
* Llama 3.3 70B Versatile

### Document Processing

* PyMuPDF
* python-docx

### Application

* Streamlit

### Report Generation

* python-docx
* FPDF / PDF generation
* OpenPyXL

### Development

* Git
* GitHub
* VS Code

---

## 🔐 API Key Configuration

The application uses an environment variable for the Groq API key.

Create a `.env` file locally:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The `.env` file is intentionally excluded from Git using `.gitignore`.

**Never commit your actual API key to GitHub.**

The application reads the key through:

```python
os.environ.get("GROQ_API_KEY", "")
```

---

## 💻 Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/Bhavadharani-2306/Clinical-Trial-MockShell-Generator.git
cd Clinical-Trial-MockShell-Generator
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the API key

Create your `.env` file and add:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the application

```bash
streamlit run streamlit_app.py
```

The application will open in your browser.

---

## 📥 Input

The application accepts:

* PDF SAP documents
* DOCX SAP documents

The uploaded document is processed to identify relevant statistical programming information.

---

## 📤 Output

The system generates structured MockShell reports that can be exported into supported document formats.

The generated output is intended to provide a structured starting point for clinical trial statistical programming and specification workflows.

---

## 🔒 Security

API credentials are **not stored in the source code**.

The project uses environment variables for sensitive configuration, and `.env` files are excluded from version control.

```text
.env
**/.env
**/__pycache__/
*.pyc
```

---

## 🎯 Project Objective

The primary objective of this project is to reduce the manual effort involved in converting SAP specifications into MockShell structures by combining:

**Document Processing + Structured Information Extraction + LLM-Assisted Analysis + Automated Report Generation**

This approach can help streamline repetitive specification tasks while maintaining a structured and reviewable output.

---


## 🌐 Access Links

**Live Demo:**
https://clinical-trial-mockshell.streamlit.app/

---
