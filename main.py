import simpy
import random
import datetime
import os

LOGFILE = 'project.log'
T_INTER = 5
SIM_TIME = 40
NUM_FLOORS = 30

def info(message, env = None):
    now = datetime.datetime.now()
    time = 'null'
    if env is not None :
        time = '%.2f' % (env.now)
    file = open(LOGFILE, 'a')
    #  file.write('%s %s\n' % (NOW.strftime("%Y-%m-%d %H:%M"), message))
    file.write('%s [%s:%s] %s\n'
               % (now.strftime("%d %b %Y %X"), os.getpid(), time, message))
    file.close()

class Man:
    def __init__(self, ind):
        self.name = 'Man %d' % ind
        self.floor = random.randint(0, NUM_FLOORS // 2)
        self.target = self.floor
        while (self.target == self.floor):
            self.target = random.randint(0, NUM_FLOORS)
        info('%s appears on floor \'%s\' with target \'%s\''
             % (self.name, self.floor, self.target), env)

class Cabine(object):
    def __init__(self):
        self.state = 0
        self.floor = 0

class Elevator(object):
    def __init__(self, env, num_machines):
        self.env = env
        self.cab = simpy.Resource(env, num_machines)
        self.cabs = [Cabine() for i in range(num_machines)]
        self.n_cabs = num_machines

    def get_free_cab(self):
        for i in range(self.n_cabs):
            if (self.cabs[i].state == 0):
                return i

    def moving(self, man):
        cid = self.get_free_cab()
        self.cabs[cid].state = 1
        moving_time = abs(man.target - man.floor)
        waiting = abs(man.floor - self.cabs[cid].floor) + moving_time
        yield self.env.timeout(waiting)
        self.cabs[cid].state = 0
        info('%s has reached by Cab %d' % (man.name, cid), env)

def call(env, ind, elev):
    man = Man(ind)
    with elev.cab.request() as request:
        yield request
        info('%s is moving' % (man.name), env)
        yield env.process(elev.moving(man))

def people_generator(env):
    elev = Elevator(env, 2);
    i = 0
    env.process(call(env, i, elev))
    while True:
        yield env.timeout(random.randint(T_INTER - 2, T_INTER + 2))
        i += 1
        env.process(call(env, i, elev))

info('Start session')
env = simpy.Environment()
env.process(people_generator(env))
env.run(until=SIM_TIME)
info('Session end')
