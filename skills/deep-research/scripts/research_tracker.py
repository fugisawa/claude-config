#!/usr/bin/env python3
"""
Research Tracker - Organize findings, sources, and generate research reports.

Usage:
    python research_tracker.py init "Research Topic"
    python research_tracker.py add-source "URL" --title "Title" --type academic --credibility high
    python research_tracker.py add-finding "Finding text" --source-id 1 --confidence high --question "Q1"
    python research_tracker.py add-search "search query" --results 10 --notes "Found relevant papers"
    python research_tracker.py status
    python research_tracker.py export --format markdown
    python research_tracker.py export --format json
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
import sys

TRACKER_FILE = "research_tracker.json"

def init_tracker(topic: str) -> dict:
    """Initialize a new research tracker."""
    return {
        "topic": topic,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "questions": [],
        "searches": [],
        "sources": [],
        "findings": [],
        "contradictions": [],
        "gaps": []
    }

def load_tracker() -> dict:
    """Load existing tracker or return None."""
    path = Path(TRACKER_FILE)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None

def save_tracker(data: dict):
    """Save tracker to file."""
    data["updated"] = datetime.now().isoformat()
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def cmd_init(args):
    """Initialize new research project."""
    tracker = init_tracker(args.topic)
    save_tracker(tracker)
    print(f"✓ Initialized research tracker for: {args.topic}")
    print(f"  Saved to: {TRACKER_FILE}")

def cmd_add_question(args):
    """Add a research question."""
    tracker = load_tracker()
    if not tracker:
        print("Error: No tracker found. Run 'init' first.")
        sys.exit(1)
    
    question = {
        "id": f"Q{len(tracker['questions']) + 1}",
        "text": args.question,
        "added": datetime.now().isoformat(),
        "status": "open"
    }
    tracker["questions"].append(question)
    save_tracker(tracker)
    print(f"✓ Added question {question['id']}: {args.question}")

def cmd_add_source(args):
    """Add a source to the tracker."""
    tracker = load_tracker()
    if not tracker:
        print("Error: No tracker found. Run 'init' first.")
        sys.exit(1)
    
    source = {
        "id": len(tracker["sources"]) + 1,
        "url": args.url,
        "title": args.title or "Untitled",
        "type": args.type or "unknown",
        "credibility": args.credibility or "unassessed",
        "added": datetime.now().isoformat(),
        "notes": args.notes or "",
        "accessed": datetime.now().strftime("%Y-%m-%d")
    }
    tracker["sources"].append(source)
    save_tracker(tracker)
    print(f"✓ Added source #{source['id']}: {source['title']}")

def cmd_add_finding(args):
    """Add a finding to the tracker."""
    tracker = load_tracker()
    if not tracker:
        print("Error: No tracker found. Run 'init' first.")
        sys.exit(1)
    
    finding = {
        "id": len(tracker["findings"]) + 1,
        "text": args.finding,
        "source_ids": [int(x) for x in args.sources.split(",")] if args.sources else [],
        "confidence": args.confidence or "medium",
        "question_id": args.question or None,
        "added": datetime.now().isoformat(),
        "notes": args.notes or ""
    }
    tracker["findings"].append(finding)
    save_tracker(tracker)
    print(f"✓ Added finding #{finding['id']} (confidence: {finding['confidence']})")

def cmd_add_search(args):
    """Log a search query."""
    tracker = load_tracker()
    if not tracker:
        print("Error: No tracker found. Run 'init' first.")
        sys.exit(1)
    
    search = {
        "id": len(tracker["searches"]) + 1,
        "query": args.query,
        "timestamp": datetime.now().isoformat(),
        "results_count": args.results or 0,
        "notes": args.notes or "",
        "useful_sources": args.useful or []
    }
    tracker["searches"].append(search)
    save_tracker(tracker)
    print(f"✓ Logged search #{search['id']}: {args.query}")

def cmd_add_contradiction(args):
    """Add a noted contradiction."""
    tracker = load_tracker()
    if not tracker:
        print("Error: No tracker found. Run 'init' first.")
        sys.exit(1)
    
    contradiction = {
        "id": len(tracker["contradictions"]) + 1,
        "topic": args.topic,
        "position_a": {"source_id": args.source_a, "position": args.position_a},
        "position_b": {"source_id": args.source_b, "position": args.position_b},
        "resolution": args.resolution or "unresolved",
        "added": datetime.now().isoformat()
    }
    tracker["contradictions"].append(contradiction)
    save_tracker(tracker)
    print(f"✓ Added contradiction #{contradiction['id']}")

def cmd_add_gap(args):
    """Add an identified gap."""
    tracker = load_tracker()
    if not tracker:
        print("Error: No tracker found. Run 'init' first.")
        sys.exit(1)
    
    gap = {
        "id": len(tracker["gaps"]) + 1,
        "description": args.description,
        "type": args.type or "information",
        "significance": args.significance or "medium",
        "added": datetime.now().isoformat()
    }
    tracker["gaps"].append(gap)
    save_tracker(tracker)
    print(f"✓ Added gap #{gap['id']}")

def cmd_status(args):
    """Show research status."""
    tracker = load_tracker()
    if not tracker:
        print("Error: No tracker found. Run 'init' first.")
        sys.exit(1)
    
    print(f"\n📋 Research: {tracker['topic']}")
    print(f"   Started: {tracker['created'][:10]}")
    print(f"   Updated: {tracker['updated'][:10]}")
    print(f"\n📊 Statistics:")
    print(f"   Questions: {len(tracker['questions'])}")
    print(f"   Searches: {len(tracker['searches'])}")
    print(f"   Sources: {len(tracker['sources'])}")
    print(f"   Findings: {len(tracker['findings'])}")
    print(f"   Contradictions: {len(tracker['contradictions'])}")
    print(f"   Gaps: {len(tracker['gaps'])}")
    
    # Confidence breakdown
    if tracker["findings"]:
        conf_counts = {}
        for f in tracker["findings"]:
            conf = f.get("confidence", "unassessed")
            conf_counts[conf] = conf_counts.get(conf, 0) + 1
        print(f"\n🎯 Confidence Levels:")
        for conf, count in sorted(conf_counts.items()):
            print(f"   {conf}: {count}")
    
    # Source type breakdown
    if tracker["sources"]:
        type_counts = {}
        for s in tracker["sources"]:
            t = s.get("type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        print(f"\n📚 Source Types:")
        for t, count in sorted(type_counts.items()):
            print(f"   {t}: {count}")

def cmd_export(args):
    """Export research in specified format."""
    tracker = load_tracker()
    if not tracker:
        print("Error: No tracker found. Run 'init' first.")
        sys.exit(1)
    
    if args.format == "json":
        output = json.dumps(tracker, indent=2)
        filename = f"research_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    else:  # markdown
        output = generate_markdown_report(tracker)
        filename = f"research_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(filename, "w") as f:
        f.write(output)
    print(f"✓ Exported to: {filename}")

def generate_markdown_report(tracker: dict) -> str:
    """Generate a markdown report from tracker data."""
    lines = []
    lines.append(f"# Research Report: {tracker['topic']}\n")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    
    # Questions
    if tracker["questions"]:
        lines.append("## Research Questions\n")
        for q in tracker["questions"]:
            status = "✓" if q.get("status") == "answered" else "○"
            lines.append(f"- [{status}] {q['id']}: {q['text']}")
        lines.append("")
    
    # Key Findings
    if tracker["findings"]:
        lines.append("## Key Findings\n")
        for f in tracker["findings"]:
            conf_emoji = {"high": "🟢", "medium": "🟡", "low": "🟠"}.get(f["confidence"], "⚪")
            lines.append(f"### Finding #{f['id']} {conf_emoji}\n")
            lines.append(f"{f['text']}\n")
            lines.append(f"**Confidence:** {f['confidence']}")
            if f["source_ids"]:
                source_refs = [f"#{sid}" for sid in f["source_ids"]]
                lines.append(f"**Sources:** {', '.join(source_refs)}")
            if f.get("question_id"):
                lines.append(f"**Addresses:** {f['question_id']}")
            lines.append("")
    
    # Contradictions
    if tracker["contradictions"]:
        lines.append("## Contradictions & Conflicts\n")
        for c in tracker["contradictions"]:
            lines.append(f"### {c['topic']}\n")
            lines.append(f"- **Position A** (Source #{c['position_a']['source_id']}): {c['position_a']['position']}")
            lines.append(f"- **Position B** (Source #{c['position_b']['source_id']}): {c['position_b']['position']}")
            lines.append(f"- **Resolution:** {c['resolution']}")
            lines.append("")
    
    # Gaps
    if tracker["gaps"]:
        lines.append("## Information Gaps\n")
        for g in tracker["gaps"]:
            lines.append(f"- **{g['type'].title()}** ({g['significance']}): {g['description']}")
        lines.append("")
    
    # Sources
    if tracker["sources"]:
        lines.append("## Sources\n")
        by_type = {}
        for s in tracker["sources"]:
            t = s.get("type", "other")
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(s)
        
        for source_type, sources in sorted(by_type.items()):
            lines.append(f"### {source_type.title()}\n")
            for s in sources:
                cred = s.get("credibility", "unassessed")
                lines.append(f"- **[{s['id']}]** {s['title']} ({cred})")
                lines.append(f"  - URL: {s['url']}")
                lines.append(f"  - Accessed: {s['accessed']}")
                if s.get("notes"):
                    lines.append(f"  - Notes: {s['notes']}")
            lines.append("")
    
    # Search Log
    if tracker["searches"]:
        lines.append("## Search Log\n")
        lines.append("| # | Query | Results | Notes |")
        lines.append("|---|-------|---------|-------|")
        for s in tracker["searches"]:
            notes = s.get("notes", "")[:50] + ("..." if len(s.get("notes", "")) > 50 else "")
            lines.append(f"| {s['id']} | {s['query']} | {s['results_count']} | {notes} |")
        lines.append("")
    
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Research Tracker")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # init
    p_init = subparsers.add_parser("init", help="Initialize new research")
    p_init.add_argument("topic", help="Research topic")
    
    # add-question
    p_q = subparsers.add_parser("add-question", help="Add research question")
    p_q.add_argument("question", help="Question text")
    
    # add-source
    p_src = subparsers.add_parser("add-source", help="Add source")
    p_src.add_argument("url", help="Source URL")
    p_src.add_argument("--title", help="Source title")
    p_src.add_argument("--type", choices=["academic", "news", "official", "expert", "primary", "other"])
    p_src.add_argument("--credibility", choices=["high", "medium", "low", "unassessed"])
    p_src.add_argument("--notes", help="Notes about source")
    
    # add-finding
    p_find = subparsers.add_parser("add-finding", help="Add finding")
    p_find.add_argument("finding", help="Finding text")
    p_find.add_argument("--sources", help="Comma-separated source IDs")
    p_find.add_argument("--confidence", choices=["high", "medium", "low", "uncertain"])
    p_find.add_argument("--question", help="Related question ID")
    p_find.add_argument("--notes", help="Additional notes")
    
    # add-search
    p_search = subparsers.add_parser("add-search", help="Log search")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--results", type=int, help="Number of results")
    p_search.add_argument("--notes", help="Notes about results")
    p_search.add_argument("--useful", nargs="*", help="Useful source IDs found")
    
    # add-contradiction
    p_contra = subparsers.add_parser("add-contradiction", help="Add contradiction")
    p_contra.add_argument("topic", help="Topic of contradiction")
    p_contra.add_argument("--source-a", type=int, required=True)
    p_contra.add_argument("--position-a", required=True)
    p_contra.add_argument("--source-b", type=int, required=True)
    p_contra.add_argument("--position-b", required=True)
    p_contra.add_argument("--resolution", help="How resolved")
    
    # add-gap
    p_gap = subparsers.add_parser("add-gap", help="Add information gap")
    p_gap.add_argument("description", help="Gap description")
    p_gap.add_argument("--type", choices=["data", "research", "source", "temporal", "geographic", "methodological"])
    p_gap.add_argument("--significance", choices=["high", "medium", "low"])
    
    # status
    subparsers.add_parser("status", help="Show research status")
    
    # export
    p_export = subparsers.add_parser("export", help="Export research")
    p_export.add_argument("--format", choices=["markdown", "json"], default="markdown")
    
    args = parser.parse_args()
    
    if args.command == "init":
        cmd_init(args)
    elif args.command == "add-question":
        cmd_add_question(args)
    elif args.command == "add-source":
        cmd_add_source(args)
    elif args.command == "add-finding":
        cmd_add_finding(args)
    elif args.command == "add-search":
        cmd_add_search(args)
    elif args.command == "add-contradiction":
        cmd_add_contradiction(args)
    elif args.command == "add-gap":
        cmd_add_gap(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "export":
        cmd_export(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
