import gym
import sys
import os
import copy
from gym import spaces
import numpy as np
import matplotlib.pyplot as plt

EMPTY = BLACK = 0
WALL = GRAY = 1
BLUE = 2
TARGET = GREEN = 3
AGENT = RED = 4
SUCCESS = PINK = 6
YELLOW = 7
COLORS = {BLACK: [0.0, 0.0, 0.0], GRAY: [0.5, 0.5, 0.5],
          BLUE: [0.0, 0.0, 1.0], GREEN: [0.0, 1.0, 0.0],
          RED: [1.0, 0.0, 0.0], PINK: [1.0, 0.0, 1.0],
          YELLOW: [1.0, 1.0, 0.0]}

NOOP = 0
DOWN = 1
UP = 2
LEFT = 3
RIGHT = 4


class GridworldEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    num_env = 0

    def __init__(self, plan):
        self.actions = [NOOP, DOWN, UP, LEFT, RIGHT]
        self.inv_actions = [0, 2, 1, 4, 3]
        self.action_space = spaces.Discrete(5)
        self.action_pos_dict = {NOOP: [0, 0], DOWN: [-1, 0], UP: [1, 0], LEFT: [0, -1], RIGHT: [0, 1]}

        # set observation space
        self.obs_shape = [128, 128, 3]  # observation space shape
        self.observation_space = spaces.Box(low=0, high=1, shape=self.obs_shape)

        # initialize system state
        this_file_path = os.path.dirname(os.path.realpath(__file__))
        self.grid_map_path = os.path.join(this_file_path, 'plan{}.txt'.format(plan))
        self.start_grid_map = self._read_grid_map(self.grid_map_path)  # initial grid map
        self.current_grid_map = copy.deepcopy(self.start_grid_map)  # current grid map
        self.observation = self._gridmap_to_observation(self.start_grid_map)
        self.grid_map_shape = self.start_grid_map.shape

        # agent state: start, target, current state
        self.agent_start_state, self.agent_target_state = self._get_agent_start_target_state()
        self.agent_state = copy.deepcopy(self.agent_start_state)

        # set other parameters
        self.restart_once_done = False  # restart or not once done
        self.verbose = True  # to show the environment or not

        GridworldEnv.num_env += 1
        self.this_fig_num = GridworldEnv.num_env
        if self.verbose:
            self.fig = plt.figure(self.this_fig_num)
            plt.show(block=False)
            plt.axis('off')
            self._render()

    def _step(self, action):
        """ return next observation, reward, finished, success """
        action = int(action)
        info = {'success': False}
        nxt_agent_state = (self.agent_state[0] + self.action_pos_dict[action][0],
                           self.agent_state[1] + self.action_pos_dict[action][1])

        if action == NOOP:
            info['success'] = True
            return self.observation, 0, False, info
        next_state_out_of_map = (nxt_agent_state[0] < 0 or nxt_agent_state[0] >= self.grid_map_shape[0]) or \
                                (nxt_agent_state[1] < 0 or nxt_agent_state[1] >= self.grid_map_shape[1])
        if next_state_out_of_map:
            info['success'] = False
            return self.observation, 0, False, info

        # successful behavior
        target_position = self.current_grid_map[nxt_agent_state[0], nxt_agent_state[1]]

        if target_position == EMPTY:
            self.current_grid_map[self.agent_state[0], self.agent_state[1]] = EMPTY
            self.current_grid_map[nxt_agent_state[0], nxt_agent_state[1]] = AGENT
            self.agent_state = copy.deepcopy(nxt_agent_state)
        elif target_position == WALL:
            info['success'] = False
            return self.observation, 0, False, info
        elif target_position == TARGET:
            self.current_grid_map[self.agent_state[0], self.agent_state[1]] = EMPTY
            self.current_grid_map[nxt_agent_state[0], nxt_agent_state[1]] = SUCCESS
            self.agent_state = copy.deepcopy(nxt_agent_state)

        self.observation = self._gridmap_to_observation(self.current_grid_map)
        self._render()

        if nxt_agent_state[0] == self.agent_target_state[0] and nxt_agent_state[1] == self.agent_target_state[1]:
            target_observation = copy.deepcopy(self.observation)
            if self.restart_once_done:
                self.observation = self._reset()
                info['success'] = True
                return self.observation, 1, True, info
            else:
                info['success'] = True
                return target_observation, 1, True, info
        else:
            info['success'] = True
            return self.observation, 0, False, info

    def _reset(self):
        self.agent_state = copy.deepcopy(self.agent_start_state)
        self.current_grid_map = copy.deepcopy(self.start_grid_map)
        self.observation = self._gridmap_to_observation(self.start_grid_map)
        self._render()
        return self.observation

    def _read_grid_map(self, grid_map_path):
        grid_map = open(grid_map_path, 'r').readlines()
        grid_map_array = []
        for k1 in grid_map:
            k1s = k1.split(' ')
            tmp_arr = []
            for k2 in k1s:
                try:
                    tmp_arr.append(int(k2))
                except:
                    pass
            grid_map_array.append(tmp_arr)
        grid_map_array = np.array(grid_map_array)
        return grid_map_array

    def _get_agent_start_target_state(self):
        start_state = np.where(self.start_grid_map == AGENT)
        target_state = np.where(self.start_grid_map == TARGET)

        start_or_target_not_found = not(start_state[0] and target_state[0])
        if start_or_target_not_found:
            sys.exit('Start or target state not specified')
        start_state = (start_state[0][0], start_state[1][0])
        target_state = (target_state[0][0], target_state[1][0])

        return start_state, target_state

    def _gridmap_to_observation(self, grid_map, obs_shape=None):
        if obs_shape is None:
            obs_shape = self.obs_shape
        observation = np.random.randn(*obs_shape) * 0.0
        gs0 = int(observation.shape[0] / grid_map.shape[0])
        gs1 = int(observation.shape[1] / grid_map.shape[1])
        for i in range(grid_map.shape[0]):
            for j in range(grid_map.shape[1]):
                for k in range(3):
                    this_value = COLORS[grid_map[i, j]][k]
                    observation[i * gs0:(i + 1) * gs0, j * gs1:(j + 1) * gs1, k] = this_value
        return observation

    def _render(self, mode='human', close=False):
        if not self.verbose:
            return
        img = self.observation
        fig = plt.figure(self.this_fig_num)
        plt.clf()
        plt.imshow(img)
        fig.canvas.draw()
        plt.pause(0.00001)
        return

    def change_start_state(self, sp):
        """ change agent start state
            Input: sp: new start state
         """
        if self.agent_start_state[0] == sp[0] and self.agent_start_state[1] == sp[1]:
            _ = self._reset()
            return True
        elif self.start_grid_map[sp[0], sp[1]] != EMPTY:
            raise ValueError('Cannot move start position to occupied cell')
        else:
            s_pos = copy.deepcopy(self.agent_start_state)
            self.start_grid_map[s_pos[0], s_pos[1]] = EMPTY
            self.start_grid_map[sp[0], sp[1]] = AGENT
            self.current_grid_map = copy.deepcopy(self.start_grid_map)
            self.agent_start_state = [sp[0], sp[1]]
            self.observation = self._gridmap_to_observation(self.current_grid_map)
            self.agent_state = copy.deepcopy(self.agent_start_state)
            self._reset()
            self._render()
        return True

    def change_target_state(self, tg):
        if self.agent_target_state[0] == tg[0] and self.agent_target_state[1] == tg[1]:
            _ = self._reset()
            return True
        elif self.start_grid_map[tg[0], tg[1]] != EMPTY:
            raise ValueError('Cannot move target position to occupied cell')
        else:
            t_pos = copy.deepcopy(self.agent_target_state)
            self.start_grid_map[t_pos[0], t_pos[1]] = EMPTY
            self.start_grid_map[tg[0], tg[1]] = TARGET
            self.current_grid_map = copy.deepcopy(self.start_grid_map)
            self.agent_target_state = [tg[0], tg[1]]
            self.observation = self._gridmap_to_observation(self.current_grid_map)
            self.agent_state = copy.deepcopy(self.agent_start_state)
            self._reset()
            self._render()
        return True

    def _close_env(self):
        plt.close(1)
        return

    @staticmethod
    def get_action_meaning():
        return ['NOOP', 'DOWN', 'UP', 'LEFT', 'RIGHT']
