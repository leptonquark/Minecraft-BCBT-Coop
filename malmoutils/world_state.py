import time

MAX_DELAY = 60


def check_timeout(agent, world_state, last_delta):
    new_delta = time.time()
    if is_world_state_idle(world_state) and new_delta - last_delta > MAX_DELAY:
        print("Max delay exceeded for world state change")
        agent.restart_minecraft(world_state, "world state change")
    return new_delta


def is_world_state_idle(world_state):
    return world_state.number_of_video_frames_since_last_state == 0 \
           and world_state.number_of_observations_since_last_state == 0 \
           and world_state.number_of_rewards_since_last_state == 0
