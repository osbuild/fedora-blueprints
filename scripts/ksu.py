#!/usr/bin/env python3
"""
`ksu` or `kickstart utilities` is a script to inspect the
[fedora kickstarts](https://pagure.io/fedora-kickstarts/) repository or any
other collection of kickstart files.

It can turn that collection into a graphviz `.dot` file to see relationships
between the different kickstart files, it can report kickstarts that are
unused, and it can try to find the set intersection between all kickstart
files to determine the "base system", plus some other tidbits.

`ksu` requires Python 3.9 or higher.
"""

import argparse
import io
import itertools
import logging
import pathlib
import sys
from typing import Any

"""
Copyright 2023 Simon de Vlieger <cmdr@supakeen.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished
to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


log = logging.getLogger(__name__)


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        epilog="Copyright 2023 Simon de Vlieger <cmdr@supakeen.com>",
    )

    parser.add_argument(
        "-v",
        action="count",
        default=0,
        help="verbosity, pass multiple times to set level.",
    )

    subparsers = parser.add_subparsers(dest="subparser_name")

    graph_parser = subparsers.add_parser(
        "graph", description=main_graph.__doc__
    )
    graph_parser.add_argument("directory")

    return parser.parse_args(args)


def parse_kickstart(path: pathlib.Path) -> dict[str, Any]:
    data: dict[str, list[pathlib.Path]] = {"includes": []}
    text = path.read_text()

    for line in text.splitlines():
        if line.startswith("%include"):
            _, include = line.split()
            include_path = (path.parent / pathlib.Path(include)).resolve()

            if not include_path.exists():
                log.warning(
                    "%s includes %s, which does not exist", path, include_path
                )

            data["includes"].append(include_path)

    return data


def main_graph(args: argparse.Namespace) -> int:
    """Output a `.dot` format graph for the kickstarts in a given
    directory. The `.dot` file can be used with the `dot` program to generate
    an image: `./ksu.py graph ~/kickstarts | dot -Ksfdp -Tpng -o graph.png`"""

    assert args.subparser_name == "graph"

    path = pathlib.Path(args.directory).resolve()

    if not path.exists():
        log.fatal("path %s does not exist", path)
        return 1

    if not path.is_dir():
        log.fatal("path %s is not a directory", path)
        return 1

    paths = path.glob("**/*.ks")

    graph: dict[pathlib.Path, list[pathlib.Path]] = {}

    for kickstart_path in paths:
        log.debug("parsing kickstart file at %s", kickstart_path)

        data = parse_kickstart(kickstart_path)

        log.info("%s has %d includes", kickstart_path, len(data["includes"]))

        graph[kickstart_path] = data["includes"]

    # while we're at it, let's create a reverse graph as well
    rgraph: dict[pathlib.Path, list[pathlib.Path]] = {}

    for node, edges in graph.items():
        if node not in rgraph:
            rgraph[node] = []

        for edge in edges:
            if edge not in rgraph:
                rgraph[edge] = [node]
            else:
                rgraph[edge] += [node]

    # generate `.dot` file format for graphfiz
    file = io.StringIO()
    file.write("digraph {\n")

    # first we write down all the nodes, we shorten the paths by making them
    # relative to the initial path containing them so the names are a bit
    # shorter

    # get a set of unique nodes
    nodes = (
        set(itertools.chain.from_iterable(graph.values()))
        | set(graph.keys())
    )

    for node in nodes:
        node_text = node.relative_to(path)
        file.write("  " + f'"{node_text}"')

        opts = {}

        # references to non-existent kickstart files can be colored
        # differently
        if not node.exists():
            opts["style"] = "filled"
            opts["fillcolor"] = "#DD0000"

        # if a node includes nothing we give it a different shape
        if node in graph and not len(graph[node]):
            opts["shape"] = "diamond"

        # if a node isn't included by anything this is likely an end
        # and we color it differently to make it stand out
        if node in rgraph and not len(rgraph[node]):
            opts["penwidth"] = "5"

        if opts:
            file.write(" [")
            file.write(",".join(f'{key}="{val}"' for key, val in opts.items()))
            file.write("]")

        file.write(";\n")

    file.write("\n")

    for node, edges in graph.items():
        node = node.relative_to(path)

        for edge in edges:
            edge = edge.relative_to(path)

            file.write("  " + f'"{node}" -> "{edge}";\n')

    file.write("}\n")

    print(file.getvalue(), end="")

    return 0


def main() -> int:
    args = parse_args(sys.argv[1:])

    logging.basicConfig(level=logging.FATAL - (10 * args.v))

    if args.subparser_name == "graph":
        return main_graph(args)

    # should be unreachable
    return -1


if __name__ == "__main__":
    raise SystemExit(main())


# SPDX-FileType: SOURCE
# SPDX-FileCopyRightText: Copyright 2023 Simon de Vlieger <cmdr@supakeen.com>

# SPDX-License-Identifier: MIT

# vi:sw=4:ts=4:et:
