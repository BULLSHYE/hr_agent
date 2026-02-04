# 🤖 AI-Powered HR Recruitment Agent

## 📌 Project Overview

This project implements an AI-powered HR Recruitment Agent designed to assist HR teams in automating the recruitment workflow. It enables HR professionals to:

- **Upload or Generate Job Descriptions (JD)**: Support for PDF, DOCX, and TXT formats, or AI-generated JDs
- **Discover Candidates**: Fetch candidate data from job portals (currently mocked APIs)
- **Store Candidate Intelligence**: Vector database for semantic search and matching
- **Match Candidates with JDs**: AI-powered similarity scoring and reasoning
- **Generate Personalized Emails**: AI-written emails for candidates and HR notifications
- **Dynamic Model Switching**: Switch between API-based and local LLMs at runtime
- **Docker-Ready**: Fully containerized for easy deployment

The system demonstrates end-to-end AI system design, including AI orchestration, vector memory (RAG), model routing, matching logic, and real-world API simulation.

## 🏗️ System Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐
│  Streamlit UI   │────│   FastAPI       │
│   Frontend      │    │   Backend       │
└─────────────────┘    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
           ┌────────▼──┐ ┌────▼───┐ ┌───▼────┐
           │ LangGraph │ │ Vector │ │ Model  │
           │ Workflow  │ │ DB     │ │ Router │
           │           │ │(Chroma)│ │        │
           └───────────┘ └────────┘ └────────┘
                              │         │
                    ┌─────────┼─────────┐
                    │         │         │
           ┌────────▼──┐ ┌────▼───┐ ┌───▼────┐
           │ API LLM   │ │ Local  │ │ Email  │
           │(OpenAI)   │ │ LLM    │ │ Service│
           │           │ │(Ollama)│ │        │
           └───────────┘ └────────┘ └────────┘
```

### Data Flow:

1. HR uploads/generates JD → JD is embedded and stored
2. Candidate data fetched and embedded → Stored in vector DB
3. Vector DB queried for best candidates → Matching scores generated
4. AI generates personalized emails → Results displayed in UI

## 📁 Project Structure

```
omni-assignment/
├── docker-compose.yml          # Docker orchestration
├── README.md                   # Project documentation
├── backend/                    # FastAPI backend
│   ├── Dockerfile              # Backend container config
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── ai_flow/                # AI workflow components
│   │   ├── graph.py            # LangGraph workflow for recruitment
│   │   └── __pycache__/
│   ├── core/                   # Core business logic
│   │   ├── chroma_client.py    # ChromaDB vector database client
│   │   ├── embeddings.py       # Text embedding utilities
│   │   ├── langgraph_workflow.py # JD generation workflow
│   │   ├── llm.py              # LLM configuration and routing
│   │   ├── logging.py          # Logging middleware
│   │   └── __pycache__/
│   ├── db/                     # Database layer
│   │   ├── db.py               # SQLAlchemy database setup
│   │   └── __pycache__/
│   ├── models/                 # Data models
│   │   ├── job_descriptions.py # JD model
│   │   ├── user.py             # User model
│   │   └── __pycache__/
│   ├── routes/                 # API endpoints
│   │   ├── candidates.py       # Candidate management
│   │   ├── choose_model.py     # Model selection
│   │   ├── email.py            # Email generation
│   │   ├── job_descriptions.py # JD operations
│   │   ├── match_score.py      # Matching logic
│   │   ├── user.py             # Authentication
│   │   └── __pycache__/
│   ├── schema/                 # Pydantic schemas
│   │   ├── candidates.py       # Candidate schemas
│   │   ├── choose_model.py     # Model schemas
│   │   ├── email.py            # Email schemas
│   │   ├── job_descriptions.py # JD schemas
│   │   ├── match_score.py      # Match schemas
│   │   ├── user.py             # User schemas
│   │   └── __pycache__/
│   ├── services/               # Business services
│   │   ├── candidates.py       # Candidate services
│   │   ├── email.py            # Email services
│   │   ├── job_descriptions.py # JD services
│   │   ├── match_score.py      # Matching services
│   │   └── __pycache__/
│   └── utilities/              # Utility functions
│       ├── auth.py             # Authentication utilities
│       ├── crypt.py            # Encryption utilities
│       ├── jd_parser.py        # JD parsing utilities
│       ├── mock_sources.py     # Mock data sources
│       └── __pycache__/
├── frontend/                   # Streamlit frontend
│   ├── Dockerfile              # Frontend container config
│   ├── app.py                  # Streamlit application
│   ├── requirements.txt        # Python dependencies
│   └── __pycache__/
└── chroma_db/                 # ChromaDB persistent storage
    ├── chroma.sqlite3
    └── [collection_dirs]/
