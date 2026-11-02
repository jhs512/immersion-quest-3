# One image runs, grades and traces C++ and Rust on Windows, so the trace sees the binary the grader ran.
# Base: official Docker Hub rust image (Debian trixie), pinned by index digest. Tools: Debian trixie apt.
FROM rust:1.95.0-slim-trixie@sha256:28846ec5a6bcfcddb93f403ba7071bd579787852b2f2ac3839965620e8bd9456
RUN apt-get update \
 && apt-get install -y --no-install-recommends clang-19 lldb-19 python3-lldb-19 python3 libstdc++-14-dev \
 && rm -rf /var/lib/apt/lists/* \
 && ln -s /usr/bin/clang++-19 /usr/local/bin/clang++ \
 && ln -s /usr/bin/lldb-19 /usr/local/bin/lldb \
 && useradd --create-home --uid 1000 learner
USER learner
WORKDIR /work
