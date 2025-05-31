# DevBrain - Your Second Brain for Development

A personal memory bank for developers that captures terminal commands, outputs, and notes, making them searchable through natural language.

## Features

- 🧾 Searchable terminal history with context
- 📘 Logbook for scripts, debugging, and notes
- 🤖 AI-powered natural language search
- 🔒 Local-first, privacy-focused design

## Quick Start

1. Install the shell integration:

```bash
bash shell/install.sh
```

2. Reload your shell configuration (for Bash):

```bash
source ~/.bashrc
```

(For Zsh, use `source ~/.zshrc`)

3. Install backend requirements:

```bash
cd backend
pip install -r requirements.txt
```

4. Start DevBrain in your terminal (this will automatically start the backend server):

```bash
devbrain_toggle
```

5. Start using DevBrain features in your terminal!

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

## Shell Commands

DevBrain provides several shell functions for seamless integration:

### devbrain_toggle

Enable or disable DevBrain logging and automatically start/stop the backend server.

```bash
devbrain_toggle
```

### devbrain_search

Search your command history using a keyword or phrase.

```bash
devbrain_search "<query>"
```

### devbrain_ask

Search your command history using natural language (AI-powered).

```bash
devbrain_ask "<your question>"
```

### devbrain_commit

Generate an AI-powered commit message for the current git changes and optionally commit.

```bash
devbrain_commit
# or for a specific directory
 devbrain_commit <directory>
```

## Architecture

- **Shell Integration**: Captures terminal commands and context
- **Backend API**: FastAPI server for data management
- **Database**: SQLite for local storage
- **AI Layer**: OpenAI integration for natural language search

## License

MIT License - see LICENSE file for details
