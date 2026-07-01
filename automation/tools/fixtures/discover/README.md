# Discover fixtures

| Fixture | Mode | Purpose |
|---------|------|---------|
| `discover-594-linker-pass.json` | **`linker`** | Production linker pass (draft_truth_v2) |
| `discover-594-linker-bad.json` | **`linker`** | Must exit 1 (wrong discovery_mode) |
| `discover-*-minimal.json` | **`generation --allow-incomplete`** | Legacy probe fixtures — scheduled for removal |

Use frozen coverage with `coverage_frozen_at` for linker tests (`automation/temp/coverage-594-frozen-shell.json`).
