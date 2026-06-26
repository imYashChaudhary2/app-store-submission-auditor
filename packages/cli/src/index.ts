#!/usr/bin/env node

import { existsSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const args = process.argv.slice(2);

function help() {
  console.log(`
App Store Submission Auditor

Usage:
  appssa scan <path>
  app-store-submission-auditor scan <path>

Example:
  appssa scan .
`);
}

function walk(dir: string, files: string[] = []) {
  for (const item of readdirSync(dir)) {
    if ([".git", "node_modules", "DerivedData", "build", "dist"].includes(item)) continue;

    const full = join(dir, item);
    const stat = statSync(full);

    if (stat.isDirectory()) walk(full, files);
    else files.push(full);
  }

  return files;
}

if (args.length === 0 || args.includes("--help")) {
  help();
  process.exit(0);
}

const command = args[0];
const target = args[1] ?? ".";

if (command !== "scan") {
  console.error(`Unknown command: ${command}`);
  help();
  process.exit(1);
}

if (!existsSync(target)) {
  console.error(`Path does not exist: ${target}`);
  process.exit(1);
}

const files = walk(target);

const hasXcodeProject = files.some((file) => file.includes(".xcodeproj"));
const hasInfoPlist = files.some((file) => file.endsWith("Info.plist"));
const hasPrivacyManifest = files.some((file) => file.endsWith("PrivacyInfo.xcprivacy"));

console.log("# App Store Submission Audit");
console.log("");
console.log(`Scanned path: \`${target}\``);
console.log("");

if (!hasXcodeProject) {
  console.log("## P2: No Xcode project detected");
  console.log("Run this from the root of an Apple platform app repo if this is unexpected.");
  console.log("");
}

if (!hasInfoPlist) {
  console.log("## P1: Info.plist not detected");
  console.log("Confirm the app target has a valid Info.plist and permission purpose strings.");
  console.log("");
}

if (!hasPrivacyManifest) {
  console.log("## P1: PrivacyInfo.xcprivacy not detected");
  console.log("Add or verify a privacy manifest, especially if the app or SDKs use privacy-sensitive APIs.");
  console.log("");
}

if (hasXcodeProject && hasInfoPlist && hasPrivacyManifest) {
  console.log("No obvious basic App Store submission risks detected.");
}

console.log("---");
console.log("This scanner is heuristic and does not replace Apple App Review or legal review.");
