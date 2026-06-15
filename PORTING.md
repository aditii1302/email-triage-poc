# Porting Notes

This document describes how each local adapter maps to its production equivalent.
Every external dependency is consumed only through an interface in backend/app/interfaces/.
Swapping to production is a configuration change, not a code change.

---

## LLM Client

Local: OllamaLLMClient in backend/app/adapters/ollama_llm.py
Production: HostedLLMClient in backend/app/adapters/hosted_llm.py

Switch: Set LLM_PROVIDER=hosted in .env

Production mapping:
- classify_intent() -> POST to cloud LLM endpoint with intent classification prompt
- extract() -> POST to cloud LLM endpoint with extraction prompt
- describe_image() -> POST to vision-capable cloud LLM with base64 image

Auth: API key via HOSTED_LLM_API_KEY in .env
Note: Mock uses Ollama local inference. Production will use a cloud endpoint with faster response times.

---

## ITSM-A (Incident Platform)

Local: Mock FastAPI service on port 8001
Production: Real ITSM-A REST API

Switch: Set ITSM_A_BASE_URL to production URL in .env

Production mapping:
- POST /api/now/table/incident -> creates incident, returns sys_id and number
- GET /api/now/table/incident/{sys_id} -> fetches incident by ID
- PATCH /api/now/table/incident/{sys_id} -> updates status, priority, work notes
- GET /api/now/table/incident?sysparm_query=... -> searches incidents

Auth: Basic auth or OAuth2 via ITSM_A_USERNAME and ITSM_A_PASSWORD in .env
Note: Mock uses SQLite. Production uses the real ITSM-A database.

---

## ITSM-B (Service Desk Platform)

Local: Mock FastAPI service on port 8002
Production: Real ITSM-B REST API

Switch: Set ITSM_B_BASE_URL to production URL in .env

Production mapping:
- POST /rest/api/2/issue -> creates issue, returns id and key
- GET /rest/api/2/issue/{key} -> fetches issue by key
- PUT /rest/api/2/issue/{key} -> updates issue fields
- POST /rest/api/2/issue/{key}/comment -> adds comment
- POST /rest/api/2/search -> searches issues with JQL

Auth: Basic auth via ITSM_B_USERNAME and ITSM_B_API_TOKEN in .env
Note: Mock uses SQLite. Production uses the real ITSM-B database.

---

## Directory Service

Local: Mock FastAPI service on port 8003 with 25 fake users
Production: Microsoft Graph API / Entra ID

Switch: Set DIRECTORY_BASE_URL to production URL in .env

Production mapping:
- GET /users?email=... -> GET https://graph.microsoft.com/v1.0/users/{email}
- Returns: upn, display_name, department, manager

Auth: OAuth2 client credentials via AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID in .env
Note: Mock returns static fake data. Production returns real employee records.

---

## Vector Store

Local: ChromaDB embedded file-backed store in ./chroma_db
Production: Managed vector search service (e.g. Azure AI Search, Pinecone)

Switch: Set VECTOR_STORE=managed in .env and implement ManagedVectorStore adapter

Production mapping:
- collection.upsert() -> index document in managed vector store
- collection.query() -> similarity search in managed vector store

Note: Mock uses local files. Production uses a managed service with higher throughput.

---

## Mail Source

Local: File watcher on mailboxes/inbox_*/new/ folders
Production: Exchange/Microsoft 365 shared mailbox via Graph API

Switch: Implement GraphMailSource adapter and set MAIL_SOURCE=graph in .env

Production mapping:
- watchdog file watcher -> Graph API subscription (webhook) on shared mailbox
- .eml file -> Message object from Graph API
- moving files to folders -> marking messages as read/moving to folders via Graph API

Auth: OAuth2 via Microsoft Entra ID
Note: Mock uses local .eml files. Production watches live Exchange mailboxes.

---

## Bi-directional Sync

Local: Polling worker every 15 seconds in stage7_ticket.py
Production: Webhooks from both ITSM platforms

Switch: Replace polling loop with webhook endpoints in main.py
The sync logic itself (conflict resolution, field mapping) stays unchanged.
Only the transport layer changes from polling to webhook push.
