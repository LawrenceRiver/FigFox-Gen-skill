#!/usr/bin/env python3
"""Check this self-contained Skill package without making model/network calls."""
from pathlib import Path
import ast
import importlib.util
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['SKILL.md','agents/openai.yaml','requirements.txt','references/workflow.md','references/debate.md','references/generation-rules.md','references/quality-notes.md','scripts/extract_pdf.py']

def main():
    errors=[]
    if sys.version_info < (3,10):errors.append('Python 3.10+ required')
    for name in REQUIRED:
        p=ROOT/name
        if not p.is_file() or not p.stat().st_size:errors.append('Missing/empty: '+name)
    if importlib.util.find_spec('fitz') is None:errors.append('Install requirements.txt: PyMuPDF is missing')
    for p in (ROOT/'scripts').glob('*.py'):
        try:ast.parse(p.read_text())
        except SyntaxError as exc:errors.append(f'{p.name}: {exc}')
    if (ROOT/'SKILL.md').is_file():
        entry=(ROOT/'SKILL.md').read_text()
        if not entry.startswith('---\nname: posfox-gen\n'):errors.append('Unexpected Skill frontmatter/name')
        for target in re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)',entry):
            if '://' not in target and not (ROOT/target).is_file():errors.append('Broken Skill link: '+target)
    if errors:
        for err in errors:print('FAIL:',err)
        return 1
    print('OK: Skill files, local links, Python syntax and PDF dependency. No model call or framework test performed.')
    return 0

if __name__=='__main__':raise SystemExit(main())
