from random import random

with open('random.txt', 'w') as f:
    for k in range(1000000):
        print('{:6f}'.format(random()), file=f)
