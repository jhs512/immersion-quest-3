# Docker networking foundations: planning evidence

Research date: 2026-11-09. Scope: facts and proposed small labs for a later course plan; no lesson implementation. All lab outcomes below are **predictions requiring validation**, not executed results. Documentation inspected online on this date; platform details must be rechecked when the course pins its Docker version.

## Inspected local state

- Isolated worktree created from `f441002c` on `research/network-docker-foundations-20261109`; original dirty checkout was not edited, staged, or switched. This note is the only intended change.
- Read-only `docker version --format '{{json .}}'` probe found a CLI but failed to connect to `npipe:////./pipe/dockerDesktopLinuxEngine`: the named pipe did not exist. No daemon was started, image downloaded, container run, or host setting changed. Therefore neither local availability nor the proposed captures are verified.
- No root glossary or ADR directory existed in this worktree. This is an inspected repository fact, not an online claim.

## Facts that constrain the learning model

### An address needs an owner and a prefix

CIDR expresses a prefix length: for IPv4, `/24` fixes the first 24 of 32 bits and corresponds to `255.255.255.0`; it is not a property of an address's first octet. Route selection uses the longest matching prefix, so an overlapping `/24` can beat a `/16`, and the default `/0` is least specific. Teach address-and-mask together before predicting local versus gateway paths. [RFC 4632, sections 3.1 and 5.1](https://www.rfc-editor.org/rfc/rfc4632.html)

