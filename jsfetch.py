#!/usr/bin/env python3
"""JS Fetch - JavaScript URL security scanner - By MuZaN"""

import argparse
import re
import sys
import time
import os
import subprocess
from urllib.parse import urlparse


class bcolors:
    RED = '\033[91m'
    BLACK = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def gradient_text(text, color1="FF0000", color2="000000"):
    """Red -> Black gradient for beautiful appearance."""
    result = ""
    for i, char in enumerate(text):
        ratio = i / max(len(text) - 1, 1)
        r = int(int(color1[0:2], 16) + (int(color2[0:2], 16) - int(color1[0:2], 16)) * ratio)
        g = int(int(color1[2:4], 16) + (int(color2[2:4], 16) - int(color1[2:4], 16)) * ratio)
        b = int(int(color1[4:6], 16) + (int(color2[4:6], 16) - int(color1[4:6], 16)) * ratio)
        result += f"\033[38;2;{r};{g};{b}m{char}"
    result += bcolors.RESET
    return result


ASCII_ART = """▄▄▄██▀▀▀██████   █████▒▓█████▄▄▄█████▓ ▄████▄   ██░ ██
   ▒██ ▒██    ▒ ▓██   ▒ ▓█   ▀▓  ██▒ ▓▒▒██▀ ▀█  ▓██░ ██▒
   ░██ ░ ▓██▄   ▒████ ░ ▒███  ▒ ▓██░ ▒░▒▓█    ▄ ▒██▀▀██░
▓██▄██▓  ▒   ██▒░▓█▒  ░ ▒▓█  ▄░ ▓██▓ ░ ▒▓▓▄ ▄██▒░▓█ ░██
 ▓███▒ ▒██████▒▒░▒█░    ░▒████▒ ▒██▒ ░ ▒ ▓███▀ ░░▓█▒░██▓
 ▒▓▒▒░ ▒ ▒▓▒ ▒ ░ ▒ ░    ░░ ▒░ ░ ▒ ░░   ░ ░▒ ▒  ░ ▒ ░░▒░▒
 ▒ ░▒░ ░ ░▒  ░ ░ ░       ░ ░  ░   ░      ░  ▒    ▒ ░▒░ ░
 ░ ░ ░ ░  ░  ░   ░ ░       ░    ░      ░         ░  ░░ ░
 ░   ░       ░             ░  ░        ░ ░       ░  ░  ░
                                       ░"""


def ascii_art_animation():
    """Display embedded ASCII art with animation effect (Red Black Gradient)."""
    lines = ASCII_ART.strip().split("\n")
    for line in lines:
        print(gradient_text(line, "FF0000", "000000"))
        sys.stdout.flush()
        time.sleep(0.05)


def ensure_requirements():
    """Check requirements and install them automatically if missing."""
    print(f"{bcolors.RED}[*]{bcolors.RESET} Checking requirements...")
    
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception:
        pass
    missing = []
    try:
        import requests 
    except ImportError:
        missing.append("requests")

    if not missing:
        print(f"{bcolors.RED}[+]{bcolors.RESET} All requirements satisfied.\n")
        return

    print(f"{bcolors.RED}[!]{bcolors.RESET} Missing: {', '.join(missing)} - installing automatically...")
    for pkg in missing:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--break-system-packages", pkg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pkg],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                print(f"{bcolors.RED}[ERROR]{bcolors.RESET} Could not install {pkg}: {e}")
                print(f"{bcolors.RED}[INFO]{bcolors.RESET} Run manually: pip3 install {pkg}")
                sys.exit(1)
    print(f"{bcolors.RED}[+]{bcolors.RESET} Requirements installed.\n")


