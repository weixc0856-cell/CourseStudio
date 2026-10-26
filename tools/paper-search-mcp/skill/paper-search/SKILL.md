---
name: paper-search
description: Search, download, and read academic papers from 20+ sources (arXiv, PubMed, Semantic Scholar, Crossref, OpenAlex, etc). Use when the user asks to find papers, search research literature, look up a paper by DOI, download a paper PDF, or extract text from a paper.
---

# Paper Search

Search, download, and read academic papers through a **project-local** install.

## Invocation

Always call the launcher by absolute path:

- Bash (Git Bash / WSL-style shell):
  ```bash
  /d/CourseStudio/tools/paper-search-mcp/bin/paper-search <command> [args]
  ```
- PowerShell:
  ```powershell
  & D:\CourseStudio\tools\paper-search-mcp\bin\paper-search.cmd <command> [args]
  ```

Do **not** run `uv tool install paper-search-mcp`, `pip install`, `uvx`, or add anything
to PATH. Dependencies live in `D:\CourseStudio\tools\paper-search-mcp\.venv` and optional
API keys are read from `D:\CourseStudio\.config\paper-search-mcp\.env`; the launcher sets
`PAPER_SEARCH_MCP_ENV_FILE` for you.

If the launcher reports a missing environment, repair it with:

```bash
cd /d/CourseStudio/tools/paper-search-mcp && uv sync --frozen
```

## Commands

### Search

```bash
<launcher> search "<query>" -n <max_per_source> -s <sources> -y <year>
```

- `-n`: results per source (default: 5)
- `-s`: comma-separated sources, `fast`, `fastest`, or `all` (default: all)
- `-y`: year filter, e.g. `2020` or `2018-2022` (Semantic Scholar)
- `--source-timeout SECONDS`: per-source bound

Speed presets:

- `-s fastest`: OpenAlex + Crossref only — quickest first pass
- `-s fast`: OpenAlex, Crossref, arXiv, PubMed, Europe PMC (+ Semantic Scholar when keyed)
- `-s all`: broad default set; optional paid sources are never added automatically

Explicit source choices are never expanded. Use `-s unpaywall` for DOI lookup.

### Download PDF

```bash
<launcher> download <source> <paper_id> [-o <save_dir>]
```

Save into the active course's research/downloads folder by default rather than the CWD
when a course project is in scope.

### Read (extract text)

```bash
<launcher> read <source> <paper_id> [-o <save_dir>]
```

`--full-text` requests identity-verified article text where the source supports it;
an abstract-only result is not full text.

### List sources

```bash
<launcher> sources
```

### Call MCP-equivalent tools directly

```bash
<launcher> tool --list
<launcher> tool search_crossref "transformer attention" --filter from-pub-date:2024-01-01 --sort published --order desc --max-results 2
<launcher> tool get_crossref_paper_by_doi 10.1038/nature12373
```

Objects and lists return JSON; text and download paths return plain text. Exceptions
return a JSON error with exit code 1; invalid CLI syntax exits with code 2.

## Output

`search` and `download` return JSON. `read` returns plain text. Config warnings go to
stderr and can be ignored.

## Sources

arxiv, pubmed, biorxiv, medrxiv, google_scholar, iacr, semantic, crossref, openalex,
pmc, core, europepmc, dblp, openaire, citeseerx, doaj, base, zenodo, hal, ssrn,
openreview, unpaywall, acm

Optional: `ieee` (needs `PAPER_SEARCH_MCP_IEEE_API_KEY`), `wos` / `scopus` (need their
keys and explicit selection). ACM is keyless via Crossref metadata; PDF access may
need an OA fallback.

## Workflow

1. Search with a targeted source set (`fast` or `fastest` first unless breadth matters).
2. Present results as a table: title, authors, year, source, DOI/URL.
3. For full text, use `read <source> <paper_id>`.
4. For the PDF, use `download <source> <paper_id>` and report the saved path.
5. For course work, record title, DOI/URL, and access date in the course's
   `research/` claim ledger; do not cite a paper you have not opened.

Rate limits, CAPTCHA, publisher paywalls, and upstream outages are expected failure
modes. Report them as such instead of silently substituting an unverified source.
