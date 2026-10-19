"""Single authoring and validation registration, shared with the Rust build adapter."""
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load_registry(catalog=None):
    if catalog is None:
        catalog=json.loads((ROOT/'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
    rows=[]; seen={field:set() for field in ('key','revision','pilot','folder')}
    for course in catalog['courses']:
        for item in course['lessons']:
            key=item['key']; validation=dict(item['validation'])
            source=re.fullmatch(r'tools/redesigned_lessons/([a-z0-9_]+)/approved-prd\.json',item['authoring_prd'])
            if not source or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',key):
                raise ValueError('Invalid lesson registration path or key')
            row=dict(key=key,folder=source[1],revision=item['revision'],pilot=validation.pop('pilot'),driver=validation.pop('driver'),config=validation)
            if len(row['pilot'])!=1 or row['pilot'] in 'abcdefghijm' or row['driver'] not in ('native','code','git-remote'):
                raise ValueError('Invalid validation identity or driver')
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',row['revision']):raise ValueError('Invalid lesson revision')
            for field,values in seen.items():
                if row[field] in values:raise ValueError(f'duplicate {field}: {row[field]}')
                values.add(row[field])
            rows.append(row)
    return rows