def is_js_url(entry):
    """True if entry looks like a JS file (ignores ?query and #fragment).

    Examples that must PASS:
      https://www.googletagmanager.com/gtm.js?id=GTM-KV28SC4J
      https://site.com/app.js?ver=4.3.1
      /tmp/test.js
    Examples that must SKIP:
      https://site.com/wp-json/oembed/1.0/embed?url=...
      https://site.com/wp-json/
      https://site.com/style.min.css
    """
    e = entry.strip()
    if not e:
        return False
    parsed = urlparse(e)
    
    if parsed.scheme in ("http", "https"):
        path = parsed.path.lower()
        return path.endswith(".js")
    
    clean = e.split("?")[0].split("#")[0].lower()
    return clean.endswith(".js")


def fetch_content(entry, timeout=15):
    """Fetch JS content from remote URL or local file. Returns (content, error)."""
    parsed = urlparse(entry.strip())
    if parsed.scheme in ("http", "https"):
        
        try:
            import requests
        except ImportError:
            return None, "requests module not installed"
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) jsfetch/1.0 By MuZaN"
            }
            r = requests.get(entry.strip(), headers=headers, timeout=timeout, verify=False)
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}"
            ctype = r.headers.get("Content-Type", "")
            text = r.text
            
            if "html" in ctype.lower() and "<html" in text[:2000].lower() and ".js" not in text[:2000].lower():
                pass
            return text, None
        except Exception as e:
            return None, str(e)
    else:
        
        clean = entry.strip().split("?")[0].split("#")[0]
        try:
            with open(clean, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(), None
        except Exception as e:
            return None, str(e)


DUMMY_VALUES = {
    "", "null", "undefined", "none", "test", "testing", "example",
    "changeme", "xxx", "***", "123", "password", "your_api_key",
    "your-api-key", "yourapikey", "api_key", "your_token", "placeholder",
    "false", "true",
}


def is_dummy(value):
    v = value.strip().strip('"').strip("'").lower()
    if v in DUMMY_VALUES:
        return True
    if v.startswith("your_") or v.startswith("test_") or v.startswith("example"):
        return True
    if set(v) in ({"*"}, {"x"}, {"-"}) :
        return True
    return False


def scan_javascript(content, filename):
    """Smart scan: keyword -> value extraction + high-confidence provider patterns."""
    findings = []

    
    provider_patterns = [
        (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
        (r'AIZA[0-9A-Za-z\-_]{35}', "Google API key"),
        (r'AIza[0-9A-Za-z\-_]{35}', "Google API key"),
        (r'xox[baprs]-[a-zA-Z0-9\-]{10,}', "Slack token"),
        (r'ghp_[a-zA-Z0-9]{36,}', "GitHub token"),
        (r'gho_[a-zA-Z0-9]{36,}', "GitHub OAuth token"),
        (r'sk-live-[a-zA-Z0-9]{16,}', "Stripe live key"),
        (r'rk-live-[a-zA-Z0-9]{16,}', "Stripe restricted key"),
        (r'sk-[a-zA-Z0-9]{20,}', "OpenAI/Secret key"),
        (r'ya29\.[a-zA-Z0-9\-_\.]{20,}', "Google OAuth token"),
        (r'eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_\.=]*', "JWT token"),
        (r'-----BEGIN (?:RSA )?PRIVATE KEY-----', "Private key block"),
    ]
    for pattern, desc in provider_patterns:
        for match in re.findall(pattern, content):
            if isinstance(match, tuple):
                match = match[0] if match else ""
            if not match or is_dummy(match):
                continue
            findings.append(f"{bcolors.RED}[API_KEY]{bcolors.RESET} {desc}: {match} (file: {filename})")

   
    smart_keywords = {
        
        "api_key": "API_KEY", "apikey": "API_KEY", "api-key": "API_KEY",
        "apiKey": "API_KEY", "app_key": "API_KEY", "appkey": "API_KEY",
        "public_key": "API_KEY", "publishable_key": "API_KEY",
        
        "client_secret": "SECRET", "clientSecret": "SECRET",
        "secret_key": "SECRET", "secretKey": "SECRET",
        "private_key": "SECRET", "privateKey": "SECRET",
        "aws_secret": "SECRET", "app_secret": "SECRET",
        
        "auth_token": "TOKEN", "authtoken": "TOKEN", "auth-token": "TOKEN",
        "authToken": "TOKEN", "access_token": "TOKEN", "accessToken": "TOKEN",
        "refresh_token": "TOKEN", "refreshToken": "TOKEN",
        "id_token": "TOKEN", "bearer": "TOKEN",
        "session_token": "TOKEN", "csrf_token": "TOKEN",
        
        "password": "CRED", "passwd": "CRED", "pwd": "CRED",
        "username": "CRED", "login": "CRED",
    }
    
    seen_values = set()
    for keyword, label in smart_keywords.items():
        kw = re.escape(keyword)
        patterns = [
            rf'["\']?{kw}["\']?\s*:\s*["\']([^"\'\s;,<>}}]{{4,}})["\']',
            rf'["\']?{kw}["\']?\s*=\s*["\']?([^"\'\s;,<>}}]{{4,}})["\']?',
        ]
        for pat in patterns:
            for match in re.findall(pat, content, re.IGNORECASE):
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                value = match.strip().strip(',').strip(';')
                if not value or is_dummy(value) or len(value) < 4:
                    continue
                # skip obvious non-secrets (function calls, booleans, numbers alone)
                if value in ("true", "false", "null", "undefined"):
                    continue
                if value.lower() in seen_values:
                    continue
                seen_values.add(value.lower())
                findings.append(
                    f"{bcolors.RED}[{label}]{bcolors.RESET} {keyword}: {value} (file: {filename})"
                )

    
    for match in re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content):
        if is_dummy(match):
            continue
        findings.append(f"{bcolors.RED}[CRED]{bcolors.RESET} Email: {match} (file: {filename})")

   
    url_pattern = r'(https?://[^\s<>"\'`]+)'
    for match in re.findall(url_pattern, content):
        parsed = urlparse(match)
        if parsed.netloc:
            findings.append(f"{bcolors.RED}[URL]{bcolors.RESET} Endpoint: {match} (file: {filename})")

    
    seen = set()
    uniq = []
    for f in findings:
        if f not in seen:
            seen.add(f)
            uniq.append(f)
    return uniq


def ask(prompt):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


def ask_logs():
    """Ask: show logs in terminal or not. Returns True = show logs."""
    while True:
        ans = ask(f"{bcolors.RED}[?]{bcolors.RESET} Show logs in terminal? (y/n): ").lower()
        if ans in ("y", "yes", "1", "show"):
            return True
        if ans in ("n", "no", "0", "hide"):
            return False
        print("Please answer y or n.")


def normalize_domain(d):
    d = d.strip().strip('"').strip("'").strip("/")
    if not d:
        return ""
    if not d.startswith(("http://", "https://")):
        d = "https://" + d
    return d


def extract_js_urls_from_html(html, base_url):
    """Extract <script src=...> JS URLs from HTML, resolved to absolute."""
    from urllib.parse import urljoin
    found = []
    for m in re.findall(r'<script[^>]+src\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE):
        src = m.strip()
        if not src or src.startswith(("data:", "javascript:", "blob:")):
            continue
        abs_url = urljoin(base_url, src)
        if is_js_url(abs_url):
            found.append(abs_url)
    # dedupe, keep order
    seen, uniq = set(), []
    for u in found:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def run_scan(entries, output_file, verbose=True):
    """Mission 1: scan JS files/URLs for secrets."""
    if verbose:
        print(f"\n{bcolors.RED}[JS FETCH]{bcolors.RESET} Scanning JavaScript files...")
        print(f"{gradient_text('JS FETCH - JS SECURITY SCANNER', 'FF0000', '000000')}\n")
    else:
        print(f"{bcolors.RED}[*]{bcolors.RESET} Scanning {len(entries)} JS targets (quiet mode)...")

    total_findings = 0
    with open(output_file, "w", encoding="utf-8") as out:
        for i, raw in enumerate(entries, 1):
            entry = raw.strip().strip('"').strip("'")
            if not entry:
                continue
            if not is_js_url(entry):
                if verbose:
                    print(f"[SKIP] Not a JS file: {entry}")
                continue
            if verbose:
                print(f"{bcolors.RED}[FETCH]{bcolors.RESET} {entry}")
            else:
                sys.stdout.write(f"\r[>] Scanning {i}/{len(entries)} | secrets: {total_findings}")
                sys.stdout.flush()
            content, err = fetch_content(entry)
            if content is None:
                if verbose:
                    print(f"[SKIP] Could not fetch: {entry} ({err})")
                continue
            findings = scan_javascript(content, entry)
            if verbose and not findings:
                print(f"{bcolors.RED}[OK]{bcolors.RESET} No secrets found: {entry}")
            for finding in findings:
                if verbose:
                    print(finding)
                clean = re.sub(r'\x1b\[[0-9;]+m', '', finding)
                out.write(clean + "\n")
            total_findings += len(findings)

    if not verbose:
        sys.stdout.write("\n")
    print(f"\n{bcolors.RED}Results saved to: {output_file} ({total_findings} findings){bcolors.RESET}")


def run_fetch_domains(domains, output_file, verbose=True):
    """Mission 2: fetch JS URLs from normal domain(s)."""
    if verbose:
        print(f"\n{bcolors.RED}[JS FETCHER]{bcolors.RESET} Extracting JS URLs from domains...")
        print(f"{gradient_text('JS URL FETCHER', 'FF0000', '000000')}\n")
    else:
        print(f"{bcolors.RED}[*]{bcolors.RESET} Fetching JS URLs from {len(domains)} domain(s) (quiet mode)...")

    try:
        import requests
    except ImportError:
        print(f"{bcolors.RED}[ERROR]{bcolors.RESET} requests not installed.")
        sys.exit(1)

    all_js = []
    with open(output_file, "w", encoding="utf-8") as out:
        for i, d in enumerate(domains, 1):
            base = normalize_domain(d)
            if not base:
                continue
            if verbose:
                print(f"{bcolors.RED}[FETCH]{bcolors.RESET} {base}")
            else:
                sys.stdout.write(f"\r[>] Domains {i}/{len(domains)} | js urls: {len(all_js)}")
                sys.stdout.flush()
            try:
                r = requests.get(
                    base,
                    headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) jsfetch/1.0 By MuZaN"},
                    timeout=20, verify=False,
                )
                if r.status_code != 200:
                    if verbose:
                        print(f"[SKIP] {base} -> HTTP {r.status_code}")
                    continue
                js_urls = extract_js_urls_from_html(r.text, base)
                if verbose:
                    if not js_urls:
                        print(f"{bcolors.RED}[OK]{bcolors.RESET} No JS URLs found: {base}")
                    for u in js_urls:
                        print(f"{bcolors.RED}[JS]{bcolors.RESET} {u}")
                for u in js_urls:
                    if u not in all_js:
                        all_js.append(u)
                        out.write(u + "\n")
            except Exception as e:
                if verbose:
                    print(f"[SKIP] {base} -> {e}")
                continue

    if not verbose:
        sys.stdout.write("\n")
    print(f"\n{bcolors.RED}JS URLs saved to: {output_file} ({len(all_js)} urls){bcolors.RESET}")


def interactive_menu():
    print(f"{bcolors.RED}[1]{bcolors.RESET} Scan JS files (scan urls for api keys / tokens / passwords)")
    print(f"{bcolors.RED}[2]{bcolors.RESET} Fetch JS urls from a normal domain (new)")
    choice = ask(f"{bcolors.RED}Select 1 or 2:{bcolors.RESET} ").strip()
    if choice not in ("1", "2"):
        print(f"{bcolors.RED}[ERROR]{bcolors.RESET} Please select 1 or 2.")
        sys.exit(1)

    if choice == "1":
        in_file = ask("Enter path of file containing JS urls: ")
        if not in_file or not os.path.exists(in_file):
            print(f"{bcolors.RED}[ERROR]{bcolors.RESET} File not found: {in_file}")
            sys.exit(1)
        out_file = ask("Enter output file path: ") or "output.txt"
        verbose = ask_logs()
        with open(in_file, "r", encoding="utf-8", errors="ignore") as f:
            entries = [l.strip() for l in f if l.strip()]
        run_scan(entries, out_file, verbose=verbose)
    else:
        print(f"{bcolors.RED}[1]{bcolors.RESET} File (file with domains)")
        print(f"{bcolors.RED}[2]{bcolors.RESET} Domain (single domain)")
        sub = ask(f"{bcolors.RED}File or domain? Select 1 or 2:{bcolors.RESET} ").strip()
        domains = []
        if sub == "1":
            p = ask("Enter path of the file: ")
            if not p or not os.path.exists(p):
                print(f"{bcolors.RED}[ERROR]{bcolors.RESET} File not found: {p}")
                sys.exit(1)
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                domains = [l.strip() for l in f if l.strip()]
        elif sub == "2":
            d = ask("Enter the domain (ex: example.com): ")
            if not d:
                print(f"{bcolors.RED}[ERROR]{bcolors.RESET} Empty domain.")
                sys.exit(1)
            domains = [d]
        else:
            print(f"{bcolors.RED}[ERROR]{bcolors.RESET} Please select 1 or 2.")
            sys.exit(1)
        out_file = ask("Enter output file path: ") or "js_urls.txt"
        verbose = ask_logs()
        run_fetch_domains(domains, out_file, verbose=verbose)

    # Footer - plain red only (no gradient) as requested
    print(f"\n{bcolors.RED}By MuZaN{bcolors.RESET}\n")


def main():
   
    ascii_art_animation()
    print(f"{bcolors.RED}By MuZaN (github.com/muzanespisito){bcolors.RESET}\n")

    
    ensure_requirements()

    parser = argparse.ArgumentParser(
        description="JS Fetch - JavaScript scanner - By MuZaN",
        epilog="By MuZaN",
    )
    parser.add_argument("-f", "--file", required=False, default=None,
                        help="File containing JavaScript URLs (scan mode)")
    parser.add_argument("-d", "--domain", required=False, default=None,
                        help="Single domain to fetch JS urls from (fetch mode)")
    parser.add_argument("--domains-file", required=False, default=None,
                        help="File containing domains (fetch mode)")
    parser.add_argument("-o", "--output", required=False, default=None,
                        help="Output file for findings")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Quiet mode: one progress line, no spam")
    args = parser.parse_args()
    verbose = not args.quiet

    
    if args.domain or args.domains_file:
        if not args.output:
            print(f"{bcolors.RED}[ERROR]{bcolors.RESET} -o output is required.")
            sys.exit(1)
        domains = []
        if args.domain:
            domains = [args.domain]
        else:
            if not os.path.exists(args.domains_file):
                print(f"{bcolors.RED}[ERROR]{bcolors.RESET} File not found: {args.domains_file}")
                sys.exit(1)
            with open(args.domains_file, "r", encoding="utf-8", errors="ignore") as f:
                domains = [l.strip() for l in f if l.strip()]
        run_fetch_domains(domains, args.output, verbose=verbose)
        print(f"\n{bcolors.RED}By MuZaN{bcolors.RESET}\n")
        return

    
    if args.file:
        if not args.output:
            print(f"{bcolors.RED}[ERROR]{bcolors.RESET} -o output is required.")
            sys.exit(1)
        if not os.path.exists(args.file):
            print(f"{bcolors.RED}[ERROR]{bcolors.RESET} Input file not found: {args.file}")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            entries = [l.strip() for l in f if l.strip()]
        run_scan(entries, args.output, verbose=verbose)
        print(f"\n{bcolors.RED}By MuZaN{bcolors.RESET}\n")
        return

    
    interactive_menu()


if __name__ == "__main__":
    main()
