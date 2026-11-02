# Connected fictional example

**Entirely fictional teaching data:** Alex Rowan, Cedar Notes, publishers, HTTP responses, reviews, engines and answers are invented. Reserved example domains are placeholders. No client case or live AI measurement is presented.

Run from the repository root:

```sh
python3 tracker.py --answers examples/connected-workflow/inputs/answers.csv --citations examples/connected-workflow/inputs/citations.csv --as-of 2026-11-01 --output examples/connected-workflow/report
```

Inputs: [answers.csv](inputs/answers.csv) · [citations.csv](inputs/citations.csv)

## Expected output

English / United Kingdom: 2 cited answers out of 4 (50%), 3 normalized explicit citations summed across answers. French / France: 1 out of 2 (50%), 1 citation. The five raw citation rows include a fragment duplicate within uk-1. These invented fractions are not a market benchmark, improvement claim or factual-support judgment.

Inspect [the generated HTML](report/report.html) and [JSON](report/report.json). The command replaces the report directory’s output files; keep your own inputs elsewhere.

## Where this fits

[Follow the complete five-tool workflow](https://github.com/mhdteto/authority-architecture-system/tree/main/examples/fictional-workflow) · [Operating method](https://github.com/mhdteto/authority-architecture-system) · [Next: authority-architecture-system](https://github.com/mhdteto/authority-architecture-system)

These original synthetic inputs and reports use CC BY 4.0; the tool retains its existing code license. Verify reproduction with:

```sh
python3 tools/verify_connected_example.py
```
