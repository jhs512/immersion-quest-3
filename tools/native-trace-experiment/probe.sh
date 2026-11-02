#!/bin/sh
# Inside the container or on macOS: compile fixtures with debug info only, dump raw LLDB view.
set -eu
case_dir=$1
cd "$case_dir"
sysroot=$(rustc --print sysroot)
rustc --edition 2021 -g -C opt-level=0 -o ownership ownership.rs
clang++ -std=c++17 -g -O0 -o lifetime lifetime.cpp
${LLDB:-lldb} -b -Q -o "command script import $case_dir/probe_lldb.py" -o "mq-probe $case_dir lifetime lifetime.cpp" > lldb-cpp.log 2>&1 || echo "cpp lldb exit $?"
${LLDB:-lldb} -b -Q -o "command script import $case_dir/probe_lldb.py" -o "mq-probe $case_dir ownership ownership.rs" > lldb-rust-raw.log 2>&1 || echo "rust raw exit $?"
mv probe-ownership.rs.json probe-ownership.rs.raw.json
${LLDB:-lldb} -b -Q -o "command script import $sysroot/lib/rustlib/etc/lldb_lookup.py" -o "command source -s 1 $sysroot/lib/rustlib/etc/lldb_commands" \
  -o "command script import $case_dir/probe_lldb.py" -o "mq-probe $case_dir ownership ownership.rs" > lldb-rust-fmt.log 2>&1 || echo "rust fmt exit $?"
./ownership > graded-rust.txt; ./lifetime > graded-cpp.txt
echo done
