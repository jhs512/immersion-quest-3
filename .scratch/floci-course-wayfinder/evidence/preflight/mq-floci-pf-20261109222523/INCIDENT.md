# mq-floci-pf-20261109222523 (run.py all): harness crash, kept

subnet 19/19 contract cases OK, lanes removed. Then compare_snapshots raised TypeError (harness bug: iterated new non-dict keys),
so host-diff.json/summary.json were not written and the java part never started. The diff was recomputed afterwards
from the saved host-before/after.json with the fixed function: clean=true. This run is not counted as a complete attempt.
