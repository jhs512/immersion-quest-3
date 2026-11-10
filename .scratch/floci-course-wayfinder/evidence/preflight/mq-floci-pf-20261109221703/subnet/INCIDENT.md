# attempt 2 (mq-floci-pf-20261109221703): 19/19 contract cases OK, host inventory NOT clean (kept)

Three anonymous volumes were added: 12d765a0... (student), c813413b... (explanation), ebb2fd37... (envcheck).
Each matches the Mounts (Destination /app/data, image `VOLUME /app/data`) of the run-labelled lane container in the
recorded `owned?container` inspect in `events.json`. Cause: `docker rm -f` without `-v`. Raw `host-diff.json` clean=false
is kept. Removal is recorded separately in `../ownership-cleanup.json`. Fix in later runs: lane `/app/data` is a
size-limited tmpfs (no implicit volume) and owned-container removal records mounts and removes anonymous volumes with `-v`.
