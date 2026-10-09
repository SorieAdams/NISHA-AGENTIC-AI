# NISHA — Approval Policy

**Owner:** Sorie Adams Kamara  
**Version:** 1.0  
**Status:** Active

---

## Approval Card Format

Every action requiring approval must produce a card with:

| Field | Description |
|---|---|
| **Intent** | What the agent is trying to accomplish |
| **Data used** | What data will be accessed or sent |
| **Target system** | Which system will be affected |
| **Irreversible** | Yes/No — can this be undone? |
| **Rollback** | How to undo if something goes wrong |
| **Exact action** | The precise command/operation |

---

## Policy Table

| Action Class | Policy |
|---|---|
| Public research, local planning, drafting | ✅ May proceed — logged |
| Local file read | ✅ May proceed — logged |
| Local file write/modify | ⚠️ Propose diff; request approval if important files |
| Git commits | ⚠️ Show diff and tests; approval before push |
| Git push | 🔴 Explicit approval required |
| Email, message, post, application | 🔴 Draft only; explicit approval before send/submit |
| Account login, MFA, permissions | 🔴 Pause and ask |
| Upload to cloud AI / external service | 🔴 Ask if personal/private data included |
| Money, contracts, purchases | 🔴 Always ask; show exact consequences |
| File deletion | 🔴 Always ask; show what will be deleted |
| Publishing content externally | 🔴 Always ask |

---

## Agents & Their Authority

| Agent | Authority Level | May Do | May Never Do |
|---|---|---|---|
| **Nisha** | Orchestrator | Plan, draft, route, research, remember | Send, publish, delete without approval |
| **Scout** | Read-only | Public web research | Send personal data externally |
| **Asha** | Sandbox | Local code, local git, local tests | Push to GitHub without approval |
| **Mira** | Read-only | Draft applications, update local tracker | Send applications, contact anyone |
| **Operator** | Gated | Execute approved workflows only | Execute undeclared steps |

---

## Deviation Response

When a deviation is detected:
1. **Log** — record the deviation with agent, type, declared vs seen
2. **Alert** — notify Sorie Adams immediately
3. **Block** — do not execute the deviated action on new traffic
4. **Wait** — for review: dismiss or enforce

*Deviations are typed, auditable events. Enforcement is operator-controlled and reversible.*
