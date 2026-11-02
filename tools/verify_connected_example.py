#!/usr/bin/env python3
"""Reproduce the connected fictional example using this repository's actual CLI."""
from pathlib import Path
import json,subprocess,sys,tempfile,hashlib
ROOT=Path(__file__).resolve().parents[1]
DEMO=ROOT/'examples/connected-workflow'
data=json.loads((DEMO/'command.json').read_text())
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as temp:
    output=Path(temp).resolve()/'report'
    args=[str(output) if v=='OUTPUT' else v for v in data['args']]
    subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
    expected={p.relative_to(DEMO/'report').as_posix():digest(p) for p in (DEMO/'report').rglob('*') if p.is_file()}
    actual={p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file()}
    assert expected==actual,'Connected fictional example does not reproduce byte-for-byte'
    print('Connected fictional example: all',len(expected),'output files match.')
