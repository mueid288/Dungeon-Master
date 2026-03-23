# Dungeon Master

Dungeon Master is an AI-powered RPG game engine built with FastAPI and integrated with the Groq API. It acts as an interactive "Dungeon Master," generating dynamic, progressive storylines, quests, and scenarios formatted in Roman Urdu. It tracks the game's state over multiple turning points (Acts 1-4) and makes narrative decisions based on automated D20 dice rolls, character classes, and past memory inputs.

## Features

- **Authentication**: Secure user registration and login using JWT and password hashing.
- **Character & Inventory Management**: Create characters with specific attributes (health, classes) and persistently track their inventory (items gained/lost).
- **Campaign Management**: Initialize and track campaigns, tying players and their respective characters to ongoing themes and quests.
- **AI Game Engine**: Powered by Groq, the engine dynamically constructs prompts based on action count to control the story's pacing (Introduction, Middle, Climax, Conclusion) and uses simulated 1-20 dice rolls for action consequences.
- **Memory & State Tracking**: Uses a database-backed memory system to remember critical lore and recent actions, ensuring the AI maintains context and continuity throughout the campaign.
- **PDF Reports**: Export features for campaigns.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM & Migrations**: SQLAlchemy & Alembic
- **AI Provider**: Groq API
- **Frontend**: Vanilla HTML, CSS, and JavaScript
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Groq API Key

## How to Install and Run Locally

**1. Clone the repository and navigate to the project directory:**

```bash
git clone <repository_url>
cd "Dungeon Master"
```

**2. Start the Database:**
Spin up the PostgreSQL database using Docker Compose:

```bash
docker-compose up -d
```

**3. Setup the Backend Environment:**
Create and activate a virtual environment, then install all dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**4. Configuration:**
Create a `.env` file in the root directory and add your environment variables:

```env
GROQ_API_KEY="your_groq_api_key_here"
DATABASE_URL=postgresql://dm_user:dm_pass@localhost:5432/dungeon_master
SECRET_KEY="your_jwt_secret_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**5. Run Database Migrations:**
Apply the active SQLAlchemy models to your PostgreSQL database:

```bash
alembic upgrade head
```

**6. Start the Application:**
Launch the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The backend API documentation will be available at `http://localhost:8000/docs`.

**7. Access the Frontend:**
Open `frontend/index.html` in your web browser or use a simple live server (like VS Code's Live Server extension) to interact with the game UI.
