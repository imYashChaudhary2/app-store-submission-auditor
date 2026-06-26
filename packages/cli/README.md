# App Store Submission Auditor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Platform](https://img.shields.io/badge/platform-Apple%20App%20Store-black)
![Agent Ready](https://img.shields.io/badge/agent-Claude%20Code%20%7C%20Codex-blue)

A reusable **Claude Code, Codex, and terminal-agent skill** for auditing Apple App Store submission readiness before you send a build to App Review.

It turns App Store submission work into a repeatable release gate: repository scan, policy checklist, privacy review, metadata review, IAP review, account-deletion review, signing/capability review, TestFlight readiness, and App Review notes preparation.

> This project does **not** guarantee App Store approval. It helps developers find likely blockers and evidence gaps before submission.

## Why this exists

App Store review problems usually come from boring-but-deadly mismatches:

- the app works, but screenshots describe features that are not shipped yet;
- the app has account creation, but no in-app account deletion path;
- a third-party SDK collects data, but App Privacy answers do not mention it;
- digital features are unlocked outside In-App Purchase;
- App Review cannot access the full app because the demo account or backend is broken;
- entitlements/capabilities are enabled without a clear need.

This skill gives AI coding agents a structured way to catch those issues early.

## What it checks

| Area | Checks |
|---|---|
| App completeness | launch flow, placeholders, broken URLs, demo account/demo mode, backend readiness |
| Metadata | screenshots, previews, description, keywords, support URL, privacy URL, age rating |
| Privacy | privacy policy, App Privacy labels, permission strings, ATT, SDK data collection |
| SDK compliance | `PrivacyInfo.xcprivacy`, required-reason APIs, SDK inventory, signatures/evidence |
| Login | third-party login rules, Sign in with Apple/equivalent login, forced login risk |
| Account deletion | in-app deletion initiation, full deletion vs deactivation, subscription notes |
| Payments | In-App Purchase, subscriptions, restore purchases, external payment risk |
| Signing/capabilities | entitlements, App ID/capability match, managed entitlement justification |
| Sensitive domains | kids, health, finance, UGC, AI, VPN, gambling, crypto/trading, location, identity |
| Release readiness | TestFlight, export compliance, App Review notes, evidence packet |

## Repository contents

```text
app-store-submission-auditor/
├── README.md
├── SKILL.md                              # Main skill instructions
├── AGENTS.md                             # Codex / generic coding-agent instructions
├── CLAUDE.md                             # Claude Code project-level instructions
├── skill_manifest.json
├── checklists/
│   ├── app_store_policy_matrix.yaml
│   └── review_gate_checklist.md
├── prompts/
│   ├── claude-code-audit-prompt.md
│   └── codex-audit-prompt.md
├── references/
│   └── source-index.md
├── scripts/
│   ├── app_store_static_scan.py
│   └── app_store_audit.sh
└── templates/
    ├── app_review_notes_template.md
    ├── audit_report_template.md
    └── privacy_data_map.csv
```

## Quick start

Clone this repository:

```bash
git clone https://github.com/imYashChaudhary2/app-store-submission-auditor.git
cd app-store-submission-auditor
```

Run the scanner against an Apple app repository:

```bash
python3 scripts/app_store_static_scan.py --repo /path/to/your/app --out /path/to/your/app/.app-store-audit
```

Or use the shell wrapper:

```bash
bash scripts/app_store_audit.sh /path/to/your/app
```

Open the generated report:

```bash
open /path/to/your/app/.app-store-audit/app-store-static-scan.md
```

## Install for Claude Code

### Option A: project-scoped skill

From your app repository:

```bash
mkdir -p .claude/skills/app-store-submission-auditor
cp -R /path/to/app-store-submission-auditor/* .claude/skills/app-store-submission-auditor/
```

Then ask Claude Code:

```text
Use the App Store Submission Auditor skill in .claude/skills/app-store-submission-auditor to audit this repo for App Store submission readiness. Run read-only scans first. Produce a P0/P1/P2 report with evidence and exact file paths. Do not modify files unless I approve fixes.
```

### Option B: user/global skill folder

If your Claude setup supports a global skills directory:

```bash
mkdir -p ~/.claude/skills
cp -R /path/to/app-store-submission-auditor ~/.claude/skills/app-store-submission-auditor
```

Then use this prompt inside any Apple app repo:

```text
Use the app-store-submission-auditor skill to review this repository before App Store submission.
```

## Install for Codex or generic agents

Copy `AGENTS.md` into your app repository root, or merge its contents into your existing `AGENTS.md`:

```bash
cp /path/to/app-store-submission-auditor/AGENTS.md /path/to/your/app/AGENTS.md
```

Then ask your coding agent:

```text
Follow AGENTS.md and run the App Store submission audit. Use the static scanner if available. Return P0 blockers, P1 high-risk items, P2 improvements, evidence paths, and the next fix order. Do not change source files.
```

## Recommended audit workflow

1. **Refresh policy** — the agent checks current Apple Developer/App Store Connect sources if web access exists.
2. **Discover repo structure** — Xcode project, workspace, Info.plist, entitlements, StoreKit config, privacy manifests, metadata folders.
3. **Run static scanner** — read-only evidence collection.
4. **Inspect high-risk flows** — login, account deletion, purchases, restore purchases, permissions, SDKs, privacy policy, App Review notes.
5. **Generate report** — P0/P1/P2 findings with evidence and exact file paths.
6. **Fix only after approval** — the skill defaults to read-only mode.

## Severity model

| Severity | Meaning |
|---|---|
| `P0_BLOCKER` | Likely rejection, invalid binary, legal/safety issue, or missing mandatory flow |
| `P1_HIGH` | High review risk or missing evidence that often causes back-and-forth |
| `P2_MEDIUM` | Should fix before launch, may not block every review |
| `P3_NICE_TO_HAVE` | Launch quality, maintainability, or polish improvement |

## Example output

```markdown
# App Store Submission Audit Report

## Verdict
- Overall: READY_WITH_WARNINGS
- Review risk: Medium
- Policy freshness: VERIFIED_CURRENT
- Repo audited: /Users/dev/MyApp

## P0 Blockers
| Finding | Evidence | Why Apple may care | Recommended fix |
|---|---|---|---|
| Account creation exists but no deletion flow was found | `AuthView.swift`, `SettingsView.swift` | Apps with account creation must support in-app deletion initiation | Add delete-account path under Settings > Account |

## P1 High-Risk Items
| Finding | Evidence | Recommended fix |
|---|---|---|
| PrivacyInfo.xcprivacy not found | scanner output | Add privacy manifest / verify SDK requirements |
```

## Manual checklist

Use the checklist before submitting:

```bash
cat checklists/review_gate_checklist.md
```

The checklist is useful even without an AI agent.

## Static scanner notes

The scanner is intentionally conservative. It does not prove compliance. It only collects evidence and flags likely review risks.

It looks for:

- app metadata files;
- entitlement files;
- privacy manifests;
- permission strings;
- StoreKit/IAP hints;
- login and account-deletion hints;
- third-party SDK hints;
- external payment keywords;
- UGC, AI, health, kids, finance, VPN, location, crypto/trading, and other sensitive-domain indicators.

## Safety model

This skill is **read-only by default**.

Agents using it should not:

- modify source files without explicit approval;
- bypass or hide functionality from App Review;
- create deceptive metadata;
- claim guaranteed App Store approval;
- replace legal review for regulated domains.

## Keeping policy fresh

Apple requirements change. Before a production submission, check current Apple sources listed in [`references/source-index.md`](references/source-index.md), especially:

- App Store Review Guidelines;
- Upcoming Requirements;
- User Privacy and Data Use;
- Third-party SDK requirements;
- account deletion guidance;
- App Store Connect Help for privacy, IAP, TestFlight, screenshots, age rating, export compliance, and review submission.

## Contributing

Contributions are welcome. Good contributions include:

- new static scanner checks;
- clearer App Review checklist items;
- better prompts for Claude Code, Codex, and other agents;
- updated Apple source links;
- sample audit reports;
- false-positive reductions.

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a PR.

## License

MIT. See [`LICENSE`](LICENSE).
