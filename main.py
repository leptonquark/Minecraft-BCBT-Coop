"""Single-agent Malmo runner driven by a Groot2-authored behaviour tree XML.

Usage:
    python main.py --mission <experiment_id> --tree trees/<file>.xml

Pair with Groot2 connected to tcp://localhost:1667 to monitor the tree live.
"""
import argparse
import signal
import sys
import time

from bt.groot.loader import load_tree
from bt.groot.publisher import Groot2Publisher
from bt.groot.registry import LoadContext


def _pick_experiment(experiment_id: str):
    from experiment.experiments import configurations

    for cfg in configurations:
        if cfg.id == experiment_id:
            return cfg
    available = ", ".join(c.id for c in configurations)
    raise SystemExit(f"Unknown mission {experiment_id!r}. Available: {available}")


def _build_mission(experiment_id: str, force_reset: bool):
    from world.missiondata import MissionData

    config = _pick_experiment(experiment_id)
    return MissionData(config, cooperativity=None, reset=force_reset, n_agents=1)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mission", required=True, help="Experiment id from experiment/experiments.py")
    parser.add_argument("--tree", required=True, help="Path to Groot2-authored tree XML")
    parser.add_argument("--groot-port", type=int, default=1667, help="Groot2 monitor REP port (PUB binds to port+1)")
    parser.add_argument("--no-reset", action="store_true", help="Skip force world reset")
    parser.add_argument("--tick-hz", type=float, default=10.0, help="Tree tick frequency")
    args = parser.parse_args(argv)

    from malmoutils.agent import MinerAgent
    from malmoutils.minecraft import set_mamo_xsd_path
    from world.observation import Observation

    set_mamo_xsd_path()

    mission_data = _build_mission(args.mission, force_reset=not args.no_reset)
    agent = MinerAgent(mission_data, blackboard={}, role=0)

    ctx = LoadContext(agent=agent)
    root, uid_table, tree_xml = load_tree(args.tree, ctx)
    root.setup_with_descendants()
    print(f"Loaded tree {args.tree!r} with {len(uid_table)} nodes")

    publisher = Groot2Publisher(tree_xml, uid_table, port=args.groot_port)
    publisher.start()
    print(f"Groot2 monitor listening on tcp://localhost:{args.groot_port}")

    stopping = {"flag": False}

    def _shutdown(_signum, _frame):
        stopping["flag"] = True

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        print(f"Starting mission {args.mission!r} ...")
        agent.start_mission()
        period = 1.0 / max(args.tick_hz, 0.1)
        while not stopping["flag"]:
            world_state = agent.get_next_world_state()
            if world_state is None:
                print("World state timeout; ending run.")
                break
            if not world_state.is_mission_running:
                print("Mission ended.")
                break
            observation = Observation(world_state.observations, mission_data)
            agent.set_observation(observation)
            if agent.observer is None:
                continue
            root.tick_once()
            time.sleep(period)
    finally:
        publisher.stop()
        try:
            agent.quit()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
