# 📄 RBAC Chatbot

A modern, role-based access control (RBAC) chatbot application built with Flask and MongoDB. This application enables managers to upload PDF documents and allows both managers and employees to ask questions about the uploaded PDFs using AI-powered responses.

## ✨ Features

### 🔐 Role-Based Access Control
- **Manager Role**: Full access to upload PDFs, ask questions, and view chat history
- **Employee Role**: Can ask questions about manager-uploaded PDFs and view their own chat history
- Secure authentication with session management
- Role-based endpoint protection

### 📤 PDF Management
- Upload PDF documents (managers only)
- Secure file handling with `werkzeug.utils.secure_filename`
- PDF text extraction using `pdfminer`
- MongoDB integration for document storage

### 💬 AI-Powered Q&A
- Ask natural language questions about uploaded PDFs
- Powered by Ollama for intelligent responses
- Real-time answer generation
- Markdown-to-HTML conversion for formatted responses
- Chat history tracking with timestamps

### 🎨 Modern UI/UX
- Beautiful glass-morphism design
- Animated gradient background
- Responsive layout
- Smooth animations and hover effects
- Neon-styled buttons
- User-friendly interface with role indicators

## 🛠️ Tech Stack

- **Backend**: Flask (Python web framework)
- **Database**: MongoDB (NoSQL database)
- **AI Engine**: Ollama (Local LLM inference)
- **Frontend**: HTML5, CSS3, JavaScript
- **PDF Processing**: pdfminer
- **File Handling**: Werkzeug

## 📋 Prerequisites

Before running the application, ensure you have installed:

- Python 3.8+
- MongoDB running locally (`mongodb://localhost:27017/`)
- Ollama running with a local model

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Dineshkumar-S/RBAC\ chatbot
