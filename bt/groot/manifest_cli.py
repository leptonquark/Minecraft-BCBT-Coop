"""CLI: refresh a TreeNodesModel XML from the live registry.

    python -m bt.groot.manifest_cli trees/nodes_model.xml
"""
import sys

from bt.groot.manifest import write


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        print(__doc__)
        return 2
    write(argv[0])
    print(f"Wrote {argv[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
