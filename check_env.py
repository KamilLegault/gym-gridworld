import time

import gym
import gym_gridworld
import matplotlib.pyplot as plt
from gym_gridworld.envs.gridworld_env import NOOP, UP, DOWN, LEFT, RIGHT

plt.interactive(True)

# env = gym.make('Gridworld4-v0')
env = gym.make('Gridworld1Stochastic-v0')
# env = gym.make('SequentialGridworldStochastic-v0')
state = env.reset()
env.seed(0)

# actions = [RIGHT, RIGHT, RIGHT, RIGHT, DOWN, DOWN, DOWN, LEFT, LEFT, LEFT, LEFT, ]
start = time.time()
for i in range(10000):
    # state, reward, done, info = env.step(actions[i % len(actions)])
    state, reward, done, info = env.step(env.action_space.sample())
    env.render('human')
    if done or i % 60 == 0:
        end = time.time()
        print('avg_episode time = {}'.format(end - start))
        start = time.time()
        state = env.reset()
