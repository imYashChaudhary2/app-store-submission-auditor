# Source Index

This skill should always prefer current official Apple documentation over bundled notes.

When internet access is available, refresh these sources before producing a final submission-readiness audit.

## Primary Apple sources

- App Store Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- App Review overview: https://developer.apple.com/app-store/review/
- App Store Connect Help: https://developer.apple.com/help/app-store-connect/
- Upload builds: https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/
- TestFlight: https://developer.apple.com/testflight/
- User Privacy and Data Use: https://developer.apple.com/app-store/user-privacy-and-data-use/
- Privacy manifests: https://developer.apple.com/documentation/bundleresources/privacy_manifest_files
- Third-party SDK requirements: https://developer.apple.com/support/third-party-SDK-requirements/
- Account deletion guidance: https://developer.apple.com/support/offering-account-deletion-in-your-app/
- In-App Purchase: https://developer.apple.com/in-app-purchase/
- Subscriptions: https://developer.apple.com/app-store/subscriptions/
- Upcoming Requirements: https://developer.apple.com/news/upcoming-requirements/
- Certificates, identifiers, and profiles: https://developer.apple.com/account/resources/
- Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/
- Accessibility: https://developer.apple.com/accessibility/

## Audit source priority

1. Current official Apple documentation.
2. App Store Connect state and metadata supplied by the developer.
3. Repository evidence: code, project files, entitlements, privacy manifests, StoreKit files, Fastlane metadata, screenshots, privacy policy, support URLs.
4. This skill's checklists and templates.
5. Human confirmation from the app owner.

## Freshness rule

If the agent cannot verify current Apple policy online, the final report must include:

```text
Policy freshness: UNVERIFIED_CURRENT
```

If the agent verifies current Apple policy online, the final report should list the checked URLs and date.
