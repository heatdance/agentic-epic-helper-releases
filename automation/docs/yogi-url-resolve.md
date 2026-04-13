# Yogi requirement URL resolve + lightweight snippet

Corner **Yogi** links map a requirement id (e.g. `CRT-1741`) to a Confluence **page** plus a browser anchor `#req-CRT-1741`. In **storage HTML**, the tag is usually an `ac:structured-macro` with `ac:name="requirement"` and `ac:parameter ac:name="key">CRT-…</ac:parameter>`.

## Tools (stdlib Python 3)

| Script | Role |
|--------|------|
| [automation/tools/yogi-tool/yogi_resolve.py](../tools/yogi-tool/yogi_resolve.py) | Normalize URL / `page_id` / `anchor`; optional `--follow` + cookie; optional `--snippet` (REST + extract). |
| [automation/tools/yogi-tool/yogi_snippet.py](../tools/yogi-tool/yogi_snippet.py) | Given `page_id` + `--req`, fetch **body.storage** only and print **small JSON** with `snippet_text`. |
| [automation/tools/yogi-tool/yogi_extract.py](../tools/yogi-tool/yogi_extract.py) | Pure extract from storage HTML (used by `yogi_snippet` / tests). Picks among **all** `requirement` macros with the same key (e.g. **LINK** in a table vs **DEFINITION** under `</h2><p>…</p>`). |
| [automation/tools/yogi-tool/yogi_confluence.py](../tools/yogi-tool/yogi_confluence.py) | REST `GET /rest/api/content/{id}?expand=body.storage`. |

### `yogi_resolve.py`

| Input | Example |
|-------|--------|
| Bare key + space | `CRT-1741 --space CT` |
| Short URL | `https://confluence.in.devexperts.com/requirements/CT/CRT-1741` |
| Page URL + anchor | `.../spaces/CT/pages/345721535/Title#req-CRT-1741` |
| `viewpage.action` + anchor | `.../pages/viewpage.action?pageId=...#req-...` (use `--space` if needed) |

Flags: `--follow`, `--cookie` / `CONFLUENCE_SESSION_COOKIE`, `CONFLUENCE_BASE_URL`, **`--snippet`** (needs `page_id` + cookie).

**One-shot resolve + snippet:** short `/requirements/…` URL usually needs **`--follow --cookie`** so `page_id` is filled, then storage is fetched and extracted:

```bash
python automation/tools/yogi-tool/yogi_resolve.py "https://confluence.in.devexperts.com/requirements/CT/CRT-1741" --follow --cookie "$CONFLUENCE_SESSION_COOKIE" --snippet
```

Exit codes with **`--snippet`**: **0** = OK; **1** = REST/network or other fetch error; **3** = storage fetched but requirement text missing (`key_not_found` / `macro_end_not_found` or empty snippet)—aligned with `yogi_snippet.py`.

### `yogi_snippet.py` (token-friendly)

Fetches **storage** via REST (not rendered markdown) and extracts **one** requirement row’s text.

```bash
python automation/tools/yogi-tool/yogi_snippet.py --page-id 345703196 --req CRT-1730 --cookie "JSESSIONID=..."
```

Offline / CI (no Confluence): save MCP `confluence_get_page` JSON and run:

```bash
python automation/tools/yogi-tool/yogi_snippet.py --storage-file ./export.json --req CRT-1730 --compare
```

**`--storage-file` JSON shapes** (first match wins): top-level string (raw storage HTML); `content.value`; `body.storage.value` (REST); **`metadata.content.value`** (typical MCP page object). No manual wrapper needed. In Python, `yogi_snippet.load_storage_from_export(dict)` performs the same unwrapping.

### Extractor behavior (duplicate keys)

On a single page, the same requirement **key** may appear in more than one `requirement` macro (e.g. a **LINK** row in a table and a **DEFINITION** block in a heading). The extractor scores candidates by macro **type** (prefers **DEFINITION** over **LINK**) and by **snippet length** (very short fragments are deprioritized). It can return prose from **`</ac:structured-macro></h2><p>…</p>`** (`mode`: `definition_h2_p`) as well as the existing table-cell modes (`inline_td`, `after_th_td`).

JSON output includes **`candidates_considered`** (how many distinct requirement macros matched the key) and **`selected_reason`** (e.g. `best_of_n_macros`, `single_candidate`).

### Agents in Cursor (context hygiene)

1. Use **`yogi_resolve`** to get `page_id` + `requirement_key` (from URL or Epic).
2. Prefer **`yogi_snippet`** (or MCP that returns **only** `snippet_text`) for the model — **do not** paste full `confluence_get_page` markdown/HTML into chat for every tag.
3. If no cookie in the agent environment, resolve locally; use **MCP once** server-side or ask the human to run `yogi_snippet` / paste **only** the JSON `snippet_text`.

## Size comparison (measured on real CT pages, 2026-04-10)

**Portfolio Metrics** (`pageId=345703196`), requirement **CRT-1730**:

| Delivery | Approx. size | Notes |
|----------|----------------|-------|
| **Snippet** (`yogi_snippet` / extract) | **80** characters | Only the requirement prose for agents. |
| MCP **`confluence_get_page`** → markdown | **~52,700** characters | Whole page; too heavy per Yogi tag. |
| REST **`body.storage`** HTML | **~183,000** characters | Whole page XML/macros; use only inside the script, not in LLM context. |

**Functional Configuration** (`pageId=345721535`), requirement **CRT-1741** (macro in `<th>`, body in next `<td>`):

| Delivery | Approx. size |
|----------|----------------|
| **Snippet** | **~285** characters |
| REST **body.storage** HTML | **~206,000** characters |

**Takeaway:** Snippet is **~0.04–0.14%** of raw storage for these rows — keep epic analysis on **snippets**, not full pages.

## Tests

From `automation/tools/yogi-tool/`:

```bash
python test_yogi_extract.py
```

Uses [fixtures/sample_inline_req.json](../tools/yogi-tool/fixtures/sample_inline_req.json), [fixtures/sample_adjacent_req.json](../tools/yogi-tool/fixtures/sample_adjacent_req.json), and [fixtures/sample_duplicate_key_req.json](../tools/yogi-tool/fixtures/sample_duplicate_key_req.json) (LINK + DEFINITION with the same key).

## Pipelines

1. `yogi_resolve` → `page_id`, `requirement_key`.
2. `yogi_snippet` with service account cookie → store `snippet_text` in `epics/<EPIC-KEY>/<EPIC-KEY>-ref.json` (see [epics/README.md](../../epics/README.md)).
3. Agents consume **only** stored snippets for bulk Epic analysis.