```

## 🧠 Why LangGraph / LangChain

### LangGraph Selection:

LangGraph is chosen for AI orchestration because it provides:

- **State-based Workflows**: Maintains context across multi-step processes
- **Complex Reasoning Pipelines**: Better suited than plain LangChain for sequential workflows like JD → Candidate → Match → Email
- **Built-in Features**:
  - Model switching capabilities
  - Tool calling integration
  - Reasoning traceability and debugging
  - Conditional branching and loops

### LangChain Integration:

LangChain components are used for:

- **LLM Abstraction**: Unified interface for different LLM providers
- **Prompt Engineering**: Structured prompt templates and chains
- **Tool Integration**: Connecting LLMs with external tools and APIs
- **Memory Management**: Conversation history and context retention

### Workflow Benefits:

- **Recruitment Pipeline**: Structured flow from JD processing to email generation
- **Error Handling**: Built-in retry mechanisms and fallback strategies
- **Observability**: Graph visualization and execution tracing
- **Scalability**: Easy to extend with new nodes and edges

## 🗃️ Why Selected Vector DB (ChromaDB)

ChromaDB was selected as the vector database because:

### Technical Advantages:

- **Lightweight & Local-First**: No cloud dependency, runs locally
- **Metadata Filtering**: Supports complex queries with metadata
- **Easy Integration**: Python-native with simple API
- **Performance**: Fast similarity search with HNSW indexing

### Project-Specific Benefits:

- **Candidate Memory**: Efficient storage and retrieval of candidate profiles
- **JD Storage**: Semantic search across job descriptions
- **RAG Workflows**: Perfect for retrieval-augmented generation
- **Development Friendly**: Easy setup for local development and testing

### Alternatives Considered:

- **Pinecone**: Cloud-only, requires API keys and internet
- **Weaviate**: More complex setup and configuration
- **FAISS**: Lacks metadata filtering and persistence
- **ChromaDB**: Best fit for local, lightweight vector operations

## 🤖 Model Selection Strategy

The system implements a hybrid model approach supporting two modes:

### API-based Models (Primary):

- **OpenAI GPT Models** (GPT-4o-mini, GPT-4)
- **Use Cases**:
  - Job description generation
  - Candidate matching explanations
  - Personalized email generation
  - Complex reasoning tasks

### Local Models (Fallback):

- **Phi-3 / Mistral** via Ollama
- **Use Cases**:
  - Offline operation
  - Backup when API unavailable
  - Cost-sensitive scenarios
  - Privacy requirements

### Dynamic Switching:

- **Runtime Selection**: Switch models via `POST /model/select` endpoint
- **Configuration**: Environment-based model selection
- **Fallback Logic**: Automatic switch to local models on API failure

## ⚖️ Local vs API Model Trade-offs

| Aspect          | API Models              | Local Models                 |
| --------------- | ----------------------- | ---------------------------- |
| **Quality**     | Higher quality outputs  | Good but variable quality    |
| **Setup**       | Faster (API key only)   | Requires Ollama installation |
| **Cost**        | Paid per token          | Free (one-time setup)        |
| **Speed**       | Faster inference        | Slower on consumer hardware  |
| **Privacy**     | Data sent to providers  | Fully local, private         |
| **Reliability** | Dependent on internet   | Always available offline     |
| **Resources**   | Minimal local resources | Requires GPU/CPU resources   |

### Strategy:

- **Default**: API models for quality and speed
- **Fallback**: Local models for resilience and privacy
- **Hybrid**: Runtime switching based on requirements

## 🔌 API Endpoints

| Method | Endpoint             | Description                   |
| ------ | -------------------- | ----------------------------- |
| `GET`  | `/`                  | Health check with timestamp   |
| `POST` | `/auth/login`        | User authentication           |
| `POST` | `/auth/register`     | User registration             |
| `POST` | `/jd/upload`         | Upload JD (PDF, DOCX, TXT)    |
| `POST` | `/jd/generate`       | Generate JD using AI          |
| `GET`  | `/jd/list`           | List all job descriptions     |
| `POST` | `/model/select`      | Select LLM (API/Local)        |
| `POST` | `/candidates/fetch`  | Fetch candidates from sources |
| `POST` | `/candidates/store`  | Store candidate embeddings    |
| `GET`  | `/candidates/search` | Semantic candidate search     |
| `POST` | `/match/score`       | JD-candidate matching         |
| `POST` | `/email/send`        | Generate & send emails        |

### API Documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## ▶️ How to Run Locally (Without Docker)

### Prerequisites:

- Python 3.10+
- Ollama (for local models)
- OpenAI API key

### Backend Setup:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup:

```bash
cd frontend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

