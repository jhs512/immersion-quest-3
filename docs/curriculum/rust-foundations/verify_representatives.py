"""Compile and execute review drafts; never change production course content."""

import json
import platform
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "representatives"
results = []


def check(name, source, output=None, error=None, reject=False):
    with tempfile.TemporaryDirectory(prefix="mq-rust-draft-") as temp:
        folder = Path(temp)
        code = folder / "main.rs"
        binary = folder / ("program.exe" if platform.system() == "Windows" else "program")
        code.write_text(source, encoding="utf-8")
        built = subprocess.run(
            ["rustc", "--edition=2024", str(code), "-o", str(binary)],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
        if error:
            ok = built.returncode != 0 and error in built.stderr
            actual = error if ok else built.stderr
        else:
            if built.returncode != 0:
                raise AssertionError(f"{name}: {built.stderr}")
            run = subprocess.run(
                [str(binary)], capture_output=True, text=True,
                encoding="utf-8", timeout=5,
            )
            actual = run.stdout
            ok = run.returncode == 0 and (actual != output if reject else actual == output)
        results.append({"case": name, "passed": ok, "actual": actual})
        if not ok:
            raise AssertionError(f"{name}: expected {output or error!r}, got {actual!r}")


def source(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


def main():
    version = subprocess.check_output(["rustc", "--version"], text=True).strip()
    check("R1 starter immutable reassignment", source("01-values-starter.rs"), error="E0384")
    check("R2 starter boundary", source("02-flow-starter.rs"), "3000\n")
    check("R3 starter moved value", source("03-ownership-starter.rs"), error="E0382")
    check("R4 starter missing item", source("04-data-starter.rs"), "가격: 0\n")

    values = source("01-values-solution.rs")
    check("R1 solution", values, "남은 수량: 3\n")
    check("R1 changed initial stock", values.replace("stock = 5", "stock = 8"), "남은 수량: 6\n")
    flow = source("02-flow-solution.rs")
    for total, fee in [(29999, 3000), (30000, 0), (30001, 0)]:
        check(f"R2 solution total={total}", flow.replace("shipping(30_000)", f"shipping({total})"), f"{fee}\n")
    ownership = source("03-ownership-solution.rs")
    check("R3 solution", ownership, "MQ\nMQ\n")
    check("R3 changed title", ownership.replace('"MQ"', '"Rust"'), "Rust\nRust\n")
    data = source("04-data-solution.rs")
    for index, expected in [(0, "가격: 1200\n"), (1, "가격: 1800\n"), (2, "상품 없음\n")]:
        check(f"R4 solution index={index}", data.replace("index: usize = 2", f"index: usize = {index}"), expected)
    check("R4 zero price exists", data.replace("1200, 1800", "0, 1800").replace("index: usize = 2", "index: usize = 0"), "가격: 0\n")
    check("Reject hardcoded stock", values.replace("stock = 5", "stock = 8").replace('println!("남은 수량: {stock}")', 'println!("남은 수량: 3")'), "남은 수량: 6\n", reject=True)
    check("Reject free shipping for every price", flow.replace("shipping(30_000)", "shipping(29999)").replace("if total >= 30_000 { 0 } else { 3000 }", "0"), "3000\n", reject=True)
    check("Reject missing item for valid index", data.replace("index: usize = 2", "index: usize = 0").replace('Some(price) => println!("가격: {price}")', 'Some(_price) => println!("상품 없음")'), "가격: 1200\n", reject=True)
    print(json.dumps({"platform": platform.platform(), "rustc": version, "passed": len(results), "cases": results}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
