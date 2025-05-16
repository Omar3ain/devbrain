# DevBrain - Your Second Brain for Development

A personal memory bank for developers that captures terminal commands, outputs, and notes, making them searchable through natural language.

## Features

- 🧾 Searchable terminal history with context
- 📘 Logbook for scripts, debugging, and notes
- 🤖 AI-powered natural language search
- 🔒 Local-first, privacy-focused design

## Quick Start

1. Install the shell hook:

```bash
curl -sSL https://raw.githubusercontent.com/yourusername/devbrain/main/shell/install.sh | bash
```

2. Start the backend server:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. Start using DevBrain in your terminal!

## Development

### Prerequisites

- Python 3.8+
- SQLite3
- OpenAI API key (for AI features)

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/devbrain.git
cd devbrain
```

2. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and configure your environment variables:

```bash
cp .env.example .env
```

4. Start the development server:

```bash
uvicorn app.main:app --reload
```

## Architecture

- **Shell Integration**: Captures terminal commands and context
- **Backend API**: FastAPI server for data management
- **Database**: SQLite for local storage
- **AI Layer**: OpenAI integration for natural language search

## License

MIT License - see LICENSE file for details
