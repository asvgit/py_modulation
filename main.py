"""
Carwash example.
"""
import simpy
import random
import datetime
import os


RANDOM_SEED = 42
NUM_MACHINES = 2  # Number of machines in the carwash
WASHTIME = 5      # Minutes it takes to clean a car
T_INTER = 7       # Create a car every ~7 minutes
SIM_TIME = 20     # Simulation time in minutes
LOGFILE = 'project.log'

def info(message, env = None):
    now = datetime.datetime.now()
    time = 'null'
    if env is not None :
        time = '%.2f' % (env.now)
    file = open(LOGFILE, 'a')
    #  file.write('%s %s\n' % (NOW.strftime("%Y-%m-%d %H:%M"), message))
    file.write('%s [%s:%s] %s\n' % (now.strftime("%d %b %Y %X"), os.getpid(), time, message))
    file.close()

class Carwash(object):
    def __init__(self, env, num_machines, washtime):
        self.env = env
        self.machine = simpy.Resource(env, num_machines)
        self.washtime = washtime

    def wash(self, car):
        yield self.env.timeout(WASHTIME)
        info("Carwash removed %d%% of %s's dirt." %
              (random.randint(50, 99), car), self.env)


def car(env, name, cw):
    info('%s arrives at the carwash at %.2f.' % (name, env.now), env)
    with cw.machine.request() as request:
        yield request

        info('%s enters the carwash at %.2f.' % (name, env.now), env)
        yield env.process(cw.wash(name))

        info('%s leaves the carwash at %.2f.' % (name, env.now), env)


def setup(env, num_machines, washtime, t_inter):
    # Create the carwash
    carwash = Carwash(env, num_machines, washtime)

    #  Create 4 initial cars
    for i in range(4):
        env.process(car(env, 'Car %d' % i, carwash))

    # Create more cars while the simulation is running
    while True:
        yield env.timeout(random.randint(t_inter - 2, t_inter + 2))
        i += 1
        env.process(car(env, 'Car %d' % i, carwash))


# Setup and start the simulation
info('Carwash')
info('Check out http://youtu.be/fXXmeP9TvBg while simulating ... ;-)')
random.seed(RANDOM_SEED)  # This helps reproducing the results

# Create an environment and start the setup process
env = simpy.Environment()
env.process(setup(env, NUM_MACHINES, WASHTIME, T_INTER))

# Execute!
env.run(until=SIM_TIME)
info('Session end')
