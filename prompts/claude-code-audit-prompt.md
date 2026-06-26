Use the App Store Submission Auditor skill to audit this Apple app repo.

Run read-only checks first. Do not modify files unless I approve fixes.

Please:
1. Refresh official Apple policy if internet access is available.
2. Run the static scanner if present.
3. Inspect Info.plist, entitlements, PrivacyInfo.xcprivacy, StoreKit/IAP files, auth/login views, account deletion flow, subscription code, privacy/support URLs, and App Store metadata if present.
4. Produce a report with:
   - Overall verdict: READY / READY_WITH_WARNINGS / NOT_READY
   - P0 blockers
   - P1 high-risk items
   - P2 improvements
   - Evidence found with file paths
   - Questions needing human confirmation
   - Review notes draft
   - Exact next fix order

If the app belongs to a sensitive category, add category-specific checks based only on actual evidence: finance, health, kids, UGC/social, VPN, gambling, AI, location, identity, payments, subscriptions, or regulated services.
