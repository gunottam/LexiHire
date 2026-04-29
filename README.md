# LexiHire

LexiHire is a resume screening and ranking platform built to help recruiters quickly extract, analyze, and compare candidate resumes against a target role. The app combines a React + Vite frontend with a Flask-based backend pipeline for parsing, scoring, and ranking resumes.

## What It Does

- Upload PDF or DOCX resumes and extract text automatically.
- Match resume content against the selected job role.
- Rank candidates through the compiler-inspired processing pipeline.
- Present results through a clean dashboard experience.

## Tech Stack

- Frontend: React, Vite, React Router
- Backend: Flask, PyMuPDF, python-docx
- Processing: custom tokenizer, parser, semantic analysis, scoring, and optimization pipeline
- Storage: Supabase integration for uploaded files and extracted text

## Getting Started

### Frontend

```bash
npm install
npm run dev
```

### Backend

```bash
pip install -r requirements.txt
python app.py
```

## Project Structure

- `src/` - frontend pages, layout, and components
- `app.py` - Flask API for uploads and processing
- `compiler/` - tokenization, parsing, semantic analysis, scoring, and optimization
- `databas/` - resume ranking persistence helpers
- `supabase_utils/` - Supabase client setup

## Team

- Gunottam - Team Lead
- Ananya Garg
- Prableen Kaur

## Notes

The repository now excludes runtime artifacts, local scratch files, and sample resume assets so the codebase stays focused on the actual product.

