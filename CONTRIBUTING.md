# Contributing

Thanks for helping improve App Store Submission Auditor.

## Good first contributions

- Add a new static scanner check with a low false-positive rate.
- Improve `review_gate_checklist.md` with clearer release-gate wording.
- Update `references/source-index.md` when Apple documentation URLs change.
- Add better prompts for Claude Code, Codex, or other coding agents.
- Improve templates for App Review notes, privacy data maps, or audit reports.

## Contribution rules

1. Keep the skill generic. Do not add product-specific assumptions.
2. Prefer official Apple sources when changing policy guidance.
3. Do not claim that the skill guarantees App Store approval.
4. Keep scanner behavior read-only by default.
5. Include evidence-oriented wording: file paths, snippets, observed behavior, and human-confirmation gaps.
6. Avoid aggressive checks that create noisy false positives.

## Pull request checklist

- [ ] The change is generic and reusable across Apple app categories.
- [ ] Policy guidance is backed by official Apple documentation when possible.
- [ ] Scanner changes are read-only.
- [ ] New generated output is ignored by `.gitignore` if needed.
- [ ] README or examples are updated if behavior changed.

## Commit style

Use clear commit messages, for example:

```text
Add StoreKit product detection to scanner
Improve App Review notes template
Update Apple source index
```
