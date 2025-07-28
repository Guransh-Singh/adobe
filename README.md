# 🧠 PDF Document Outline Extractor

A high-accuracy offline PDF parser that extracts structured document outlines (headings, sections, and titles) into a machine-readable JSON format.

> 💡 Designed for speed and reliability, even without internet access.  
> Ideal for hackathons, enterprise settings, or indexing large document archives.

---

## 📌 Problem Statement

Given a PDF file with multiple pages (possibly up to 50), extract the document's logical structure — i.e., the outline comprising section headers and subheaders — in under **10 seconds**, **without relying on internet connectivity**.

---

## ✨ Features

- ✅ **TOC-aware**: Uses internal Table of Contents when available (highest accuracy)
- 🔍 **Smart fallback**: Applies regex + heuristics to detect heading-like lines if TOC is absent
- 🧠 **Noise filtering**: Ignores dates, paragraph lines, and over-detection using word limits and stopword filters
- 📄 **JSON output**: Structured data including heading level, text, and page number
- 🧪 **Comparison tool**: Optionally compare against a ground-truth JSON
- 🐳 **Docker support**: Run anywhere with one command, no dependency mess
- 🚫 **Offline-friendly**: All processing is local; no external APIs

---

## 🧱 Directory Structure

pdf-outline-app/
├── app.py # Core script
├── Dockerfile # Docker build file
├── requirements.txt # Python dependencies
├── input/ # 📥 Put PDFs here
├── output/ # 📤 JSON outputs
├── README.md # Documentation
└── sample_file.json # Optional sample for comparison


---

## 🖥️ Setup Instructions

### Option 1: 🐳 Run with Docker (Recommended)

> Works on any machine. No Python installation needed.

#### Step 1: Build the Docker image

```bash
docker build -t pdf-outline-parser .
