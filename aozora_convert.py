#!/usr/bin/env python3

import argparse
import re
from pathlib import Path
from typing import Dict

GT = Dict[str, str]


'''
https://qiita.com/kichiki/items/bb65f7b57e09789a05ce
'''


def get_gaiji_table(fpath: Path) -> GT:
    with fpath.open() as f:
        ms = (re.match(r"(\d-\w{4})\s+U\+(\w{4})", li) for li in f if li[0] != "#")
        gaiji_table = {m[1]: chr(int(m[2], 16)) for m in ms if m}
    return gaiji_table


def get_gaiji(s: str, gaiji_table: GT) -> str:
    # ※［＃「弓＋椁のつくり」、第3水準1-84-22］
    m = re.search(r"第(\d)水準\d-(\d{1,2})-(\d{1,2})", s)
    if m:
        key = f"{m[1]}-{int(m[2])+32:2X}{int(m[3])+32:2X}"
        return gaiji_table.get(key, s)
    # ※［＃「身＋單」、U+8EC3、56-1］
    m = re.search(r"U\+(\w{4})", s)
    if m:
        return chr(int(m[1], 16))
    # unknown format
    return s


def replace_gaiji(text: str, gt: GT) -> str:
    return re.sub(r"※［＃.+?］", lambda m: get_gaiji(m[0], gt), text)


def operation(path_in: Path, path_out: Path, path_gaiji: Path) -> None:
    gt = get_gaiji_table(path_gaiji)

    with path_in.open() as inf, path_out.open("w") as outf:
        for line in inf:
            ol: str = replace_gaiji(line, gt)
            ol = re.sub(r"［[^］]*］", "", ol)
            ol = re.sub(r"《[^》]*》", "", ol)
            ol = re.sub(r"^\s*", "", ol)
            outf.write(ol)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    oparser.add_argument(
        "--gaiji",
        type=Path,
        default=Path(__file__).parent.joinpath("jisx0213-2004-std.txt"),
    )
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()

    operation(opts.input, opts.output, opts.gaiji)


if __name__ == "__main__":
    main()
