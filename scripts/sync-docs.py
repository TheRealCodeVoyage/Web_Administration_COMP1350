#!/usr/bin/env python3
"""
Sync publishable course material into the Jekyll site under docs/.

The Week-XX/ folders are the working source of truth. This script copies ONLY
the labs, online-activity (flipped) readings, and the group project spec into
docs/, adding the Jekyll front matter each page needs. Quizzes, exams, slides,
and internal planning documents are never touched by this script and are also
excluded by .gitignore.

Run from the repository root after editing any lab, online activity, or the
project spec:

    python3 scripts/sync-docs.py

Re-running is safe: generated pages are overwritten from source every time.
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"

# --- Explicit publish list -------------------------------------------------
# Nothing is published unless it appears here. Deliberately explicit rather
# than a glob, so adding a file to the website is always a visible change.

LABS = [
    ("Week-01/Lab1-VM-Setup.md",                  "Lab_01.md", "Lab 1: Development VM Setup with VirtualBox & Vagrant"),
    ("Week-02/Lab2-Apache-Nginx.md",              "Lab_02.md", "Lab 2: Apache & Nginx Side-by-Side"),
    ("Week-03/Lab3-IIS-Node-PM2.md",              "Lab_03.md", "Lab 3: IIS & Node.js/Express.js with PM2"),
    ("Week-04/Lab4-Deployment.md",                "Lab_04.md", "Lab 4: Deployment — GitHub Pages & Modern PaaS"),
    ("Week-05/Lab5-SSL-TLS.md",                   "Lab_05.md", "Lab 5: SSL/TLS — Self-Signed Certificates & Let's Encrypt"),
    ("Week-06/Lab6-Reverse-Proxy-TLS.md",         "Lab_06.md", "Lab 6: Reverse Proxy Terminating TLS"),
    ("Week-07/Lab7-OAuth.md",                     "Lab_07.md", "Lab 7: OAuth Login with Passport.js"),
    ("Week-09/Lab8-HAProxy-LoadBalancing.md",     "Lab_08.md", "Lab 8: Load Balancing with HAProxy"),
    ("Week-10/Lab9-SPOF-Redundancy.md",           "Lab_09.md", "Lab 9: Eliminating Single Points of Failure"),
    ("Week-11/Lab10-CDN-Cloudflare.md",           "Lab_10.md", "Lab 10: CDN — jsDelivr Latency Test & Cloudflare Setup"),
    ("Week-12/Lab11-Centralized-Logging.md",      "Lab_11.md", "Lab 11: Centralized Logging"),
]

ONLINE_ACTIVITIES = [
    ("Week-01/OA1-Web-Stack-Basics.md",           "OA_01.md", "Online Activity 1: Web Stack Basics"),
    ("Week-02/OA2-Apache-vs-Nginx.md",            "OA_02.md", "Online Activity 2: Apache vs. Nginx Recap"),
    ("Week-03/OA3-App-Servers-Recap.md",          "OA_03.md", "Online Activity 3: Application Servers Recap"),
    ("Week-04/OA4-Deployment-Models.md",          "OA_04.md", "Online Activity 4: Deployment Models Recap"),
    ("Week-05/OA5-SSL-TLS-Recap.md",              "OA_05.md", "Online Activity 5: SSL/TLS Recap"),
    ("Week-06/OA6-PKI-Proxy-Recap.md",            "OA_06.md", "Online Activity 6: PKI & Proxy Recap"),
    ("Week-07/OA7-Auth-Concepts-Recap.md",        "OA_07.md", "Online Activity 7: Authentication Concepts Recap"),
    ("Week-09/OA8-Load-Balancing-Recap.md",       "OA_08.md", "Online Activity 8: Load Balancing Recap"),
    ("Week-10/OA9-SPOF-HA-Recap.md",              "OA_09.md", "Online Activity 9: SPOF & High Availability Recap"),
    ("Week-11/OA10-CDN-Recap.md",                 "OA_10.md", "Online Activity 10: CDN Recap"),
    ("Week-12/OA11-Logging-Analytics-Recap.md",   "OA_11.md", "Online Activity 11: Logging & Analytics Recap"),
]

PROJECTS = [
    ("COMP1350_Group_Project.md",   "Group_Project.md", "Group Project: Deploy & Harden a Team Site"),
]

# Guard: refuse to publish anything that looks like assessment material, even
# if someone adds it to the lists above by mistake.
FORBIDDEN = ("quiz", "test", "exam", "answer", "solution", "midterm")


def escape_yaml(value: str) -> str:
    return value.replace('"', '\\"')


def build_page(source: Path, title: str, back_label: str) -> str:
    body = source.read_text(encoding="utf-8")

    # Course material contains shell, Nginx, and template syntax that can
    # include double braces. Jekyll's Liquid engine would try to evaluate that
    # and silently render it as an empty string — including inside fenced code
    # blocks. Wrapping the body in {% raw %} disables Liquid for the content
    # while leaving Markdown rendering untouched.
    return (
        "---\n"
        f'title: "{escape_yaml(title)}"\n'
        "---\n"
        "\n"
        f"[&larr; {back_label}]({{{{ '/' | relative_url }}}})\n"
        "\n"
        "{% raw %}\n"
        f"{body.rstrip()}\n"
        "{% endraw %}\n"
    )


def sync(entries, subdir: str, back_label: str) -> int:
    target_dir = DOCS / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for rel_source, out_name, title in entries:
        lowered = Path(rel_source).name.lower()
        if any(word in lowered for word in FORBIDDEN):
            sys.exit(f"REFUSING to publish assessment-like file: {rel_source}")

        source = REPO_ROOT / rel_source
        if not source.exists():
            sys.exit(f"Missing source file: {rel_source}")

        (target_dir / out_name).write_text(
            build_page(source, title, back_label), encoding="utf-8"
        )
        print(f"  {rel_source}  ->  docs/{subdir}/{out_name}")
        written += 1
    return written


def main() -> None:
    print("Syncing labs...")
    n_labs = sync(LABS, "labs", "Back to course index")
    print("Syncing online activities...")
    n_oa = sync(ONLINE_ACTIVITIES, "online-activities", "Back to course index")
    print("Syncing projects...")
    n_proj = sync(PROJECTS, "projects", "Back to course index")
    print(
        f"\nDone. {n_labs} labs, {n_oa} online activities, and {n_proj} project "
        f"page(s) written to docs/."
    )
    print("Slides, quizzes, exams, and planning documents were not touched.")


if __name__ == "__main__":
    main()
