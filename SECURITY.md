# Security Policy

This repository contains an agent skill and a read-only static scanner.

## Supported use

The default behavior is read-only auditing. Agents using this skill should not modify app code, project settings, provisioning, App Store Connect metadata, or legal documents unless the user explicitly approves fixes.

## Reporting a vulnerability

If you find a security issue in the scanner or instructions, open a GitHub issue with:

- affected file;
- risk description;
- reproduction steps;
- suggested fix if available.

Do not include private app source code, credentials, App Store Connect tokens, certificates, provisioning profiles, API keys, or personal user data in public issues.

## Sensitive data

Do not commit:

- App Store Connect API keys;
- signing certificates;
- provisioning profiles;
- demo account passwords;
- production API keys;
- private privacy/data maps containing real user data;
- unreleased screenshots or confidential review notes unless intended to be public.

## Agent safety

When installing third-party skills or agent instructions, review the files before execution. This skill includes scripts, so run them only from a trusted checkout.
