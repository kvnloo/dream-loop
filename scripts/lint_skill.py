#!/usr/bin/env python3
"""Lint portable skill metadata, local Markdown links, JSON and Python syntax."""
import argparse
import ast
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import yaml
import jsonschema


def lint(root):
    root=Path(root);errors=[];counts={'markdown':0,'json':0,'python':0}
    try:
        text=(root/'SKILL.md').read_text()
        if not text.startswith('---\n'):raise ValueError('YAML frontmatter missing')
        fm=yaml.safe_load(text.split('---',2)[1])
        if not isinstance(fm,dict):raise ValueError('frontmatter must be mapping')
        name=fm.get('name');desc=fm.get('description')
        if not isinstance(name,str) or not re.fullmatch('[a-z0-9_-]{1,64}',name):errors.append('invalid skill name')
        if not isinstance(desc,str) or not desc.startswith('Use when ') or len(desc)>60:
            errors.append('description must start Use when and be <=60 characters')
    except (OSError,ValueError,IndexError,yaml.YAMLError) as e:errors.append('SKILL.md: '+str(e))
    for path in sorted(root.rglob('*')):
        if not path.is_file() or any(x in {'.git','__pycache__','.venv','node_modules'} for x in path.parts):continue
        rel=str(path.relative_to(root))
        try:
            if path.suffix=='.md':
                counts['markdown']+=1
                text=path.read_text()
                # Code examples are not link contracts. Inline links elsewhere are.
                text=re.sub(r'```.*?```','',text,flags=re.S)
                for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
                    target=link.split(' "',1)[0].strip('<>')
                    url=urlsplit(target)
                    if url.scheme or not url.path or url.path.startswith('/') or '<' in target:continue
                    if not (path.parent/unquote(url.path)).exists():errors.append(f'{rel}: missing link {target}')
            elif path.suffix=='.json':
                counts['json']+=1;data=json.loads(path.read_text())
                if path.name.endswith('.schema.json'):jsonschema.Draft202012Validator.check_schema(data)
            elif path.suffix=='.py':
                counts['python']+=1;ast.parse(path.read_text(),filename=str(path))
        except (ValueError,SyntaxError,OSError,jsonschema.SchemaError) as e:errors.append(f'{rel}: {e}')
    return {'root':str(root.resolve()),'counts':counts,'errors':errors,'ok':not errors}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',nargs='?',default=str(Path(__file__).resolve().parents[1]));a=p.parse_args()
    result=lint(a.root);print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['ok'] else 1)


if __name__=='__main__':main()
