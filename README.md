# 🤖 NL → App Compiler — AI Engineer Demo Task

A system that behaves like a **compiler for software generation**: natural language → structured config → validated → executable → working application architecture.

> Built as a submission for the Base44 AI Engineer Internship Demo Task.

---

## 🎯 What It Does

Takes open-ended product descriptions like:

> *"Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."*

And converts them into a strict, complete, validated configuration covering:

- **UI Schema** — pages, components, layouts
- **API Schema** — endpoints, methods, validation rules
- **Database Schema** — tables, relations, field types
- **Auth System** — roles, permissions, access rules
- **Business Logic** — premium gating, role-based access, analytics

---

## 🏗️ Architecture — Multi-Stage Pipeline

The system is structured like a compiler with distinct, sequential stages. A single-prompt approach was explicitly avoided.

```
User Prompt
    │
    ▼
┌─────────────────────┐
│  Stage 1: Intent    │  Parse raw input → structured intermediate form
│  Extraction         │  (entities, features, roles, flows)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Stage 2: System    │  Convert intent → app architecture
│  Design Layer       │  (entity graph, data flows, role matrix)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Stage 3: Schema    │  Generate UI config, API config,
│  Generation         │  DB schema, Auth rules
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Stage 4: Refinement│  Resolve cross-layer inconsistencies,
│  & Validation       │  repair broken or hallucinated output
└─────────┬───────────┘
          │
          ▼
   Validated JSON Config
   (directly executable)
```

---

## 🔧 Key Components

### 1. Intent Extraction
- Parses free-form user input into a structured intermediate representation
- Identifies: entities, user roles, feature list, integrations, constraints

### 2. System Design Layer
- Maps extracted intent to an app architecture
- Produces: entity relationship graph, permission matrix, data flow diagram

### 3. Schema Generation
- Generates four parallel schemas:
  - `ui_schema` — page definitions, component trees, layout config
  - `api_schema` — REST endpoints, request/response types, validation
  - `db_schema` — tables, columns, types, relations, indexes
  - `auth_rules` — role definitions, resource-level permissions

### 4. Validation + Repair Engine *(Core)*
Detects and handles:
- Invalid or malformed JSON
- Missing required fields
- Hallucinated or undefined references
- Cross-layer mismatches (e.g., API field not in DB, UI field not in API)

Repair strategy:
- Targeted re-generation of specific failing layer (not blind full retry)
- Automatic patching for minor inconsistencies
- Clarification prompts for fundamentally underspecified inputs

---

## 📦 Output Format

All output is strict JSON. Example structure:

```json
{
  "meta": {
    "app_name": "CRM Platform",
    "assumptions": ["Payments via Stripe", "Email auth only"]
  },
  "db_schema": { ... },
  "api_schema": { ... },
  "ui_schema": { ... },
  "auth_rules": { ... },
  "business_logic": { ... }
}
```

Cross-layer consistency is enforced:
- Every API field maps to a DB column
- Every UI form field maps to an API endpoint
- Every protected route maps to an auth rule

---

## 🧪 Evaluation Framework

The system was tested against **20 prompts** (10 real product prompts + 10 edge cases).

### Edge Case Categories
- **Vague** — "Build me an app for my business"
- **Conflicting** — "All users are admins but only admins can delete"
- **Incomplete** — "Add payments" (no product context)

### Metrics Tracked

| Metric | Value |
|---|---|
| Overall success rate | — |
| Avg retries per request | — |
| Avg latency (end-to-end) | — |
| Repair vs re-generate ratio | — |
| Edge case pass rate | — |

> See `evaluation/results.json` for full run logs and per-prompt breakdowns.

---

## ⚖️ Cost vs Quality Tradeoffs

| Dimension | Approach |
|---|---|
| Latency | Parallel schema generation where stages allow |
| Cost | Lightweight models for extraction; stronger models for schema gen |
| Quality | Validation layer catches and repairs cheap-model errors |

---

## 🚀 Getting Started

### Prerequisites
- Node.js v18+ / Python 3.10+
- API key for the underlying LLM provider

### Installation

```bash
git clone https://github.com/sanju234-san/base44.git
cd base44
npm install        # or: pip install -r requirements.txt
cp .env.example .env
# Add your API key to .env
```

### Run

```bash
npm run dev        # Start the local interface
```

Or via CLI:

```bash
npm run generate -- --prompt "Build a CRM with login and role-based access"
```

### Environment Variables

```env
ANTHROPIC_API_KEY=your_key_here
# or
OPENAI_API_KEY=your_key_here
```

---

## 📁 Project Structure

```
base44/
├── pipeline/
│   ├── intent_extraction.js     # Stage 1
│   ├── system_design.js         # Stage 2
│   ├── schema_generation.js     # Stage 3
│   └── refinement.js            # Stage 4 — validation & repair
├── schemas/
│   ├── ui.schema.json           # UI output contract
│   ├── api.schema.json          # API output contract
│   ├── db.schema.json           # DB output contract
│   └── auth.schema.json         # Auth output contract
├── evaluation/
│   ├── prompts.json             # 20 test prompts
│   └── results.json             # Metrics per run
├── runtime/                     # Minimal execution layer
├── .env.example
└── README.md
```

---

## 📤 Submission

- **Live URL**: https://base44-hazel.vercel.app
- **Backend API**: https://base44-isuc.onrender.com/docs
- **GitHub**: https://github.com/sanju234-san/base44
- **Demo Video**: *(Loom — architecture walkthrough)*

---

## 📝 License

MIT
