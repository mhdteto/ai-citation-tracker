# Input contract, counting and limitations

## Collection workflow

This program imports observations you supply. Collect answers manually or export them through an authorized process outside this repository. Record the exact prompt, full answer, collection date, engine label, specific model label, interface, language and market. Use `unknown` as a disclosed model label if the interface does not reveal it; do not pretend two unknown models are a controlled model comparison. Market is your observation context, not an inferred user location.

Copy only URLs explicitly shown as citations in the source answer/interface. Do not manufacture URLs from brand mentions or search independently for a supporting page and count that as an AI citation. Linked navigation, recommendations and cited sources may differ by interface; document which you captured. The tool cannot verify capture authenticity or detect missing citations. Keep a capture, timestamp and collection protocol separately if your study needs an audit trail. Remove personal/confidential information before sharing reports: raw prompts and answers are exported.

## CSV rules

Use comma delimiters, double-quoted fields for commas/newlines/quotes, and doubled embedded quotes. UTF-8 with an optional initial BOM is accepted; row field counts and exact ordered headers are enforced. Blank rows are rejected. Unterminated or stray quotes are rejected. Every answer field must be nonempty after whitespace checking, but original values are preserved. Both IDs are 1–128 ASCII letters/digits plus `_.:-`, beginning with a letter/digit. Answer IDs must be unique within the dataset. One prompt ID must map to exactly one prompt text within a dataset; prompt IDs can repeat for repeated observations. Dates must be real `YYYY-MM-DD` dates no later than the required `--as-of` cutoff.

`interface` has four values: `web`, `app`, `api`, `other`. Language tags follow the documented simplified syntax: 2–3 lowercase letters followed by optional 2–8 alphanumeric hyphen-separated subtags. This is a syntax check, not an IANA registry validator. Engine, model and market are arbitrary nonempty labels. Exact label strings determine groups; case and whitespace are not silently merged. Citation rows must reference an existing answer ID. An empty answer dataset is rejected; a header-only citations dataset is accepted.

## URL normalization

Only absolute HTTP(S) URLs without credentials are accepted. Scheme and DNS hostname are lowercased; international hostnames use Python's built-in IDNA codec. IPv6 addresses are compressed and bracketed. A trailing DNS dot is removed, default ports 80 (HTTP) and 443 (HTTPS) are omitted, and an empty path becomes `/`. Fragments are discarded. Path case, percent escapes, query spelling and query order are preserved; query parameters are never removed, sorted or interpreted. Invalid hostname syntax, port range, percent escapes, controls, whitespace and backslashes are rejected.

Normalization is conservative and offline. HTTP and HTTPS stay distinct. Different queries, tracking parameters, paths, trailing slashes and percent-encoding spellings can remain distinct even if a server would redirect them to the same content. No redirect following, canonical extraction, DNS resolution, fetch, reachability check or Public Suffix List exists. A syntactically accepted URL need not exist. The complete hostname is the aggregation label; this is not a registrable-domain parser.

Within each answer, identical normalized URLs collapse into one citation. Across different answer IDs, each URL counts again. A hostname citation count counts distinct per-answer URLs: two URLs on one hostname in one answer contribute two citations, while that hostname's answer count contributes one. Answers with no citation contribute to answer counts and reduce the cited-answer fraction. None of these metrics estimates factual accuracy, source quality, authority, endorsement or an engine's hidden training/retrieval use.

## Outputs

`report.json` contains methodology, denominator definitions, groups (including prompt IDs, observed date ranges and all ranked hostnames) and all raw answer records with normalized URLs. `answers.csv` retains answer text and metadata plus citation/hostname counts; `groups.csv` contains summary metrics; `citations.csv` maps answers to normalized URLs/hostnames; `hostnames.csv` contains every group/hostname count. `report.html` is a self-contained accessible-table view with raw details and no JavaScript or external assets. No current clock or nondeterministic identifier is added; use the same cutoff and inputs to reproduce outputs.

Every exported CSV field is explicitly quoted, including fields containing embedded carriage returns, to preserve single-cell boundaries with LF record endings. HTML text and link attributes are escaped; accepted links are limited to HTTP(S). CSV values with a formula introducer (`=`, `+`, `-`, `@`) following BOM/Unicode whitespace receive a leading apostrophe. CSV safe-export escaping can change a spreadsheet cell's literal text; JSON retains original values. A browser or spreadsheet may still request network resources when you explicitly open a link; the Python tool itself makes no network calls.

The output directory and its ancestors must not be symlinks; provide a real resolved path where systems alias `/tmp` or `/var`. Every planned target is checked against input paths by resolution and same-file identity; symlink targets, input hardlinks and mutually aliased outputs are rejected before writes. Output files should be in a directory controlled by you. The guards do not claim protection against another process racing to change filesystem entries during a run. Writes are sequential; a disk/permission failure can leave partial output. Re-run after fixing the error.

## Window comparison protocol

V1 exports one dataset at a time. Prepare two windows as separate answer/citation CSV pairs and generate separate reports. Do not append two windows and treat the pooled group summaries as period-specific metrics. For side-by-side comparison, first match exact engine, model, interface, language and market, then restrict both datasets to the same prompt IDs and exact texts. Keep comparable repetition counts, sampling protocol, personalization/session settings and period length. Report raw counts beside fractions. Do not compare absent groups as zeros. Small or convenience samples are descriptive; differences do not establish a trend, causal change or population-level ranking. The tool does not automatically establish comparability or compute a delta.

## Example provenance

All supplied example observations, prompts, model/engine labels and citation URLs were authored as fiction for this repository. They are not measurements from a real AI service. Northstar Studio and Atlas Lab are illustrative names, not clients or claims of results. Reserved `.example` names are deliberate. The fixed cutoff is 2026-11-01, not a statement about live platform behavior.
