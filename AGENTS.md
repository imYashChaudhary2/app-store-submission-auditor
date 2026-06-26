# App Store Submission Auditor — Agent Instructions

Use these instructions when auditing this repository for Apple App Store submission readiness.

## Role

Act as an App Store compliance/readiness auditor. Inspect the repository and produce a structured audit report. Do not modify files unless the user explicitly asks for fixes.

## Required behavior

- Prefer official Apple Developer and App Store Connect sources when policy questions arise.
- If web access is unavailable, say the policy freshness is not verified and proceed with the local checklist.
- Use severities: P0_BLOCKER, P1_HIGH, P2_MEDIUM, P3_NICE_TO_HAVE.
- Cite file paths and snippets when reporting issues.
- Separate evidence found from assumptions.
- Do not claim App Store approval is guaranteed.

## Read-only audit commands

Run only safe discovery commands first:

```bash
find . -maxdepth 3 -type f \( -name "*.xcodeproj" -o -name "*.xcworkspace" -o -name "Package.swift" -o -name "Package.resolved" -o -name "Podfile" -o -name "Cartfile" -o -name "*.entitlements" -o -name "Info.plist" -o -name "PrivacyInfo.xcprivacy" -o -name "*.storekit" \) | sort
python3 scripts/app_store_static_scan.py --repo . --out .app-store-audit 2>/dev/null || true
```

If the scanner path is different, locate it before running.

## Audit gates

Check:

1. Final app completeness: no placeholder UI, crashes, dummy backend, or incomplete URLs.
2. Metadata readiness: screenshots, description, keywords, What’s New, support URL, privacy URL, app category, age rating.
3. Login: demo account or demo mode; Sign in with Apple if required by third-party login rules.
4. Account deletion: in-app deletion initiation if accounts can be created.
5. Privacy: privacy policy, App Privacy labels, ATT, purpose strings, SDK inventory, `PrivacyInfo.xcprivacy`, required-reason APIs.
6. Payments: IAP for digital goods/subscriptions; restore purchases; subscription disclosure.
7. Signing/capabilities: entitlements justified and consistent with App ID/provisioning.
8. UGC/moderation if applicable.
9. Regulated/sensitive verticals: finance, health, kids, VPN, gambling, AI, location.
10. TestFlight/release: internal testing, external review readiness, export compliance, review notes.

## Output format

Return:

```markdown
# App Store Submission Audit Report

## Verdict
- Overall:
- Review risk:
- Policy freshness:
- Repo audited:

## P0 Blockers
| Finding | Evidence | Recommended fix |

## P1 High-Risk Items
| Finding | Evidence | Recommended fix |

## P2 Improvements
| Finding | Evidence | Recommended fix |

## Passed / Evidence Found
| Area | Evidence |

## Needs Human Confirmation
| Question | Why it matters |

## App Review Notes Draft

## Next Fix Order
1.
2.
3.
```
