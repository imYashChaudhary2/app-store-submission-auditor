#!/usr/bin/env python3
"""Read-only App Store submission static scanner.

This scanner does not prove App Store compliance. It collects evidence and flags likely
review risks for a coding agent or human reviewer to inspect.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import plistlib
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Dict, Any, Tuple

EXCLUDE_DIRS = {
    ".git", ".svn", ".hg", "DerivedData", "build", ".build", "node_modules",
    ".app-store-audit", ".venv", "venv", "Carthage/Build", "Pods/Target Support Files"
}
TEXT_EXTS = {".swift", ".m", ".mm", ".h", ".plist", ".xcprivacy", ".json", ".md", ".txt", ".yml", ".yaml", ".storekit", ".pbxproj", ".strings", ".entitlements", ".ts", ".tsx", ".js", ".jsx"}

@dataclass
class Finding:
    severity: str
    category: str
    title: str
    evidence: str
    recommendation: str


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDE_DIRS:
        return True
    # Skip very large generated folders by name fragments
    return any(part in EXCLUDE_DIRS for part in path.parts)


def iter_files(repo: Path) -> Iterable[Path]:
    for p in repo.rglob("*"):
        if p.is_dir():
            continue
        if should_skip(p.relative_to(repo)):
            continue
        try:
            if p.stat().st_size > 2_500_000:
                continue
        except OSError:
            continue
        yield p


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def grep(files: List[Path], patterns: List[str], flags=re.IGNORECASE) -> List[Tuple[Path, str]]:
    compiled = [re.compile(p, flags) for p in patterns]
    hits = []
    for f in files:
        if f.suffix.lower() not in TEXT_EXTS:
            continue
        txt = read_text(f)
        if not txt:
            continue
        for rx in compiled:
            m = rx.search(txt)
            if m:
                hits.append((f, m.group(0)[:120].replace("\n", " ")))
                break
    return hits


def rel(repo: Path, path: Path) -> str:
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return str(path)


def parse_plist(path: Path) -> Dict[str, Any] | None:
    try:
        with path.open("rb") as f:
            return plistlib.load(f)
    except Exception:
        # Xcode plists may contain build settings like $(PRODUCT_BUNDLE_IDENTIFIER)
        return None


def collect_sdk_inventory(repo: Path, files: List[Path]) -> Dict[str, Any]:
    inventory: Dict[str, Any] = {"package_resolved": [], "podfile": [], "cartfile": [], "package_json": []}
    for f in files:
        name = f.name
        if name == "Package.resolved":
            txt = read_text(f)
            inventory["package_resolved"].append({"path": rel(repo, f), "mentions": sorted(set(re.findall(r'"identity"\s*:\s*"([^"]+)"', txt) + re.findall(r'"package"\s*:\s*"([^"]+)"', txt)))[:100]})
        elif name == "Podfile":
            txt = read_text(f)
            pods = re.findall(r"pod\s+['\"]([^'\"]+)['\"]", txt)
            inventory["podfile"].append({"path": rel(repo, f), "mentions": sorted(set(pods))[:100]})
        elif name == "Cartfile":
            txt = read_text(f)
            lines = [ln.strip() for ln in txt.splitlines() if ln.strip() and not ln.strip().startswith("#")]
            inventory["cartfile"].append({"path": rel(repo, f), "mentions": lines[:100]})
        elif name == "package.json":
            try:
                data = json.loads(read_text(f))
                deps = sorted(list((data.get("dependencies") or {}).keys()) + list((data.get("devDependencies") or {}).keys()))
            except Exception:
                deps = []
            inventory["package_json"].append({"path": rel(repo, f), "mentions": deps[:120]})
    return inventory


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="Repository root to scan")
    ap.add_argument("--out", default=".app-store-audit", help="Output directory")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    files = list(iter_files(repo))
    rel_files = [rel(repo, f) for f in files]
    findings: List[Finding] = []
    evidence: Dict[str, Any] = {}

    # Project surfaces
    xcodeproj = [f for f in files if f.name.endswith(".xcodeproj") or ".xcodeproj" in str(f)]
    workspaces = [f for f in files if f.name.endswith(".xcworkspace") or ".xcworkspace" in str(f)]
    info_plists = [f for f in files if f.name == "Info.plist"]
    entitlements = [f for f in files if f.suffix == ".entitlements"]
    privacy_manifests = [f for f in files if f.name == "PrivacyInfo.xcprivacy"]
    storekit_files = [f for f in files if f.suffix == ".storekit"]
    fastlane_dirs = sorted({rel(repo, f.parent) for f in files if "fastlane" in f.parts})

    evidence["project"] = {
        "xcodeproj_or_pbxproj": [rel(repo, f) for f in xcodeproj[:20]],
        "workspaces": [rel(repo, f) for f in workspaces[:20]],
        "info_plists": [rel(repo, f) for f in info_plists[:20]],
        "entitlements": [rel(repo, f) for f in entitlements[:20]],
        "privacy_manifests": [rel(repo, f) for f in privacy_manifests[:20]],
        "storekit_files": [rel(repo, f) for f in storekit_files[:20]],
        "fastlane_dirs": fastlane_dirs[:20],
    }

    if not xcodeproj and not workspaces and not any(f.name == "project.pbxproj" for f in files):
        findings.append(Finding("P1_HIGH", "Build", "No obvious Xcode project/workspace found", "No .xcodeproj/.xcworkspace/project.pbxproj found in scanned files", "Confirm this is the repo root or add the Apple app project before App Store audit."))

    # Plist analysis
    plist_summaries = []
    permission_keys_seen = []
    for p in info_plists:
        data = parse_plist(p)
        if isinstance(data, dict):
            keys = sorted(data.keys())
            permission_keys_seen.extend([k for k in keys if k.startswith("NS") and k.endswith("UsageDescription")])
            plist_summaries.append({
                "path": rel(repo, p),
                "bundle_id": data.get("CFBundleIdentifier"),
                "short_version": data.get("CFBundleShortVersionString"),
                "build": data.get("CFBundleVersion"),
                "permission_purpose_keys": [k for k in keys if k.startswith("NS") and k.endswith("UsageDescription")],
                "tracking_usage_description": "NSUserTrackingUsageDescription" in data,
            })
        else:
            plist_summaries.append({"path": rel(repo, p), "parse": "unparsed_or_template"})
    evidence["info_plist_summary"] = plist_summaries

    # Entitlements analysis
    ent_summaries = []
    for p in entitlements:
        data = parse_plist(p)
        if isinstance(data, dict):
            ent_summaries.append({"path": rel(repo, p), "keys": sorted(data.keys())})
        else:
            ent_summaries.append({"path": rel(repo, p), "parse": "unparsed_or_template"})
    evidence["entitlements_summary"] = ent_summaries

    # Privacy manifest analysis
    privacy_summaries = []
    for p in privacy_manifests:
        data = parse_plist(p)
        if isinstance(data, dict):
            privacy_summaries.append({
                "path": rel(repo, p),
                "keys": sorted(data.keys()),
                "tracking": data.get("NSPrivacyTracking"),
                "collected_data_count": len(data.get("NSPrivacyCollectedDataTypes") or []),
                "accessed_api_count": len(data.get("NSPrivacyAccessedAPITypes") or []),
            })
        else:
            privacy_summaries.append({"path": rel(repo, p), "parse": "unparsed_or_template"})
    evidence["privacy_manifest_summary"] = privacy_summaries

    # Keyword evidence
    text_files = [f for f in files if f.suffix.lower() in TEXT_EXTS]
    patterns = {
        "login_third_party": [r"GoogleSignIn", r"GIDSignIn", r"FBSDK", r"FacebookLogin", r"OAuth", r"Sign in with Google", r"continue with google", r"FirebaseAuth"],
        "sign_in_with_apple": [r"ASAuthorizationAppleIDProvider", r"SignInWithApple", r"sign in with apple", r"com\.apple\.developer\.applesignin"],
        "account_creation": [r"create account", r"sign up", r"signup", r"register", r"createUser", r"createUserWithEmail"],
        "account_deletion": [r"delete account", r"account deletion", r"DeleteAccount", r"remove account", r"deleteUser", r"currentUser\.delete", r"revoke.*Apple"],
        "iap_storekit": [r"StoreKit", r"Product\.products", r"Transaction\.currentEntitlements", r"purchase\(", r"restore purchases", r"RevenueCat", r"Purchases\.configure"],
        "external_payment": [r"Stripe", r"Razorpay", r"PayPal", r"Cashfree", r"checkout", r"payment link", r"web checkout"],
        "premium_digital": [r"premium", r"subscription", r"pro plan", r"unlock", r"credits", r"AI credits", r"cloud sync"],
        "privacy_policy": [r"privacy policy", r"/privacy", r"PrivacyPolicy"],
        "support_url": [r"support", r"contact us", r"help center"],
        "att_tracking": [r"AppTrackingTransparency", r"ATTrackingManager", r"NSUserTrackingUsageDescription", r"IDFA", r"AdSupport"],
        "required_reason_api_hints": [r"UserDefaults", r"systemUptime", r"mach_absolute_time", r"creationDate", r"modificationDate", r"volumeAvailableCapacity", r"stat\(", r"fstat\("],
        "ugc_hints": [r"comment", r"post", r"chat", r"message", r"upload", r"report user", r"block user", r"moderation"],
        "sensitive_data_hints": [r"transaction", r"expense", r"budget", r"wallet", r"bank", r"upi", r"receipt", r"net worth", r"investment", r"statement", r"account aggregator", r"health", r"medical", r"diagnosis", r"treatment", r"fitness", r"location", r"contacts", r"identity", r"passport", r"aadhaar", r"social security", r"child", r"kids", r"minor", r"gambling", r"betting", r"vpn", r"mdm", r"crypto", r"trading"],
        "ai_hints": [r"OpenAI", r"Anthropic", r"Gemini", r"AI", r"LLM", r"prompt", r"assistant", r"machine learning"],
        "accessibility": [r"accessibilityLabel", r"accessibilityIdentifier", r"VoiceOver", r"Dynamic Type", r"\.accessibility"],
    }
    hits = {k: [(rel(repo, p), m) for p, m in grep(text_files, v)] for k, v in patterns.items()}
    evidence["keyword_hits"] = {k: v[:50] for k, v in hits.items() if v}

    # Heuristic findings
    if hits["att_tracking"] and not any("NSUserTrackingUsageDescription" in str(x) for x in plist_summaries) and not permission_keys_seen:
        findings.append(Finding("P0_BLOCKER", "Privacy/ATT", "Tracking-related code found but no parsed NSUserTrackingUsageDescription evidence", str(hits["att_tracking"][:5]), "Verify ATT usage and add a clear NSUserTrackingUsageDescription if tracking or IDFA access occurs."))

    if hits["required_reason_api_hints"] and not privacy_manifests:
        findings.append(Finding("P1_HIGH", "Privacy manifest", "Potential required-reason API usage but no PrivacyInfo.xcprivacy found", str(hits["required_reason_api_hints"][:8]), "Review Apple required-reason API rules and add PrivacyInfo.xcprivacy declarations where required."))

    if hits["account_creation"] and not hits["account_deletion"]:
        findings.append(Finding("P0_BLOCKER", "Account deletion", "Account creation hints found but no account deletion flow evidence", str(hits["account_creation"][:8]), "Add or verify an in-app Delete Account initiation path and document it in App Review notes."))

    if hits["login_third_party"] and not hits["sign_in_with_apple"]:
        findings.append(Finding("P1_HIGH", "Login", "Third-party login hints found but no Sign in with Apple evidence", str(hits["login_third_party"][:8]), "If third-party/social login is used for primary account access, add Sign in with Apple or document an applicable exception."))

    if hits["external_payment"] and hits["premium_digital"]:
        findings.append(Finding("P0_BLOCKER", "Payments/IAP", "External payment provider and premium digital feature hints both found", f"payments={hits['external_payment'][:6]} premium={hits['premium_digital'][:6]}", "Verify all in-app digital unlocks/subscriptions use Apple IAP unless a specific exception/entitlement applies."))

    if hits["iap_storekit"] and not storekit_files:
        findings.append(Finding("P2_MEDIUM", "IAP testing", "StoreKit/IAP code found but no .storekit configuration file found", str(hits["iap_storekit"][:8]), "Consider adding a StoreKit configuration file for local testing and keep IAP product matrix ready for App Review."))

    if hits["ugc_hints"]:
        # UGC hints are noisy, so mark as human confirmation unless report/block evidence is weak.
        report_block = grep(text_files, [r"report", r"block user", r"blocked", r"moderation", r"offensive"])
        if len(report_block) < 2:
            findings.append(Finding("P1_HIGH", "UGC/content safety", "Possible UGC/social features found but limited moderation evidence", str(hits["ugc_hints"][:8]), "If users can post/upload/message, verify filtering, report, block, support contact, and moderation response plan."))

    if hits["sensitive_data_hints"]:
        findings.append(Finding("P1_HIGH", "Sensitive data/domain", "Sensitive data or regulated-domain hints found", str(hits["sensitive_data_hints"][:10]), "Verify privacy labels, consent, security model, retention, export/deletion controls, and category-specific legal/review evidence where applicable."))

    if hits["ai_hints"] and hits["sensitive_data_hints"]:
        findings.append(Finding("P1_HIGH", "AI + sensitive data", "AI and sensitive-data/domain hints found together", f"ai={hits['ai_hints'][:8]} sensitive={hits['sensitive_data_hints'][:8]}", "Disclose whether personal or sensitive data is sent to third-party AI providers and get user consent where required."))

    if not hits["privacy_policy"]:
        findings.append(Finding("P1_HIGH", "Privacy policy", "No obvious privacy policy string/URL found", "Keyword search found no privacy policy evidence", "Ensure privacy policy URL is in App Store Connect and accessible in the app."))

    if not hits["support_url"]:
        findings.append(Finding("P2_MEDIUM", "Support", "No obvious support/contact evidence found", "Keyword search found no support/contact evidence", "Ensure app and Support URL provide easy contact info."))

    if not hits["accessibility"]:
        findings.append(Finding("P2_MEDIUM", "Accessibility", "No explicit accessibility labels or audit references found", "Keyword search found no accessibility evidence", "Run VoiceOver, Dynamic Type, contrast, and tap-target audit; add labels where needed."))

    evidence["sdk_inventory"] = collect_sdk_inventory(repo, files)

    # Build report
    generated = datetime.now().isoformat(timespec="seconds")
    report_lines = []
    report_lines.append("# App Store Static Scan Report")
    report_lines.append("")
    report_lines.append(f"Generated: {generated}")
    report_lines.append(f"Repository: `{repo}`")
    report_lines.append("")
    report_lines.append("> This is a static heuristic scan. It does not guarantee App Store approval. Use it as input for a full App Store Submission Auditor review.")
    report_lines.append("")
    by_sev = {s: [f for f in findings if f.severity == s] for s in ["P0_BLOCKER", "P1_HIGH", "P2_MEDIUM", "P3_NICE_TO_HAVE"]}
    report_lines.append("## Summary")
    for sev, arr in by_sev.items():
        report_lines.append(f"- {sev}: {len(arr)}")
    report_lines.append("")
    for sev in ["P0_BLOCKER", "P1_HIGH", "P2_MEDIUM", "P3_NICE_TO_HAVE"]:
        arr = by_sev[sev]
        report_lines.append(f"## {sev}")
        if not arr:
            report_lines.append("No findings from static scan.")
        else:
            for i, f in enumerate(arr, 1):
                report_lines.append(f"### {i}. {f.title}")
                report_lines.append(f"- Category: {f.category}")
                report_lines.append(f"- Evidence: `{f.evidence}`")
                report_lines.append(f"- Recommendation: {f.recommendation}")
                report_lines.append("")
        report_lines.append("")

    report_lines.append("## Evidence Collected")
    report_lines.append("```json")
    report_lines.append(json.dumps(evidence, indent=2, ensure_ascii=False)[:60000])
    report_lines.append("```")

    md_path = out / "app-store-static-scan.md"
    json_path = out / "app-store-static-scan.json"
    md_path.write_text("\n".join(report_lines), encoding="utf-8")
    json_path.write_text(json.dumps({"generated": generated, "repo": str(repo), "findings": [asdict(f) for f in findings], "evidence": evidence}, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {md_path}")
    print(f"Wrote {json_path}")
    print(f"Findings: P0={len(by_sev['P0_BLOCKER'])}, P1={len(by_sev['P1_HIGH'])}, P2={len(by_sev['P2_MEDIUM'])}, P3={len(by_sev['P3_NICE_TO_HAVE'])}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
