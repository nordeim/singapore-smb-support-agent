# Phase 9: Data Preparation & Ingestion - Implementation Plan

**Date**: 2025-12-29
**Status**: 📋 PLANNING PHASE
**MVP Focus**: Populate knowledge base with Singapore SMB sample documents

---

## Executive Summary

Phase 9 involves creating and ingesting sample documents (FAQs, products, policies) into the Qdrant vector database. This will enable testing of the complete RAG pipeline with real Singapore SMB business context.

**Note**: Phase 3 ingestion pipeline and CLI tool are already implemented. Phase 9 focuses on data creation and testing.

---

## Current State

### ✅ Completed Components
- **Ingestion Pipeline**: `backend/app/ingestion/pipeline.py` (301 lines)
  - DocumentParser (12 formats)
  - SemanticChunker (sentence-transformers)
  - RecursiveChunker (fallback)
  - EmbeddingGenerator (OpenAI via OpenRouter)
  - Qdrant integration

- **CLI Tool**: `backend/scripts/ingest_documents.py` (314 lines)
  - Command-line interface
  - Batch processing
  - Progress tracking
  - Error handling

### ❌ Missing Components
- Sample documents (FAQs, products, policies)
- Ingestion testing
- Qdrant collection verification

---

## Phase 9 Task Breakdown (6 Tasks)

### Task 9.1: Create Sample FAQs (Singapore SMB Context)

**File**: `backend/data/faq/01_pricing.md`

**Content**:
- Service tiers (Basic, Professional, Enterprise)
- Pricing structure and discounts
- Contract terms

**File**: `backend/data/faq/02_business_hours.md`

**Content**:
- Operating schedule (9AM-6PM SGT, Mon-Fri)
- Public holidays 2025
- Emergency support availability

**File**: `backend/data/faq/03_services_overview.md`

**Content**:
- Service offerings
- Key features
- Support coverage

**File**: `backend/data/faq/04_returns_refunds.md`

**Content**:
- Return policy (14 days)
- Refund process
- Exclusions

**File**: `backend/data/faq/05_shipping_delivery.md`

**Content**:
- Delivery options
- Tracking methods
- Delivery timeline

---

### Task 9.2: Create Sample Products Catalog

**File**: `backend/data/products/product_catalog.md`

**Content**:
- Product listings
- Pricing and availability
- Technical specifications
- Categories

---

### Task 9.3: Create Sample Policies

**File**: `backend/data/policies/terms_of_service.md`

**Content**:
- Service terms and conditions
- Payment methods
- Service level agreements

**File**: `backend/data/policies/privacy_policy.md`

**Content**:
- PDPA-compliant privacy policy
- Data collection and usage
- Customer rights

**File**: `backend/data/policies/return_policy.md`

**Content**:
- Return policy details
- Exchange conditions
- Refund timeline

**File**: `backend/data/policies/shipping_policy.md`

**Content**:
- Shipping methods and costs
- Delivery timeline
- Tracking and insurance

---

### Task 9.4: Ingest Documents into Qdrant

**Command**:
```bash
python -m backend.scripts.ingest_documents \
  --input-dir ./backend/data \
  --collection knowledge_base \
  --chunk-strategy semantic \
  --batch-size 10 \
  --recursive \
  --verbose
```

**Expected Output**:
- All documents parsed with MarkItDown
- Semantic chunking applied
- Embeddings generated via OpenRouter
- Documents stored in Qdrant knowledge_base collection
- Statistics summary

---

### Task 9.5: Test Ingestion Pipeline

**Verification Steps**:
1. Check document parsing (MarkItDown)
2. Verify chunking (semantic strategy)
3. Validate embeddings (OpenAI via OpenRouter)
4. Test Qdrant upsert operations
5. Review ingestion statistics

---

### Task 9.6: Verify Qdrant Collection Population

**Verification Steps**:
1. Count documents in knowledge_base collection
2. Verify metadata (source, category, language, timestamps)
3. Test vector dimensions (1536)
4. Validate search functionality
5. Check RAG pipeline retrieval

---

## Implementation Order

### Phase 9.1: Data Creation (Tasks 9.1-9.3)
1. Create backend/data/ directory structure
2. Create FAQ documents (5 files)
3. Create product catalog (1 file)
4. Create policy documents (4 files)
5. Add metadata to documents

### Phase 9.2: Ingestion (Task 9.4)
1. Initialize Qdrant collections
2. Run ingestion CLI tool
3. Monitor ingestion progress
4. Review ingestion results

### Phase 9.3: Verification (Tasks 9.5-9.6)
1. Test document parsing
2. Verify Qdrant collection
3. Test RAG retrieval
4. Validate metadata
5. Document results

---

## File Structure After Phase 9

```
backend/
├── data/
│   ├── faq/
│   │   ├── 01_pricing.md
│   │   ├── 02_business_hours.md
│   │   ├── 03_services_overview.md
│   │   ├── 04_returns_refunds.md
│   │   └── 05_shipping_delivery.md
│   ├── products/
│   │   └── product_catalog.md
│   └── policies/
│       ├── terms_of_service.md
│       ├── privacy_policy.md
│       ├── return_policy.md
│       └── shipping_policy.md
```

