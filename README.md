# JS Fetch V2

JS Fetch V2 is a Python-based JavaScript security scanner and JavaScript URL discovery tool.

It provides two main capabilities:

1. Scan JavaScript files and URLs for potentially exposed secrets, tokens, credentials, and endpoints.
2. Extract JavaScript URLs directly from a domain or a list of domains.

The tool also includes an interactive mode, quiet mode, automatic dependency checking, duplicate filtering, and smarter detection designed to reduce obvious false positives.

## Features

* Scan remote JavaScript URLs
* Scan local JavaScript files
* Extract JavaScript URLs from HTML pages
* Support single domains
* Support a file containing multiple domains
* Detect common API keys and secret patterns
* Detect authentication and access tokens
* Detect passwords and username assignments
* Detect email addresses
* Detect private key blocks
* Extract HTTP and HTTPS endpoints
* Ignore common dummy and placeholder values
* Remove duplicate findings
* Interactive menu
* Quiet mode for cleaner output
* Progress information during large scans
* Automatic `requests` dependency check
* Save results directly to output files

## Requirements

* Python 3
* Internet connection when working with remote URLs or domains

The tool automatically checks for the `requests` package and attempts to install it if it is missing.

You can also install it manually:

```bash
pip3 install requests
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Muzanespisito/javascript-scan.git
cd javascript-scan
```

Make the script executable if needed:

```bash
chmod +x jsfetch.py
```

Run it with:

```bash
python3 jsfetch.py
```

## How It Works

JS Fetch V2 has two main scanning modes.

```text
                    JS Fetch V2
                         |
              +----------+----------+
              |                     |
           Scan Mode            Fetch Mode
              |                     |
       Existing JS URLs          Domain(s)
              |                     |
       Fetch JS content       Extract <script>
              |                     |
       Scan for secrets       Collect JS URLs
              |                     |
          Save findings        Save JS URLs
```

The tool can also be used through the interactive menu if no mode is supplied.

## Mode 1: Scan JavaScript URLs

This mode takes a file containing JavaScript URLs and scans each JavaScript resource for potentially sensitive information.

Example:

```bash
python3 jsfetch.py -f urls.txt -o findings.txt
```

Example `urls.txt`:

```text
https://example.com/app.js
https://example.com/main.js
https://example.com/assets/config.js
```

The scanner verifies that entries look like JavaScript files before attempting to fetch them. Query strings and fragments are handled when determining whether a resource is a `.js` file.

## Mode 2: Fetch JavaScript URLs From a Domain

V2 can discover JavaScript files directly from a normal web page.

For a single domain:

```bash
python3 jsfetch.py -d example.com -o js_urls.txt
```

The tool requests the page, searches for `<script src="...">` references, resolves relative URLs, filters JavaScript resources, removes duplicates, and writes the discovered URLs to the output file.

## Multiple Domains

You can also provide a file containing multiple domains.

Example `domains.txt`:

```text
example.com
example.org
example.net
```

Run:

```bash
python3 jsfetch.py --domains-file domains.txt -o js_urls.txt
```

The tool processes each domain and saves the discovered JavaScript URLs to the specified output file.

## Interactive Mode

If you run the tool without specifying a scan or fetch mode:

```bash
python3 jsfetch.py
```

JS Fetch V2 opens an interactive menu:

```text
[1] Scan JS files
[2] Fetch JS urls from a normal domain
```

### Scan Mode

Select:

```text
1
```

You will be asked for:

```text
Enter path of file containing JS urls:
Enter output file path:
Show logs in terminal? (y/n):
```

### Fetch Mode

Select:

```text
2
```

You can then choose between:

```text
[1] File
[2] Domain
```

This allows you to either provide multiple domains from a file or scan a single domain.

## Quiet Mode

For larger scans, you can use quiet mode to reduce terminal output.

Example:

```bash
python3 jsfetch.py -f urls.txt -o findings.txt -q
```

Quiet mode displays a compact progress line instead of printing every individual result to the terminal.

## Secret Detection

JS Fetch V2 includes provider-specific patterns for several common credential formats, including:

* AWS access keys
* Google API keys
* Slack tokens
* GitHub tokens
* GitHub OAuth tokens
* Stripe live keys
* Stripe restricted keys
* OpenAI-style secret keys
* Google OAuth tokens
* JWT tokens
* Private key blocks

These patterns are implemented directly in the scanner.

## Smart Keyword Detection

In addition to provider-specific patterns, the scanner searches for sensitive keywords such as:

```text
api_key
apikey
apiKey
client_secret
clientSecret
private_key
access_token
refresh_token
id_token
bearer
session_token
csrf_token
password
username
login
```

It then attempts to extract the associated value.

## False Positive Filtering

V2 includes filtering for common placeholder values such as:

```text
null
undefined
test
testing
example
changeme
xxx
password
your_api_key
your-api-key
your_token
placeholder
```

Values beginning with patterns such as `your_`, `test_`, and `example` are also ignored.

This helps reduce obvious false positives from development and example configurations.

## Endpoint Discovery

The scanner also extracts HTTP and HTTPS URLs found inside JavaScript content.

Example:

```text
[URL] Endpoint: https://api.example.com/v1/users
```

These findings are written to the output together with other detected information.

## Output

Scan results are saved to the file specified with `-o`.

Example:

```bash
python3 jsfetch.py -f urls.txt -o findings.txt
```

The tool reports the total number of findings when the scan finishes:

```text
Results saved to: findings.txt (12 findings)
```

## Command Line Options

```text
-f, --file
    File containing JavaScript URLs for scan mode.

-d, --domain
    Single domain to fetch JavaScript URLs from.

--domains-file
    File containing multiple domains for fetch mode.

-o, --output
    Output file for results.

-q, --quiet
    Enable quiet mode with compact progress output.
```

These options are defined in the V2 command-line interface.

## Examples

Scan JavaScript URLs:

```bash
python3 jsfetch.py -f urls.txt -o findings.txt
```

Fetch JavaScript URLs from one domain:

```bash
python3 jsfetch.py -d example.com -o js_urls.txt
```

Fetch JavaScript URLs from multiple domains:

```bash
python3 jsfetch.py --domains-file domains.txt -o js_urls.txt
```

Run a scan in quiet mode:

```bash
python3 jsfetch.py -f urls.txt -o findings.txt -q
```

Run interactive mode:

```bash
python3 jsfetch.py
```

## Responsible Use

JS Fetch V2 is intended for authorized security testing, research, bug bounty programs, and security assessments.

Only scan websites, domains, and JavaScript resources that you own or have explicit permission to test.

The presence of a detected key, token, credential, or endpoint does not automatically mean that it is valid, active, or exploitable. Findings should be verified responsibly and handled according to the applicable security disclosure policy.

## Author

**MuZaN**

GitHub:

https://github.com/Muzanespisito

## Disclaimer

This project is provided for security research and educational purposes.

The author is not responsible for misuse of the tool or for unauthorized testing against systems, websites, or resources.

---

### Coded with vibe coding.
