#!/usr/bin/env python3
"""Helpers for /release-notes v3 — parse batches, build JQL, format markdown."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "docs" / "release-notes-contract.json"
RELEASES = REPO_ROOT / "releases"

_JIRA_HOST_CACHE: str | None = None
_SECTION_ORDER = ["CR/s", "DR/s", "Improvement/s", "Task/s", "Other/s"]


def load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def jira_host() -> str:
    global _JIRA_HOST_CACHE
    if _JIRA_HOST_CACHE is None:
        _JIRA_HOST_CACHE = load_contract().get("jira_host", "https://jira.in.devexperts.com").rstrip("/")
    return _JIRA_HOST_CACHE


def issue_wiki_link(key: str) -> str:
    c = load_contract()
    link_cfg = c["markdown"]["issue_link"]
    host = jira_host()
    url = f"{host}{link_cfg['browse_path'].format(key=key)}"
    return link_cfg["wiki_template"].format(key=key, url=url)


def expand_version_token(token: str) -> tuple[str, list[str]]:
    token = token.strip()
    m = re.match(r"^(\d+)\.(\d+)-(\d+)$", token)
    if m:
        major, minor, end_patch = m.group(1), int(m.group(2)), int(m.group(3))
        versions = [f"{major}.{p}" for p in range(minor, end_patch + 1)]
        return token, versions
    m = re.match(r"^(\d+)-(\d+)$", token)
    if m:
        start, end = int(m.group(1)), int(m.group(2))
        return token, [str(v) for v in range(start, end + 1)]
    if re.match(r"^\d+(\.\d+)?$", token):
        return token, [token]
    raise ValueError(f"Unrecognized version token: {token!r}")


def parse_batches_arg(arg: str) -> list[dict]:
    sep = load_contract()["version_parse"]["batch_separator"]
    batches = []
    for part in arg.split(sep):
        part = part.strip()
        if not part:
            continue
        batch_token, versions = expand_version_token(part)
        batches.append({"batch_token": batch_token, "versions": versions})
    return batches


def _jql_list(values: list[str]) -> str:
    """Comma-separated JQL list; quote values that need it (spaces, apostrophes)."""
    parts = []
    for v in values:
        if re.search(r"[\s']", v):
            parts.append(f'"{v}"')
        else:
            parts.append(v)
    return ", ".join(parts)


def _scope_format_vars() -> dict[str, str]:
    s = load_contract()["corner_scope"]
    return {
        "project_xt": s["project_xt"],
        "pmoproc_master": ", ".join(s["pmoproc_master"]),
        "pmoproc_fx_spot": ", ".join(s["pmoproc_fx_spot"]),
        "epic_fx_spot_exclude": _jql_list(s["epic_fx_spot_exclude"]),
        "epic_master_include": _jql_list(s["epic_master_include"]),
        "status_exclude_fx_base": _jql_list(s["status_exclude_fx_base"]),
        "status_exclude_master_base": _jql_list(s["status_exclude_master_base"]),
        "status_exclude_adaptive": _jql_list(s["status_exclude_adaptive"]),
    }


def build_jql(query_id: str, version: str | None = None, adaptive_token: str | None = None) -> str:
    c = load_contract()
    tmpl = c["jql"]["templates"][query_id]
    vars_ = _scope_format_vars()
    vars_["order_by"] = c["jql"].get("order_by", "")
    if query_id.endswith("_adaptive"):
        if not adaptive_token:
            raise ValueError(f"query {query_id} requires adaptive_token")
        prefix = c["adaptive"]["fixversion_prefix"]
        token = adaptive_token.removeprefix(prefix) if adaptive_token.startswith(prefix) else adaptive_token
        vars_["adaptive_fixversion"] = f"{prefix}{token}"
    else:
        if not version:
            raise ValueError(f"query {query_id} requires version")
        vars_["version"] = version
    return tmpl.format(**vars_).strip()


def pull_adaptive_token(summary: str) -> str | None:
    c = load_contract()
    rx = c["adaptive"]["token_from_summary_regex"]
    m = re.search(rx, summary or "", re.I)
    if m:
        return m.group(1).strip()
    prefix = c["adaptive"]["fixversion_prefix"]
    m2 = re.search(rf"{re.escape(prefix)}(\S+)", summary or "", re.I)
    return m2.group(1) if m2 else None


def adaptive_fixversion(token: str) -> str:
    prefix = load_contract()["adaptive"]["fixversion_prefix"]
    if token.startswith(prefix):
        return token
    return f"{prefix}{token}"


def is_adaptive_trigger(issue: dict) -> bool:
    c = load_contract()
    summary = (issue.get("summary") or "").lower()
    if c["adaptive"]["trigger_summary_contains"].lower() in summary:
        return True
    if c["adaptive"].get("trigger_task_fallback") and issue.get("issuetype") == "Task":
        return "adaptive" in summary
    return False


def section_for_issuetype(name: str) -> str:
    mapping = load_contract()["issuetype_sections"]
    return mapping.get(name) or mapping["_default"]


def trigger_section_for_adaptive(issuetype: str) -> str:
    return section_for_issuetype(issuetype or "Task")


def child_type_label(issuetype: str) -> str:
    if issuetype == "Change Request":
        return "CR"
    if issuetype == "Defect Report":
        return "DR"
    if issuetype == "Improvement":
        return "Improvement"
    return issuetype or "Other"


def normalize_jira_issue(raw: dict) -> dict:
    it = raw.get("issue_type") or raw.get("issuetype") or {}
    it_name = it.get("name", "") if isinstance(it, dict) else str(it)
    return {
        "key": raw.get("key", ""),
        "summary": raw.get("summary", ""),
        "issuetype": it_name,
    }


def _version_sort_key(v: str) -> tuple:
    parts = []
    for p in re.split(r"[.]", v):
        parts.append(int(p) if p.isdigit() else p)
    return tuple(parts)


def format_markdown_document(
    versions_data: dict[str, dict[str, list]],
    adaptive_blocks: dict[str, list[dict]] | None = None,
    omit_empty_versions: bool = True,
) -> str:
    c = load_contract()
    md = c["markdown"]
    lines: list[str] = []
    adaptive_blocks = adaptive_blocks or {}

    all_versions = sorted(
        set(versions_data.keys()) | set(adaptive_blocks.keys()),
        key=_version_sort_key,
    )
    for version in all_versions:
        sections = versions_data.get(version) or {}
        adapt_for_ver = adaptive_blocks.get(version) or []
        has_content = adapt_for_ver or any(sections.get(s) for s in _SECTION_ORDER)
        if omit_empty_versions and not has_content:
            continue
        lines.append(md["version_heading"].format(version=version))
        lines.append("")

        adaptive_by_section: dict[str, list] = {}
        for block in adapt_for_ver:
            sec = block.get("section") or "Task/s"
            adaptive_by_section.setdefault(sec, []).append(block)

        for sec in _SECTION_ORDER:
            items = sections.get(sec) or []
            blocks = adaptive_by_section.get(sec) or []
            if not items and not blocks:
                continue
            lines.append(md["section_wrapper"].format(section=sec))
            for block in blocks:
                header_link = issue_wiki_link(block["key"])
                lines.append(
                    md["adaptive_header"].format(issue_link=header_link, summary=block["summary"])
                )
                for child in block.get("children") or []:
                    if not child.get("key"):
                        raise ValueError(
                            f"adaptive child missing key under {block['key']}: {child!r}"
                        )
                    lines.append(
                        md["adaptive_child"].format(
                            type_label=child["type_label"],
                            child_issue_link=issue_wiki_link(child["key"]),
                            summary=child["summary"],
                        )
                    )
            adapt_keys = {b["key"] for b in blocks}
            for item in items:
                if item.get("key") in adapt_keys:
                    continue
                lines.append(
                    md["line_format"].format(
                        issue_link=issue_wiki_link(item["key"]),
                        summary=item["summary"],
                    )
                )
            lines.append("")
    return "\n".join(lines).rstrip() + "\n" if lines else ""


def write_batch_file(batch_token: str, lane: str, content: str) -> Path | None:
    if not content.strip():
        return None
    c = load_contract()
    suffix = c["output"]["fx_suffix" if lane == "fx" else "non_fx_suffix"]
    out_dir = RELEASES / batch_token
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{batch_token}{suffix}"
    path.write_text(content, encoding="utf-8")
    return path


def _add_issues_to_sections(
    pool: dict[str, dict[str, list]],
    version: str,
    issues: list[dict],
    exclude_keys: set[str],
) -> None:
    for raw in issues:
        issue = normalize_jira_issue(raw)
        if issue["key"] in exclude_keys:
            continue
        sec = section_for_issuetype(issue["issuetype"])
        pool.setdefault(version, {}).setdefault(sec, []).append(
            {"key": issue["key"], "summary": issue["summary"]}
        )


def _can_to_children(can_issues: list[dict]) -> list[dict]:
    return [
        {
            "key": normalize_jira_issue(i)["key"],
            "type_label": child_type_label(normalize_jira_issue(i)["issuetype"]),
            "summary": normalize_jira_issue(i)["summary"],
        }
        for i in can_issues
    ]


def merge_version_data(
    master_versions: dict[str, dict[str, list]],
    fx_versions: dict[str, dict[str, list]],
    master_adaptive: dict[str, list[dict]],
    fx_adaptive: dict[str, list[dict]],
    version: str,
    *,
    master_base: list[dict],
    fx_base: list[dict],
    master_adapt_can: list[dict],
    fx_adapt_can: list[dict],
) -> None:
    trigger_keys: set[str] = set()
    for raw in master_base:
        issue = normalize_jira_issue(raw)
        if is_adaptive_trigger(issue):
            trigger_keys.add(issue["key"])

    _add_issues_to_sections(master_versions, version, master_base, trigger_keys)
    _add_issues_to_sections(fx_versions, version, fx_base, set())

    for raw in master_base:
        issue = normalize_jira_issue(raw)
        if not is_adaptive_trigger(issue):
            continue
        token = pull_adaptive_token(issue["summary"])
        if not token:
            continue
        base_block = {
            "key": issue["key"],
            "summary": issue["summary"],
            "section": trigger_section_for_adaptive(issue["issuetype"]),
        }
        m_children = _can_to_children(master_adapt_can)
        if m_children:
            master_adaptive.setdefault(version, []).append({**base_block, "children": m_children})
        f_children = _can_to_children(fx_adapt_can)
        if f_children:
            fx_adaptive.setdefault(version, []).append({**base_block, "children": f_children})


def assemble_batch_markdown(batch: dict, version_payloads: list[dict]) -> tuple[str, str]:
    """version_payloads: [{version, master_base[], fx_base[], master_adaptive[], fx_adaptive[]}]"""
    master_v: dict[str, dict[str, list]] = {}
    fx_v: dict[str, dict[str, list]] = {}
    master_a: dict[str, list[dict]] = {}
    fx_a: dict[str, list[dict]] = {}

    for vp in version_payloads:
        merge_version_data(
            master_v,
            fx_v,
            master_a,
            fx_a,
            vp["version"],
            master_base=vp.get("master_base") or [],
            fx_base=vp.get("fx_base") or [],
            master_adapt_can=vp.get("master_adaptive") or [],
            fx_adapt_can=vp.get("fx_adaptive") or [],
        )

    master_md = format_markdown_document(master_v, master_a)
    fx_md = format_markdown_document(fx_v, fx_a)
    return master_md, fx_md


def cmd_parse_batches(args: argparse.Namespace) -> None:
    print(json.dumps({"batches": parse_batches_arg(args.releases)}, indent=2))


def cmd_build_jql(args: argparse.Namespace) -> None:
    jql = build_jql(args.query, version=args.version, adaptive_token=args.adaptive_token)
    print(jql)


def cmd_format_markdown(args: argparse.Namespace) -> None:
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    doc = format_markdown_document(
        data.get("versions_data") or {},
        data.get("adaptive_blocks"),
    )
    if args.output:
        Path(args.output).write_text(doc, encoding="utf-8")
        print(args.output)
    else:
        print(doc)


def cmd_write_batch(args: argparse.Namespace) -> None:
    content = Path(args.content).read_text(encoding="utf-8")
    path = write_batch_file(args.batch_token, args.lane, content)
    print(path if path else "SKIP empty")


def cmd_assemble_from_raw(args: argparse.Namespace) -> None:
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    batch = data.get("batch") or {"batch_token": args.batch_token, "versions": []}
    payloads = data.get("version_payloads") or []
    master_md, fx_md = assemble_batch_markdown(batch, payloads)
    out = {
        "batch_token": batch.get("batch_token"),
        "master_markdown": master_md,
        "fx_markdown": fx_md,
    }
    if args.output:
        Path(args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"master_len": len(master_md), "fx_len": len(fx_md)}, indent=2))


def cmd_list_queries(args: argparse.Namespace) -> None:
    c = load_contract()
    print(json.dumps(c["jql"]["query_ids"], indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description="Release notes helpers (v3)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pb = sub.add_parser("parse-batches")
    pb.add_argument("releases")
    pb.set_defaults(func=cmd_parse_batches)

    bj = sub.add_parser("build-jql")
    bj.add_argument(
        "--query",
        required=True,
        choices=["fx_spot_base", "master_base", "fx_spot_adaptive", "master_adaptive"],
    )
    bj.add_argument("--version", default=None)
    bj.add_argument("--adaptive-token", default=None)
    bj.set_defaults(func=cmd_build_jql)

    lq = sub.add_parser("list-queries")
    lq.set_defaults(func=cmd_list_queries)

    fm = sub.add_parser("format-markdown")
    fm.add_argument("--input", required=True)
    fm.add_argument("--output", default=None)
    fm.set_defaults(func=cmd_format_markdown)

    wb = sub.add_parser("write-batch")
    wb.add_argument("--batch-token", required=True)
    wb.add_argument("--lane", choices=["fx", "non_fx"], required=True)
    wb.add_argument("--content", required=True)
    wb.set_defaults(func=cmd_write_batch)

    ar = sub.add_parser("assemble-from-raw")
    ar.add_argument("--input", required=True)
    ar.add_argument("--batch-token", default=None)
    ar.add_argument("--output", default=None)
    ar.set_defaults(func=cmd_assemble_from_raw)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
