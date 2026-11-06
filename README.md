# Groupware AI Chatbot – Graph Data Architecture & Validation Harness

## Overview
This repository contains the architecture, data discovery models, ETL synchronization specifications, security controls, and automated validation harness for the **Groupware AI Chatbot** project.

- **Source of Truth**: PostgreSQL 18.6
- **Operational & Semantic Graph**: Neo4j 5.26+ (Architecture B)
- **Vector DB**: Dedicated embedding & retrieval store (ChatMessage Option A)

## Repository Structure
- `documentation/phase-1-database-discovery/`: Canonical Architecture Documents 01 through 39.
- `docs/`: Phase 1.2+ Canonical Specifications (Docs 29 through 39).
- `scripts/`:
  - `phase1_2_1/`: Phase 1.2.1 Document consistency validator (13 checks).
  - `phase1_2_2/`: Phase 1.2.2 Core modules runner.
  - `phase1_2_3_1/`: Phase 1.2.3.1 Corrective validators, Circuit Breaker, Status Aggregator, and Master Orchestrator.
- `tests/`:
  - `phase1_2_3_1/`: Independent relational and graph simulators, unit tests (`test_independent_executors.py`, `test_circuit_breaker.py`, `test_hard_delete_approval.py`, `test_runner_failure_injection.py`), and fixtures.
- `artifacts/phase1_2_3_1/`: Evidence reports, execution logs, and defect closure registers.

## Running the Master Validation Suite
```bash
python scripts/phase1_2_3_1/run_all.py
```

## Running Deliverable Packaging & Self-Contained Verification
```bash
python scripts/phase1_2_3_1/package_deliverables.py
```

## Running Local LLM Serving (vLLM) & Web Chat UI

### 1. Khởi chạy vLLM Serving (Qwen2.5-7B)
```bash
./scripts/serve_vllm.sh
```

### 2. Khởi chạy Giao diện Chatbot (Web UI)
Mở một terminal mới và chạy:
```bash
./scripts/run_ui.sh
# hoặc: python main.py chat-ui
```
Sau đó mở trình duyệt truy cập: **`http://localhost:8080`**

