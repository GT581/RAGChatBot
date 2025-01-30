# RAG Chatbot

This project is a Retrieval-Augmented Generation (RAG) chatbot application that integrates with the Gemini API (as it is available for free: https://ai.google.dev/pricing) and it includes both frontend and backend components. It is built with Python and FastAPI for the backend, React in the frontend, and compiled and deployed with Docker.

## Project Structure

```plaintext
ragchatbot/
├── .env                     # Environment variables (DB credentials, API keys)
├── .env.example             # Example environment variables template
├── docker-compose.yml       # Docker services configuration
├── start                    # Executable to start services
├── stop                     # Executable to stop services
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py      # Chat endpoints (message handling, sessions)
│   │   │   └── ingest.py    # File upload and processing endpoints
│   │   ├── core/
│   │   │   ├── config.py    # Pydantic settings type definitions
│   │   │   ├── settings.py  # Default values and settings initialization
│   │   │   └── logging.py   # Logging configuration and setup
│   │   ├── db/
│   │   │   ├── database.py  # SQLAlchemy setup and connection handling
│   │   │   ├── init.sql     # Database schema and pgvector setup
│   │   │   └── models.py    # SQLAlchemy models (Chat, Document, etc.)
│   │   ├── services/
│   │   │   ├── chat_service.py       # Chat logic and message handling
│   │   │   ├── document_service.py   # Document processing and vector search
│   │   │   ├── embeddings_service.py # Gemini embeddings with rate limiting
│   │   │   ├── ingest_service.py     # File validation and processing
│   │   │   └── llm_service.py        # Gemini chat completion integration
│   │   ├── schemas/
│   │   │   └── models.py    # Pydantic models for API validation
│   │   └── main.py          # FastAPI app initialization and routing
│   ├── tests/
│   │   ├── conftest.py                # Test fixtures
│   │   ├── test_api.py                # API endpoint tests
│   │   ├── test_models.py             # Database model tests
│   │   ├── test_schemas.py            # Pydantic schema tests
│   │   ├── test_chat_service.py       # Chat service tests
│   │   ├── test_document_service.py   # Document service tests
│   │   ├── test_embeddings_service.py # Embeddings service tests
│   │   ├── test_llm_service.py        # LLM service tests
│   │   ├── test_ingest_service.py     # Combined ingest service tests
│   │   └── test_integration.py        # End-to-end integration tests
│   ├── Dockerfile           # Backend service container setup
│   ├── requirements.txt     # Python package dependencies
│
└── frontend/
    ├── public/
    │   └── index.html      # HTML entry point
    ├── src/
    │   ├── components/     # React components
    │   │   ├── ChatInterface.tsx # Main chat container
    │   │   ├── ChatWindow.tsx    # Message display area
    │   │   ├── FileUpload.tsx    # File upload handling
    │   │   ├── Header.tsx        # App header with navigation
    │   │   ├── MessageInput.tsx  # Message input with send
    │   │   ├── MessageItem.tsx   # Individual message display
    │   │   ├── MessageList.tsx   # Message history container
    │   │   └── Sidebar.tsx       # Chat session management
    │   ├── services/
    │   │   └── api.ts     # Backend API client with types
    │   ├── App.tsx        # Root React component
    │   ├── index.tsx      # React entry point
    │   ├── types.ts       # TypeScript type definitions
    │   └── index.css      # Global styles and Tailwind
    ├── Dockerfile         # Frontend container setup
    ├── package.json       # NPM dependencies
    ├── package-lock.json  # NPM lock file
    ├── tsconfig.json      # TypeScript configuration
    ├── tailwind.config.js # Tailwind CSS configuration
    └── postcss.config.js  # PostCSS plugins config
```


## Setup

1. Clone the repository
```bash
git clone https://github.com/GT581/RAGChatBot.git
cd ragchatbot
```

2. Create a .env file in the root directory with the following variables (using the example .env.example as a reference, replace the values with your own if desired, using postgres defaults):

```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ragchatbot
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ragchatbot

GEMINI_API_KEY='your_gemini_api_key'

REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
```

3. Running the project with Docker

   If you want to run the application using Docker, you can do so without manually installing dependencies for both backend and frontend. Docker Compose will handle everything for you.

   1. Build and start the containers

      Navigate to the project root directory (where `docker-compose.yml` is located) and run:

      ```bash
      docker compose up --build
      ```

      This command will build both the frontend and backend containers and start the application. The Docker Compose setup will automatically configure the necessary environment variables and dependencies.

   2. Accessing the application

      Once the containers are up, you can access the application via the following:

      - **Frontend**: Open [http://localhost:3000](http://localhost:3000) in your browser to interact with the UI.
      - **Backend API**: The FastAPI backend will be available at [http://localhost:8000](http://localhost:8000).

   3. Stopping the containers

      To stop the containers, you can use the following command:

      ```bash
      docker compose down
      ```

      This will stop and remove the containers but leave your data intact.

      Also, you can execute './stop' to stop the containers.

   4. Restarting the containers

      To restart the containers, you can use the following command:

      ```bash
      docker compose up -d
      ```

      This will start the containers with your existing data.

      Also, you can execute './start' to start the containers.

## Configuration
Application settings are defined in the `backend/app/core/settings.py` file. These settings are used to configure the application's behavior and performance, specifically related to the Gemini API and document processing.

### Models
- Gemini Model: Gemini 1.0 Pro
- Embedding Model: Text Embedding 004

### Rate Limits
The application is configured to work within Gemini API's free tier limits:
- 15 RPM (requests per minute)
- 32,000 TPM (tokens per minute)
- 1,500 RPD (requests per day)

### File Processing
Optimized for different file types:
- PDF: up to 5MB
- Excel: up to 4MB
- CSV: up to 3MB
- Text/JSON: up to 2MB

### Chunking Strategy
- Size: 500 characters (~300 words)
- Overlap: 50 characters (20%)
- Batch Size: 5 chunks per request
- Max Chunks: 100 per document