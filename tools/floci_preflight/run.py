"""Floci first-lesson preflight entry point.

    python tools/floci_preflight/run.py subnet   # plain mock-EC2 lanes, no Docker socket
    python tools/floci_preflight/run.py java     # privileged DIND + real Java 25 EC2 guests
    python tools/floci_preflight/run.py all

Raw evidence goes to target/floci-preflight/<run>/<part>/ (git-ignored). The run's
machine-readable result is target/floci-preflight/<run>/summary.json.
"""
from __future__ import annotations

import json
import sys

from common import TARGET, new_run_id


def main(argv: list[str]) -> int:
    parts = {'subnet': ['subnet'], 'java': ['java'], 'all': ['subnet', 'java']}[argv[1] if len(argv) > 1 else 'all']
    run_id = new_run_id()
    results = {}
    for part in parts:
        if part == 'subnet':
            import subnet_contract
            results[part] = subnet_contract.main(run_id)
        else:
            import java_guest
            results[part] = java_guest.main(run_id)
    ok = all(not r['fatal'] and not r.get('cases_bad') and r['host_inventory_clean'] for r in results.values())
    summary = {'run_id': run_id, 'parts': {p: {k: v for k, v in r.items() if k != 'host_diff'}
                                           for p, r in results.items()},
               'all_ok': ok}
    out = TARGET / run_id / 'summary.json'
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'summary: {out}  all_ok={ok}', flush=True)
    for p, r in results.items():
        print(f"  {p}: cases {r.get('cases_ok')}/{r.get('cases_total')} fatal={r['fatal']} "
              f"host_clean={r['host_inventory_clean']} bad={r.get('cases_bad')}", flush=True)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
