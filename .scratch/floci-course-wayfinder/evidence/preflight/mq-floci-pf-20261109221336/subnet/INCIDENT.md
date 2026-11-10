# attempt 1 (mq-floci-pf-20261109221336) — failed, kept

1. Lane start failed: Floci exited with `chroot: cannot change root directory to '/': Operation not permitted`.
   Cause: `--cap-drop ALL` removes CAP_SYS_CHROOT that the Floci image entrypoint uses. Harness config error, not a Floci API result.
2. Host diff not clean, not caused by this run's mutations:
   - default `bridge` network id c5cd075e21e1 (Created 13:04:01Z) -> 8f93c436ba28 (Created 13:13:40.750Z = 22:13:40.750 local).
     This run's first mutation was `docker network create` at 22:13:41.663 local (events.json). The built-in bridge is recreated only
     when the daemon (re)starts, so the daemon restarted during the before-snapshot window, before any run mutation.
   - `mq3-gitlab-6afa409d` container network list order changed (bridge,ci -> ci,bridge), consistent with a daemon restart.
   - anonymous volume 0e66bb61... created 13:13:41Z, label com.docker.volume.anonymous, no container references it.
     This run created no volume and no container with volumes. Not removed: not owned by this run.
   Nothing was cleaned up or hidden. `docker events` history for the window was not retrievable (call hung, stopped).

## Correction (appended later; original text above kept unchanged)

The volume conclusion in item 2 is wrong. Anonymous volume `0e66bb6104539577091dfad80c20061466e4cafc8cdfffdfe1f7924dcedc3758`
IS owned by this run: the Floci image declares `VOLUME /app/data`, so `docker run` created it implicitly. The recorded
`owned?container` inspect in `events.json` for `/mq-floci-pf-20261109221336-student` (Config.Labels mq.lab matches this run)
lists Mounts Type=volume Name=0e66bb61... Destination=/app/data. `docker rm -f` without `-v` left it behind.
It did not exist in host-before and is the exact name added in host-after. Its removal is recorded separately in
`../ownership-cleanup.json`; the raw `host-diff.json` (clean=false) stays as recorded.
The default bridge replacement timing stands as recorded (13:13:40.750Z, before the first mutation); no global cause is claimed.
