# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-01-01

### Fixed
- Fixed ConfidenceRing logic inversion (high confidence now displays green, low confidence displays red)
- Fixed ChatHeader hydration error (time rendering moved to client-side with useState + useEffect pattern)
- Enhanced WebSocket error handling with detailed WebSocketErrorDetails interface
- Implemented exponential backoff for WebSocket reconnection (3s * 2^attempt, max 30s)
- Added graceful degradation to REST API after 3 consecutive WebSocket failures
- Added WebSocket lifecycle management methods: disable(), enable(), isWebSocketDisabled()
- Removed dead code from ChatMessage component (unused imports: ThinkingState, useChatStore, isThinking)
- Improved code maintainability and bundle size through component cleanup

### Changed
- ChatMessage component is now a pure presentation component (no business logic)
- ChatHeader now updates time every 60 seconds using client-side rendering
- WebSocket reconnection strategy now uses exponential backoff instead of fixed intervals

### Performance
- Improved initial page load stability by eliminating hydration errors
- Reduced bundle size through removal of unused imports
- Enhanced WebSocket resilience with intelligent fallback mechanisms

## [1.0.0] - 2025-12-31

### Added
- Initial MVP release
- RAG pipeline with Qdrant vector search (native API)
- Hierarchical memory system (Redis short-term + PostgreSQL long-term)
- WebSocket real-time chat with thought streaming
- PDPA compliance features (30-minute session TTL, auto-expiry)
- Multi-document ingestion pipeline (PDF, DOCX, MD, etc.)
- Auto-escalation to human agents
- Confidence ring visual feedback system
- Session pulse PDPA countdown visualization
- Singapore business hours integration

### Architecture
- FastAPI backend with async/await patterns
- Next.js 15 frontend with Zustand state management
- Shadcn UI components (Radix primitives)
- Tailwind CSS with 2px radius utilitarian design
- Qdrant vector database for knowledge base
- Redis cache with TTL for session management
- PostgreSQL for long-term data persistence

### Features
- Real-time WebSocket thought events (assembling_context, validating_input, searching_knowledge, generating_response)
- Trust-centric UX with visual feedback
- Semantic chunking and recursive chunking strategies
- BGE cross-encoder reranking
- Context compression with token budget enforcement
- MarkItDown document parsing
- OpenRouter integration for LLM and embeddings

[1.0.1]: https://github.com/nordeim/singapore-smb-support-agent/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/nordeim/singapore-smb-support-agent/releases/tag/v1.0.0