### Environment Variables:

Create `.env` file in backend directory:

```env
OPENAI_API_KEY=your_openai_key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
DATABASE_URL=sqlite:///./hr_agent.db
SECRET_KEY=your_secret_key
```

## 🐳 Docker Setup

### Prerequisites:

- Docker & Docker Compose
- `.env` file with required variables

### Quick Start:

```bash
# Clone repository
git clone <repository-url>
cd omni-assignment

# Create environment file
cp .env.example .env
# Edit .env with your API keys

# Build and run
docker-compose up --build
```

### Access Points:

| Service        | URL                          | Description             |
| -------------- | ---------------------------- | ----------------------- |
| Backend API    | `http://localhost:8000/docs` | FastAPI Swagger UI      |
| Frontend UI    | `http://localhost:8501`      | Streamlit Web Interface |
| Backend Health | `http://localhost:8000/`     | Health check endpoint   |

### Docker Commands:

```bash
# Build only
docker-compose build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up --build --force-recreate
```

## ⚠️ Assumptions & Limitations

### Assumptions:

- **Mock Data Sources**: Candidate APIs are simulated (LinkedIn, Naukri, etc.)
- **Single User**: Designed for individual HR user workflows
- **English Language**: All processing assumes English content
- **Limited Concurrency**: Not optimized for high concurrent users
- **Local Vector DB**: ChromaDB runs locally with file-based persistence

### Limitations:

- **No Authentication UI**: API-only authentication (no login forms)
- **Mock Integrations**: No real job portal API connections
- **No Persistent Relational DB**: Only vector database, no user/session persistence
- **Basic UI**: Streamlit interface is functional but not production-grade
- **Single JD Processing**: Processes one JD at a time
- **Email Dependencies**: Requires SMTP configuration for email features
- **Resource Intensive**: Local LLM requires significant hardware resources

## 🚀 Future Improvements

### High Priority:

- **Real API Integrations**: LinkedIn, Naukri, Indeed API connections
- **User Authentication UI**: Login/register forms in Streamlit
- **Resume Upload & Parsing**: PDF/DOCX resume processing
- **Multi-JD Support**: Batch processing multiple job descriptions
- **Database Migration**: PostgreSQL/MySQL for relational data

### Medium Priority:

- **Role-Based Access**: HR Admin, Recruiter, Manager roles
- **Feedback Loop**: User feedback for improving match scores
- **Streaming Responses**: Real-time LLM response streaming
- **Background Jobs**: Celery/Redis for async processing
- **Advanced Matching**: Skills gap analysis, culture fit scoring

### Low Priority:

- **Observability**: Comprehensive logging, metrics, tracing
- **Dashboard UI**: Analytics dashboard with charts and KPIs
- **Multi-Language Support**: Support for non-English content
- **Cloud Deployment**: AWS/GCP/Azure deployment configurations
- **Mobile App**: React Native mobile companion app
- **AI Model Fine-tuning**: Custom model training on recruitment data

## 📦 Tech Stack

### Backend:

- **Framework**: FastAPI (async, high performance)
- **AI Orchestration**: LangGraph + LangChain
- **Vector Database**: ChromaDB
- **LLM Providers**: OpenAI, Ollama (local)
- **Database**: SQLAlchemy + SQLite
- **Authentication**: JWT tokens
- **Email**: SMTP integration

### Frontend:

- **Framework**: Streamlit
- **HTTP Client**: Requests library
- **UI Components**: Streamlit native components

### Infrastructure:

- **Containerization**: Docker + Docker Compose
- **Process Management**: Uvicorn (backend), Streamlit (frontend)
- **Environment**: Python 3.10+
- **Dependencies**: Poetry/pip for package management

### Development Tools:

- **Linting**: Black, Flake8
- **Testing**: Pytest
- **Documentation**: Swagger/ReDoc auto-generated
- **Version Control**: Git

## 🏁 Conclusion

This AI-powered HR Recruitment Agent demonstrates:

- ✅ **End-to-end AI System Design**: Complete pipeline from JD to email
- ✅ **AI Orchestration**: LangGraph for complex workflows
- ✅ **Vector Memory**: ChromaDB for semantic search and RAG
- ✅ **Matching Logic**: Cosine similarity with AI-powered reasoning
- ✅ **Model Flexibility**: Dynamic switching between API and local LLMs
- ✅ **Production Readiness**: Docker containerization and API design
- ✅ **Scalable Architecture**: Modular design for easy extension
