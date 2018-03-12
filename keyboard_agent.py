#!/usr/bin/env python
from __future__ import print_function

import sys, gym
from pyglet.window import key

import gym_gridworld
from gym_gridworld.envs.gridworld_env import UP, DOWN, LEFT, RIGHT, NOOP
#
# Test yourself as a learning agent! Pass environment name as a command-line argument.
#

env = gym.make('SequentialGridworldStochastic-v0' if len(sys.argv) < 2 else sys.argv[1])

if not hasattr(env.action_space, 'n'):
    raise Exception('Keyboard agent only supports discrete action spaces')
ACTIONS = env.action_space.n
ROLLOUT_TIME = 1000
SKIP_CONTROL = 0  # Use previous control decision SKIP_CONTROL times, that's how you
# can test what skip is still usable.

human_action = 0
human_wants_restart = False
human_sets_pause = False


def key_press(k, mod):
    global human_action, human_wants_restart, human_sets_pause
    human_action = NOOP

    if k == key.R: human_wants_restart = True
    if k == key.LEFT: human_action = LEFT
    if k == key.RIGHT: human_action = RIGHT
    if k == key.UP: human_action = UP
    if k == key.DOWN: human_action = DOWN


def key_release(k, mod):
    global human_action
    human_action = NOOP

    # if k == key.LEFT: human_action = LEFT
    # if k == key.RIGHT: human_action = RIGHT
    # if k == key.UP: human_action = UP
    # if k == key.DOWN: human_action = DOWN


env.render()
env.unwrapped.viewer.window.on_key_press = key_press
env.unwrapped.viewer.window.on_key_release = key_release


def rollout(env):
    global human_action, human_wants_restart, human_sets_pause
    human_wants_restart = False
    obser = env.reset()
    skip = 0
    for t in range(ROLLOUT_TIME):
        if not skip:
            # print("taking action {}".format(human_agent_action))
            a = human_action
            skip = SKIP_CONTROL
        else:
            skip -= 1

        obser, r, done, info = env.step(human_action)
        print('Reward = {}'.format(r))
        env.render()
        if done: break
        if human_wants_restart: break
        while human_sets_pause:
            env.render()
            import time
            time.sleep(0.1)


print("ACTIONS={}".format(ACTIONS))
print("Press keys 1 2 3 ... to take actions 1 2 3 ...")
print("No keys pressed is taking action 0")

while 1:
    rollout(env)
