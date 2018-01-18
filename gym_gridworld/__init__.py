from gym.envs.registration import register

for i in range(10):
    register(
        id='gridworld{}-v0'.format(i),
        kwargs={'plan': i},
        entry_point='gym_gridworld.envs:GridworldEnv',
    )
