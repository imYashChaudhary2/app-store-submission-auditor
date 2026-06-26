# Claude Code Instructions — App Store Submission Audit

When the user asks for App Store submission readiness, use the `app-store-submission-auditor` skill in this repo.

## Default mode

Read-only audit mode. Do not edit project files unless the user explicitly approves fixes.

## Process

1. Read `SKILL.md` if present.
2. Run repository discovery.
3. Run `scripts/app_store_static_scan.py --repo . --out .app-store-audit` if present.
4. Inspect important files directly: Xcode project settings, `Info.plist`, `.entitlements`, `PrivacyInfo.xcprivacy`, StoreKit config, auth/login views, account deletion flow, subscription/purchase code, Fastlane/App Store metadata, privacy policy, support page references.
5. Produce a P0/P1/P2 audit report with evidence and file paths.
6. Ask for approval before modifying code.

## Sensitive-domain emphasis

Do not assume the app category from the repository name alone. Infer from actual code, metadata, screenshots, and user-provided context. If the app touches sensitive or regulated areas, add extra checks for:

- Financial or payment data, transaction records, or regulated financial claims.
- Health, fitness, wellness, medical claims, or HealthKit data.
- Kids, mixed-audience content, parental gates, and child privacy.
- User-generated content, chat, uploads, moderation, report/block flows.
- VPN, MDM, gambling, real-money, crypto/trading, identity, or location-sensitive features.
- AI features that process personal data or send data to third-party providers.
- Subscriptions, digital unlocks, credits, cloud features, and restore-purchase handling.
