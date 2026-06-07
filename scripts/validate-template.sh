#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

required_files=(
  "README.md"
  "START_HERE.md"
  "CLAUDE.md"
  "AGENTS.md"
  "index.md"
  "log.md"
  "VERSION"
  "LICENSE.md"
  "TEMPLATE_MANIFEST.md"
)

required_dirs=(
  "AI-Sessions/raw"
  "AI-Sessions/conversations"
  "AI-Sessions/wiki/sources"
  "AI-Sessions/wiki/concepts"
  "AI-Sessions/wiki/decisions"
  "AI-Sessions/wiki/errors"
  "AI-Sessions/wiki/projects"
  "AI-Sessions/wiki/design"
  "AI-Sessions/wiki/dev-tasks"
  "AI-Sessions/wiki/guidelines"
  "prompts"
  "scripts"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$ROOT/$file" ]]; then
    echo "Missing required file: $file" >&2
    exit 1
  fi
done

for dir in "${required_dirs[@]}"; do
  if [[ ! -d "$ROOT/$dir" ]]; then
    echo "Missing required directory: $dir" >&2
    exit 1
  fi
done

if find "$ROOT" -name ".DS_Store" -o -name "Thumbs.db" | grep -q .; then
  echo "Remove OS metadata files before distribution." >&2
  exit 1
fi

if grep -RInE "(sk-|api[_-]?key|password|token|secret)" "$ROOT" \
  --exclude-dir=.obsidian \
  --exclude="validate-template.sh" \
  --exclude=".gitignore" >/tmp/ai-agent-wiki-template-secrets.txt; then
  echo "Potential secret-like text found:" >&2
  cat /tmp/ai-agent-wiki-template-secrets.txt >&2
  exit 1
fi

echo "Template validation passed: $ROOT"