RFC 1918 reserves exactly `10.0.0.0/8`, `172.16.0.0/12`, and `192.168.0.0/16` for private networks. `172.32.0.1` is outside that reservation. Private addresses are reusable across independent networks and need not be globally unique; a private address does not itself implement filtering or access control. [RFC 1918, sections 3 and 5](https://www.rfc-editor.org/rfc/rfc1918.html)

Avoid the false binary “private or public”: IANA separately records private use, `127.0.0.0/8` loopback, `169.254.0.0/16` link local, `100.64.0.0/10` shared address space, and documentation ranges. Global reachability is an explicit registry attribute, not the complement of RFC 1918 membership. [IANA IPv4 special-purpose registry](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml) IPv4 link-local traffic is for one link and routers must not forward it. [RFC 3927, section 2.6.2](https://www.rfc-editor.org/rfc/rfc3927.html)

Do not generalize “usable addresses = 2^(32-prefix)-2” to every prefix. `/31` has special point-to-point semantics; it belongs after ordinary bridge subnet exercises. [RFC 3021, section 2.1](https://www.rfc-editor.org/rfc/rfc3021.html) `/32` can represent a single destination route; introduce it with longest-prefix matching rather than as a normal multi-host LAN. [RFC 4632, section 3.1](https://www.rfc-editor.org/rfc/rfc4632.html)

**Proposed address ledger, not a promise that these ranges are free on every learner machine:**

| Owner | Example | Meaning |
|---|---|---|
| Host loopback | `127.0.0.1:18080` | Host endpoint of an explicitly published HTTP port |
| Compose `front` network | `172.30.40.0/24` | Network segment, mask `255.255.255.0` |
| Its IPAM allocation pool | `172.30.40.128/25` | Smaller pool for automatic allocation; not another interface mask |
| Its gateway | `172.30.40.1` | Proposed bridge gateway |
| `web` container | `172.30.40.10/24`, port `8080` | Deliberately static only for address/DNS experiments |
| `dns-auth` container | `172.30.40.53/24`, port `1053` | Authoritative lab server, not host resolver |
| Container loopback | `127.0.0.1` on `lo` | The current container's namespace |
| Embedded Docker DNS | `127.0.0.11` | Docker-managed resolver on a custom network |

Compose distinguishes IPAM `subnet`, allocation `ip_range`, and `gateway`; a service's static address must be covered by a declared subnet. [Compose networks](https://docs.docker.com/reference/compose-file/networks/), [Compose services: ipv4_address](https://docs.docker.com/reference/compose-file/services/#ipv4_address-ipv6_address) **Inference:** select a non-overlapping lab prefix after preflight; allow one parameter to substitute it everywhere. Do not change global daemon pools or learner VPN settings.

### Linux mechanisms and Desktop boundaries

Linux network namespaces isolate devices, IP stacks, routes, firewall rules, and socket port spaces. A veth pair joins network namespaces; it is not the same object as a bridge. [Linux network_namespaces(7)](https://www.man7.org/linux/man-pages/man7/network_namespaces.7.html), [Linux veth(4)](https://www.man7.org/linux/man-pages/man4/veth.4.html) A Linux bridge forwards at layer 2. It is not automatically a router, DHCP server, DNS server, or NAT gateway. [Linux kernel bridge documentation](https://www.kernel.org/doc/html/latest/networking/bridge.html)

Docker user-defined bridges provide scoped container-name discovery and network membership controls; Docker creates the underlying OS network objects. A bridge network spans one Docker daemon host. [Docker bridge driver](https://docs.docker.com/engine/network/drivers/bridge/) On Engine with the iptables backend, Docker installs host-namespace rules for forwarding, masquerading, and published ports. [Docker with iptables](https://docs.docker.com/engine/network/firewall-iptables/) Do not grade specific iptables chain output universally: Docker also documents an nftables firewall backend. [Docker packet filtering](https://docs.docker.com/engine/network/packet-filtering-firewalls/)

On Docker Desktop, Linux-container networking lives inside a VM; host-visible backend processes mediate traffic. [Desktop network overview](https://docs.docker.com/desktop/features/networking/) Windows/macOS learners should not expect a host `docker0`, direct access to Linux-container IPs, or successful host-to-container ping. Use port publication and container-side inspection. Windows containers are a different mode, outside this proposed baseline. [Desktop networking limitations](https://docs.docker.com/desktop/features/networking/networking-how-tos/)

Name observed interfaces from `ip -br address` / `ip route`, rather than assuming every endpoint is `eth0` or the host bridge is literally `docker0`. **Inference:** use native-Linux host veth/bridge inspection only as an optional extension. Inside-container observations and Docker metadata are the portable required path; a drawn bridge/veth diagram is a mechanism model, not proof of the learner's host topology.

### Reachability is distinct from naming and publishing

Compose creates a default bridge network and service-name discovery. Containers communicate using the **container port**; a **host port** is a separate access path. Addresses can change on recreation while service names remain stable. [Compose networking](https://docs.docker.com/compose/how-tos/networking/) Treat recreation as an exercise in rediscovery, not an assertion that an IP must change every time.

Publishing without an explicit host address generally exposes a port on all host interfaces. Bind lab ports to `127.0.0.1`; published localhost ports on Engine versions older than 28 have a documented same-L2 exposure caveat. [Docker port publishing](https://docs.docker.com/engine/network/port-publishing/) Publishing does not make a process listening only on its own container loopback reachable through its container address: the application's bind address is a separate condition. Container `127.0.0.1` refers to that container's namespace. [Docker daemon DNS troubleshooting](https://docs.docker.com/engine/daemon/troubleshoot/#dns-resolver-found-in-resolvconf-and-containers-cant-use-it)

**Inference:** an internal HTTP listener and client on the same bridge are a cheaper first lab than reaching an Internet endpoint. Use a fixed application response token to distinguish correct target reachability from “something returned HTTP 200.” Never claim two separate Compose networks perfectly emulate cloud subnet routing/security groups.

### Four different DNS roles

1. The host OS resolver serves host applications; changing a container's resolver does not reconfigure the host.
2. Docker's embedded resolver on custom networks is `127.0.0.11`, resolves Docker names, and forwards external queries to configured upstream resolvers. Containers on the default `bridge` have different resolver setup. [Docker networking: DNS](https://docs.docker.com/engine/network/#dns-services)
3. An authoritative server owns a zone's records. A resolver may recurse for a client; an iterative client follows referrals itself. These are distinct roles even if one product implements several. [RFC 1034, sections 2.4 and 4.3.1](https://www.rfc-editor.org/rfc/rfc1034.html)
4. A lab forwarding server can relay to another server without demonstrating full root-to-TLD recursion. CoreDNS `file` serves a master-file zone; `forward` proxies to configured upstreams. [CoreDNS file](https://coredns.io/plugins/file/), [CoreDNS forward](https://coredns.io/plugins/forward/)

An A record contains an IPv4 address, not a URL or port; CNAME names another DNS name. TTL concerns caching, not network reachability. [RFC 1035, sections 3.2.1, 3.3.1 and 3.4.1](https://www.rfc-editor.org/rfc/rfc1035.html) Use `quest.test.` for an explicitly configured private zone; `.test` is reserved, whereas `.localhost` has special loopback handling. [RFC 6761, sections 6.2 and 6.3](https://www.rfc-editor.org/rfc/rfc6761.html)

`dig @SERVER -p PORT NAME TYPE` queries a specified DNS endpoint; normal application resolution may use a different resolver path. Inspect status, answer type/address, TTL, authority flags and server, not just whether the process exited successfully. [ISC BIND dig manual](https://bind9.readthedocs.io/en/latest/manpages.html#dig-dns-lookup-utility)

**Proposed DNS topology:** `client -> dns-forward:1053 -> dns-auth:1053`, plus `web:8080`, all local. First explicitly query `dns-auth` with `dig`; next query the forwarder; only later change application resolver configuration. Keeping nonstandard DNS port `1053` avoids host port 53 contention and makes explicit-server exercises possible without binding a privileged port. Application resolver integration on port 53 is a later, separately validated step. Do not edit host hosts files, host DNS settings, or daemon-wide DNS for these lessons.

## Proposed tiny-lab catalogue

Each row is a **planning inference** using the mechanisms cited above, not a verified lab. Each keeps at least client and server containers running, changes one condition, records a prediction before execution, checks observations, restores the condition, then transfers to one unfamiliar address/name/port. A row may need splitting when learner testing shows too much cognitive load.

| # | One question / changed condition | Observable pass/fail evidence |
|---|---|---|
| 1 | Which process owns the port? Change server port `8080 -> 8081`. | Client can reach only the new port and receives the expected token. |
| 2 | Does each container have its own loopback? Change destination `web -> 127.0.0.1`. | Client fails locally while server remains healthy; identify both namespaces. |
| 3 | Bind address versus address assignment: server binds loopback, then all container interfaces. | Same client request changes failure to success; inspect listener independently. |
| 4 | Two endpoints, one bridge: predict source and destination IPv4. | Inspect both container addresses and match a bounded capture. |
| 5 | Port publishing: add host `127.0.0.1:18080 -> 8080`. | Host request succeeds; client still uses `web:8080`. |
| 6 | Wrong published port versus wrong container port. | One field correction restores only the intended access path. |
| 7 | Address, prefix, network: compare `/24` endpoints. | Learner computes network via bitwise AND and verifies connected route. |
| 8 | CIDR boundary `/25`: `.127` versus `.128`. | Address classification matches computed prefixes; do not assign broadcast/network endpoints. |
| 9 | CIDR boundary `/26`: same first three octets is insufficient. | Learner classifies `.63/.64`, then predicts route for safe host addresses. |
| 10 | Private boundary `172.31` versus `172.32`. | Classification uses RFC 1918 membership, not textual appearance. |
| 11 | Private, loopback, link-local, documentation and shared space. | Classification includes global reachability, not merely private/public. |
| 12 | `subnet` versus smaller automatic allocation pool. | Inspect endpoint prefix and allocation location; they answer different questions. |
| 13 | Default route versus connected subnet route. | `ip route get` chooses on-link destination or gateway as predicted. |
| 14 | Longer prefix beats broad route. | Read-only route-choice model plus `ip route get` where fixture provides both; route mutation is optional advanced work. |
| 15 | One service moved to another bridge. | Request fails; network inspection proves missing shared membership; restore membership. |
| 16 | One dual-network application joins both networks. | Its own connections succeed to each side; peers do not gain application-layer proxying automatically. |
| 17 | Service-name discovery versus literal IP. | DNS result and connection refer to the same running endpoint. |
| 18 | Add/remove a network-scoped alias. | Alias answer changes while canonical service name remains available. |
| 19 | Recreate server, rediscover by name. | Re-query and reconnect; do not require different numeric IP. |
| 20 | Query correct DNS server versus wrong endpoint. | `dig` reports intended responding server; timeout differs from NXDOMAIN. |
| 21 | Authoritative A record points to wrong but valid local IP. | DNS succeeds but HTTP token is wrong/fails; repair only record. |
| 22 | Change DNS answer without changing web listener. | Explicit query returns new address; demonstrate naming/reachability independence. |
| 23 | CNAME target versus URL/port misconception. | CNAME chain resolves; HTTP port stays application configuration. |
| 24 | Missing record versus unreachable DNS server. | Compare NXDOMAIN response to bounded timeout and server logs. |
| 25 | UDP versus TCP DNS using `dig +tcp`. | Same name queried over two transports; preserve both in later port-53 publishing. |
| 26 | Forwarder versus authority. | Both logs identify query path; authority flag differs where applicable. |
| 27 | Wrong upstream on forwarder. | Direct authority query succeeds while forwarded query fails; repair upstream. |
| 28 | TTL/cache change using explicit resolver cache. | Observe decreasing TTL, then expiration/refresh; cache-free direct authority is control. |
| 29 | Docker name versus `quest.test` name. | Query each intended resolver explicitly; establish which system owns each name. |
| 30 | Capture the HTTP request, then deliberately use a dead port. | Successful exchange versus SYN/retry/refusal evidence, with time bound. |
| 31 | Capture DNS query and response. | Match query ID, names, ports, response code; logs alone are not packet evidence. |
| 32 | Transfer: diagnose wrong resolver, record, network, listener, or port. | One injected defect per attempt, evidence-led fix, clean reset. |

Rows 10–11 are classification checks embedded in a live two-container context; they are not fake packet demonstrations. Rows 14 and 28 require extra fixtures; defer until their cost is justified. No claim is made that route tables, NAT, or DNS caches are simulated by a plain calculator.

## Packet evidence and least-cost privileges

`tcpdump` captures on an interface or reads a saved capture; live capture may need privileges, while reading a file does not. `-p` avoids requesting promiscuous mode; `-n` avoids name-resolution distraction; bounded count and duration prevent hanging tasks. [tcpdump manual](https://www.tcpdump.org/manpages/tcpdump.1.html)

Docker documents `NET_RAW` for RAW/PACKET sockets and `NET_ADMIN` for network administration; `--privileged` grants much broader access. [Docker run capabilities](https://docs.docker.com/engine/containers/run/#runtime-privilege-and-linux-capabilities) **Inference to validate:** capture only the client's own namespace using a tools sidecar sharing it; drop capabilities and grant only the capture capability actually needed, use `tcpdump -p`, and do not mount the Docker socket. Route reading needs no route mutation. A manually constructed router/NAT lab would need extra authority and setup: defer it, rather than use privileged containers in the baseline.

Evidence levels must be explicit: (a) observed DNS/HTTP packets inside one container namespace; (b) Docker metadata describing a managed network; (c) Linux implementation documentation; (d) a pedagogical topology drawing. An inside-container capture does not prove which host NAT rule executed. To observe NAT's rewritten source requires a capture/receiver beyond the relevant translation boundary; Desktop's host backend makes this a platform-specific extension. [Desktop network overview](https://docs.docker.com/desktop/features/networking/), [Docker iptables NAT rules](https://docs.docker.com/engine/network/firewall-iptables/)

## Portability, cost, grading and reset decisions

**Recommended baseline (inference):** Docker Compose v2, Linux containers, amd64/arm64-compatible pinned images, one prebuilt client/tools image plus a tiny HTTP fixture and CoreDNS. Avoid package installation inside each lesson, Internet queries during grading, Windows-native containers, host networking, and host firewall manipulation. Download/build sizes, cold-start time, architecture availability and capture permissions remain **unmeasured** here.

Windows installation requires supported OS/WSL or Hyper-V prerequisites and hardware virtualization; current documentation specifies 8 GB RAM. [Docker Desktop Windows install](https://docs.docker.com/desktop/setup/install/windows-install/) Mac has a separate supported-platform checklist. [Docker Desktop Mac install](https://docs.docker.com/desktop/setup/install/mac-install/) Desktop licensing is free for categories including personal use and education, but organizational use may require payment. [Docker Desktop license](https://docs.docker.com/subscription-billing/desktop-license/) Docker group membership on native Linux grants root-level privileges; treat installation as a prerequisite, not an automatic course action. [Linux post-install security note](https://docs.docker.com/engine/install/linux-postinstall/)

**Grading proposal (inference):** preflight engine availability, Linux mode, Compose version, image availability, prefix overlap, free host ports and writable owned output directory. Start dependencies with health checks; ordinary start order is not readiness. [Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/) Grade bounded client commands, expected HTTP token, DNS status/RRsets/server, route-choice fields and normalized capture facts. Ignore IDs, MAC addresses, host bridge names, ephemeral source ports, precise packet timing and dynamically assigned IPs. On failure distinguish prerequisite, fixture, timeout and learner-condition failures.

**Owned teardown proposal:** use one unique course/lab project name and a manifest of its resources. Run `docker compose -p <owned-project> -f <owned-file> down`; add `--volumes` only when every declared volume is disposable lab data. Compose down removes its service containers and owned networks; external networks/volumes are excluded, and volumes are not removed by default. [Compose down](https://docs.docker.com/reference/cli/docker/compose/down/) Never use system/network/volume prune or stop unrelated resources. Store captures in the owned directory with bounded retention; do not capture other applications.

**Decisions for the main planner / human:** confirm required operating systems and existing Docker installation policy; approve the tools image distribution method and offline/cache budget; decide whether native-Linux bridge/NAT capture is optional; select the depth of binary mask arithmetic and whether manual routing gets an advanced branch; decide if 30+ units include strengthening existing lessons or are all additions. Floci/AWS progression needs its own feature evidence: Docker bridges are not VPCs, network membership is not a security group, and this note does not establish that an emulator reproduces AWS packet forwarding.
