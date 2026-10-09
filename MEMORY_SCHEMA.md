# NISHA — Memory Schema

**Owner:** Sorie Adams Kamara  
**Version:** 1.0

---

## Memory Stores

NISHA maintains six separate memory stores, each with a distinct purpose:

### 1. Profile / Identity (`memory/long_term.json → identity`)
- name, age, birthday, city, role, faith, email, nationality
- Injected into every session prompt

### 2. Soul (`NISHA_SOUL.md`)
- NISHA's charter: values, protection priorities, voice, rules
- Version-controlled. Owner-editable only.

### 3. Projects (`memory/long_term.json → projects`)
- Active project names, goals, GitHub links
- Source links, MVP scopes

### 4. Episodic History (`memory/rag_store.json`)
- Task, result, evidence, correction, outcome
- Retrieved by semantic similarity (RAG)
- Max 500 entries, oldest trimmed first

### 5. Vault (`memory/vault/.nisha_vault.enc`)
- Credentials, API keys, sensitive notes
- Encrypted at rest (password-protected)
- **NEVER injected into prompt logs or shared with any cloud service**
- Access: `vault.get(key, password)` — requires password each time

### 6. Audit (`memory/audit/*.jsonl`)
- Approvals, tool calls, data sharing, screenshots, errors
- One JSONL file per agent + orchestrator
- Append-only, never modified

---

## Memory Schema (long_term.json)

```json
{
  "identity": {
    "name":        { "value": "Sorie Adams Kamara", "updated": "YYYY-MM-DD" },
    "city":        { "value": "Freetown, Sierra Leone", "updated": "YYYY-MM-DD" },
    "role":        { "value": "IT Administrator, IPAM student", "updated": "YYYY-MM-DD" },
    "faith":       { "value": "Christian (Baptist) — Winners Baptist Church, BCSL", "updated": "YYYY-MM-DD" }
  },
  "preferences": {
    "stack":       { "value": "Flutter, Dart, Supabase, Python", "updated": "YYYY-MM-DD" }
  },
  "projects": {
    "ai_assistant": { "value": "NISHA — personal agentic AI", "updated": "YYYY-MM-DD" }
  },
  "relationships": {},
  "wishes": {},
  "notes": {
    "machine": { "value": "Two Windows laptops: 12 GB RAM / 24 GB RAM", "updated": "YYYY-MM-DD" }
  }
}
```

---

## Injection Rules

1. Long-term memory → injected at every session start
2. RAG episodic memory → retrieved on-demand by query similarity
3. Vault → NEVER injected; accessed only by explicit vault tool call
4. Audit → NEVER injected; read-only for review

---

## Data Handling Rules

- **Local-first** — all memory stored locally on Sorie's machine
- **Ask before sending** any personal material to an online AI service
- **Encrypted vault** for secrets; never in prompt logs
- **View/edit/export/delete** controls always available to Sorie Adams
- **Max value length:** 380 characters per memory entry
- **Max total memory prompt:** 2200 characters
