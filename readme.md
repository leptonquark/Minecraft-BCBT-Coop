# Malmo Behaviour Trees — Groot2 edition

Single-agent Malmo behaviour trees authored visually in
[Groot2](https://www.behaviortree.dev/groot/) and executed in Python via
`py-trees`. Groot2 doubles as a live monitor for the running tree.

Layout:

- `bt/groot/` — XML loader + registry + Groot2 monitor publisher.
- `trees/` — Groot2-authored tree XMLs and a `TreeNodesModel` palette.
- `main.py` — the single entry point.

## Install

```sh
pip install -r requirements.txt
```

Install Groot2 from the [official site](https://www.behaviortree.dev/groot/)
(prebuilt binaries for macOS / Linux / Windows).

## Author a tree

1. Open Groot2.
2. Import the node palette: **File → Import → `trees/nodes_model.xml`**
   (or paste the `<TreeNodesModel>` block into a fresh tree file).
3. Drag Actions / Conditions onto the canvas, fill in the input ports
   (e.g. `MineMaterial.material = "log2"`), save as XML under `trees/`.

The reference demo is `trees/demo_gather_wood.xml` — a reactive loop that
travels to logs and chops until the inventory holds five.

## Run

```sh
python main.py --mission g10spmdw --tree trees/demo_gather_wood.xml
```

`--mission` selects a world setup from `experiment/experiments.py` (mission id,
*not* the tree). `g10spmdw` is the manual test arena that pre-spawns log and
stone cuboids the agent can reach.

## Monitor live

While `main.py` is running:

1. In Groot2 open **Monitor** mode.
2. Connect to `tcp://localhost:1667`.
3. Groot2 fetches the running tree (the exact XML you authored) and lights up
   each node with its current status (`RUNNING` / `SUCCESS` / `FAILURE` / `IDLE`)
   as the agent acts in-world.

Change the port with `--groot-port 4242` (Groot2 also connects to the PUB
socket at `port + 1` automatically).

## Refresh the node palette

If you add a new Action / Condition class and register it in
`bt/groot/registry.py`, regenerate the palette so Groot2 sees it:

```sh
python -m bt.groot.manifest_cli trees/nodes_model.xml
```

## Known limitations

- The Groot2 protocol implementation is intentionally minimal — FULLTREE,
  STATUS, and BLACKBOARD requests work; breakpoints / hooks are accepted but
  no-ops.
- `<SubTree>` references are not yet supported by the loader.
- Decorator semantics (`Retry`, `Repeat`) follow `py_trees` and may differ in
  edge cases from BehaviorTree.CPP's reference implementation.
