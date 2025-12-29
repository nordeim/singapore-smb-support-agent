# Singapore SMB Customer Support AI Agent

An advanced, production-ready AI customer support agent designed for Singapore Small-to-Medium Businesses (SMBs). Built with cutting-edge RAG technology, hierarchical memory management, and full PDPA compliance.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 20+
- OpenRouter API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd singapore-smb-support-agent
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` with your credentials:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://agent_user:your_password@localhost:5432/support_agent
SECRET_KEY=your-secret-key-here
```

4. Start all services:
```bash
docker-compose up -d
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Features

### AI-Powered Customer Support
- **Advanced RAG Pipeline**: Multi-stage retrieval with hybrid search (BM25 + Dense vectors)
- **Hierarchical Memory**: Working, short-term (Redis), and long-term (PostgreSQL) memory layers
- **Context-Aware Responses**: Maintains conversation history and context
- **Auto-Escalation**: Intelligent handoff to human agents when confidence is low

### Technology Stack
- **Backend**: Python 3.11+, FastAPI, Pydantic AI, LangChain 0.3.x
- **Vector Database**: Qdrant with native sparse search (FastEmbedSparse)
- **LLM Provider**: OpenRouter API (cost-effective, multi-model)
- **Frontend**: React 18+, TypeScript, Tailwind CSS, Shadcn/UI
- **Database**: PostgreSQL 16 with SQLAlchemy async
- **Cache**: Redis 7 with 30min session TTL

### PDPA Compliance
- 30-day default data retention with auto-expiry
- Consent tracking and data minimization
- Anonymization for analytics
- Audit trail for all data access

## Project Structure

```
singapore-smb-support-agent/
├── backend/              # Python FastAPI application
│   ├── app/
│   │   ├── agent/      # Pydantic AI agent with tools
│   │   ├── api/        # REST endpoints and WebSocket
│   │   ├── rag/        # RAG pipeline implementation
│   │   ├── memory/     # Memory management system
│   │   └── ingestion/  # Document ingestion pipeline
│   ├── tests/          # Unit and integration tests
│   └── scripts/        # Utility scripts
├── frontend/            # React TypeScript application
│   └── src/
│       ├── components/  # React components
│       ├── lib/         # API and WebSocket clients
│       └── stores/      # Zustand state management
├── infrastructure/       # Docker configuration
└── docs/              # Documentation
```

## Development

### Backend Development

1. Activate virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Run backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run development server:
```bash
npm run dev
```

## Data Ingestion

Upload documents to the knowledge base:

```bash
python backend/scripts/ingest_documents.py \
  --input_dir ./data/documents \
  --collection knowledge_base \
  --chunking semantic
```

Supported formats: PDF, DOCX, XLSX, PPTX, HTML, Markdown, CSV

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | Login and get JWT token |
| `/api/chat` | POST | Send chat message |
| `/ws/chat/{session_id}` | WebSocket | Real-time chat streaming |
| `/api/feedback` | POST | Submit feedback on responses |

## Testing

### Run Backend Tests
```bash
cd backend
pytest
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

### Run RAG Evaluation
```bash
cd backend
python scripts/evaluate_rag.py
```

## Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

### Docker Deployment (Production)
```bash
docker-compose -f infrastructure/docker-compose.prod.yml up -d
```

## Performance Targets

| Metric | Target |
|--------|--------|
| Response Time (p50) | < 1.5s |
| Response Time (p95) | < 3.0s |
| Concurrent Users | 100+ |
| Uptime | 99.5% |
| Error Rate | < 0.1% |

## RAG Quality Metrics

| Metric | Target | Minimum |
|--------|--------|----------|
| Faithfulness | > 0.90 | > 0.85 |
| Answer Relevancy | > 0.85 | > 0.80 |
| Context Precision | > 0.80 | > 0.75 |
| Context Recall | > 0.85 | > 0.80 |

## Troubleshooting

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues and solutions.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## Support

For issues and questions, please open an issue on GitHub or contact support.

---

Built with ❤️ for Singapore SMBs
