# App Store Review Gate Checklist

Use this as the release gate before sending a build to App Review.

## P0 — Must pass before submission

- [ ] App launches on clean install without crash.
- [ ] Onboarding, login, main dashboard, core action, purchase, restore purchase, settings, privacy, support, and delete-account paths tested on physical device.
- [ ] No placeholder screens, dummy copy, disabled backend, test-only UI, or empty web pages.
- [ ] App Review can access the full app through a demo account or complete demo mode.
- [ ] Backend services needed for review are live.
- [ ] Privacy policy URL works and is accessible in the app.
- [ ] App Privacy labels match actual app + SDK behavior.
- [ ] ATT exists if tracking occurs.
- [ ] `PrivacyInfo.xcprivacy` and required-reason API declarations are handled where required.
- [ ] Account deletion can be initiated in-app if account creation exists.
- [ ] Digital premium features/subscriptions/credits use IAP unless a documented exception applies.
- [ ] IAP products are reviewable, visible, functional, and restorable where applicable.
- [ ] Support URL/contact is current.
- [ ] Export compliance answered.

## P1 — High review risk

- [ ] Sign in with Apple or equivalent privacy-friendly login exists if third-party/social login is used for primary account access.
- [ ] Screenshots and previews show real app UI, not future features.
- [ ] App name/subtitle/keywords avoid trademark stuffing or misleading claims.
- [ ] Age rating answers are accurate.
- [ ] Entitlements are justified and match capabilities.
- [ ] Third-party SDK inventory is documented.
- [ ] TestFlight internal testing completed.
- [ ] Accessibility smoke test completed: VoiceOver, Dynamic Type, contrast, tap targets.
- [ ] Localization/region-sensitive flows checked.
- [ ] App Review notes explain non-obvious features and sensitive flows.

## Sensitive or regulated domain add-on

- [ ] Sensitive data types are mapped in privacy docs, including financial, health, location, identity, child, user content, or AI-processing data if applicable.
- [ ] Data source and storage model are clearly disclosed: on-device, cloud sync, third-party services, analytics, crash reporting, AI processing, and retention.
- [ ] Imports, uploads, background processing, email parsing, document parsing, or account connections have explicit user consent where applicable.
- [ ] Category-specific claims avoid unsupported legal, medical, financial, safety, or guaranteed-results promises.
- [ ] Data export and deletion behavior are clear.
- [ ] AI processing discloses whether data leaves the device and which provider or processor receives it.
- [ ] Licenses, regulatory documents, entitlement approvals, or geo-restriction evidence are ready if relevant.

## Submission packet

- [ ] Demo credentials.
- [ ] App Review notes.
- [ ] Sample data/QR codes/documents if needed.
- [ ] Entitlement justifications.
- [ ] Licenses or regulatory documents if relevant.
- [ ] Privacy data map.
- [ ] IAP/subscription product matrix.
- [ ] Screenshots/previews by platform and locale.
