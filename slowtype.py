import sys
import time
import random

def slow_type(t,typing_speed=500,random_speed=True):
    for l in t:
        sys.stdout.write(l)
        sys.stdout.flush()
        if random_speed:
            time.sleep(random.random()*10.0/typing_speed)
        else:
            time.sleep(10.0/typing_speed)
    print('')