**Note**: Ingestion pipeline and CLI tool already exist in Phase 3:
- `backend/app/ingestion/pipeline.py`
- `backend/scripts/ingest_documents.py`

---

## Execution Commands

### 1. Create Data Directory Structure
```bash
mkdir -p backend/data/faq
mkdir -p backend/data/products
mkdir -p backend/data/policies
```

### 2. Create Sample Documents
```bash
# Create FAQs
touch backend/data/faq/01_pricing.md
touch backend/data/faq/02_business_hours.md
touch backend/data/faq/03_services_overview.md
touch backend/data/faq/04_returns_refunds.md
touch backend/data/faq/05_shipping_delivery.md

# Create Products
touch backend/data/products/product_catalog.md

# Create Policies
touch backend/data/policies/terms_of_service.md
touch backend/data/policies/privacy_policy.md
touch backend/data/policies/return_policy.md
touch backend/data/policies/shipping_policy.md
```

### 3. Ingest Documents
```bash
cd backend
python -m scripts.ingest_documents \
  --input-dir ./data \
  --collection knowledge_base \
  --chunk-strategy semantic \
  --batch-size 5 \
  --recursive \
  --init-collections \
  --verbose
```

### 4. Verify Collection
```bash
# Start backend
docker-compose up -d

# Check Qdrant collection
curl http://localhost:6333/collections/knowledge_base

# Test retrieval (requires backend API)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "message": "What are your pricing plans?"
  }'
```

---

## Expected Results

### After Data Creation
- **10 markdown files** in backend/data/
- **Singapore SMB context** in all documents
- **Professional tone** and formatting

### After Ingestion
- **Documents stored** in Qdrant knowledge_base collection
- **Semantic chunks** created (512± tokens each)
- **Embeddings generated** (1536 dimensions, OpenAI via OpenRouter)
- **Metadata indexed** (source, category, language, timestamps)

### Statistics Expected
- **Total Documents**: 10 files
- **Estimated Chunks**: 50-100 chunks (5-10 per document)
- **Embedding Cost**: Minimal (semantic chunking reduces requests)
- **Ingestion Time**: ~5-10 minutes (depends on OpenRouter API)

---

## Testing Checklist

### Document Quality
- [ ] All files are valid markdown
- [ ] Content is clear and professional
- [ ] Singapore SMB context is authentic
- [ ] English language only (MVP)
- [ ] Formatting is consistent

### Ingestion Success
- [ ] All files parsed successfully
- [ ] No parsing errors
- [ ] Chunks generated (5-10 per document)
- [ ] Embeddings created
- [ ] Qdrant upsert successful
- [ ] Metadata stored correctly

### Qdrant Collection
- [ ] Collection exists (knowledge_base)
- [ ] Points count is correct
- [ ] Vector dimensions are 1536
- [ ] Metadata fields are present
- [ ] Search functionality works

### RAG Pipeline
- [ ] Documents can be retrieved
- - [ ] Relevance scores are reasonable
- - [ ] Context is returned correctly
- [ ] Sources are cited properly

---

## Risk Mitigation

### Ingestion Risks
**Risk**: Document parsing fails
**Mitigation**: Use MarkItDown (robust parser), error handling in CLI

**Risk**: Embedding API quota exceeded
**Mitigation**: Semantic chunking reduces requests, use OpenRouter credits

**Risk**: Qdrant collection not initialized
**Mitigation**: `--init-collections` flag in CLI tool

**Risk**: Chunking produces too many small chunks
**Mitigation**: Configurable chunk_size (512 tokens) and similarity_threshold (0.5)

### Quality Risks
**Risk**: Sample content is unrealistic
**Mitigation**: Use real Singapore SMB scenarios, professional language

**Risk**: Content is not comprehensive
**Mitigation**: Cover all major categories (pricing, hours, services, returns, shipping, policies, products)

---

## Success Criteria

### ✅ Data Creation
- [ ] All 10 sample documents created
- [ ] Content is Singapore SMB-appropriate
- [ ] Files are well-formatted markdown
- [ ] English language only (MVP)

### ✅ Ingestion
- [ ] All documents successfully ingested
- [ ] No critical errors
- [ ] Statistics logged
- [ ] Qdrant collection populated

### ✅ Verification
- [ ] Documents are searchable via RAG
- [ ] Relevance scores are reasonable
- [ ] Sources are properly cited
- [ ] Metadata is accurate

---

## Next Phase

**Phase 10: Testing & Dockerization** (0% complete)

Primary focus after Phase 9:
1. Create unit tests for all components
2. Create integration tests for API and pipeline
3. Create backend and frontend Dockerfiles
4. Update docker-compose.yml
5. Test full deployment locally
6. Run RAGAS evaluation (if enabled)

---

## Conclusion

Phase 9 is straightforward: create sample Singapore SMB documents and test the ingestion pipeline. All infrastructure is already in place from Phase 3.

**Estimated Duration**: 1-2 hours
**Complexity**: Low (data creation) to Medium (testing/verification)

---

**Plan Complete** ✅
