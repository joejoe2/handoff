import os
import math
import random
import matplotlib.pyplot as plt
import copy

# 40/3.6 m/s => 600/(40/3.6)=75 => 75*4 unit/sec
unitlen = 750 / 75  # m per unit
# use [y][x] to access pre calculated power   # in unit
bs1 = []
bs2 = []
bs3 = []
bs4 = []
# bs is in format [y][x]   # in unit
#   x->
# y [[...],
#    [...],
#    ...
#    [...]]
# define direction in x,y
# 0 is (1,0) 1 is (-1,0)
# 2 is (0,1) 3 is (0,-1)
map = ["bs1", "bs2", "bs3", "bs4"]  # map file name
mappos = [[75, 75], [75 * 3, 75], [75, 75 * 3], [75 * 3, 75 * 3]]  # bs loc in (x,y)   # in unit
entry = [[0, 75, 0], [75, 0, 2], [75 * 2, 0, 2], [75 * 3, 0, 2], [75 * 4, 75, 1], [75 * 4, 75 * 2, 1], [0, 75 * 2, 0],
         [0, 75 * 3, 0],
         [75, 75 * 4, 3], [75 * 2, 75 * 4, 3
                           ], [75 * 3, 75 * 4, 3], [75 * 4, 75 * 3, 1]]  # in (x,y, direction)   # in unit
width = 75 * 4  # in unit
height = 75 * 4  # in unit
pt = -60  # first meter power in dbm
arrival_prob = (2 / 60) * math.exp(-(2 / 60))
threshold = -110  # dbm
entro = 5  # dbm
pmin = -125  # dbm


class Car:
    def __init__(self, hold, power, x, y, direction, speed=1):
        self.hold = hold
        self.power = power
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.active = True
        self.duration = 0

    def step(self):
        if not self.active:
            return

        if (self.x % 75 == 0) and (self.y % 75 == 0):
            self.turn()
        self.move()

    def turn(self):
        if self.x == 0 and self.y == 0:
            if self.direction == 3:
                self.direction = 0
            elif self.direction == 1:
                self.direction = 2
            return
        elif self.x == 0 and self.y == 75*4:
            if self.direction == 2:
                self.direction = 0
            elif self.direction == 1:
                self.direction = 3
            return
        elif self.x == 75*4 and self.y == 0:
            if self.direction == 0:
                self.direction = 2
            elif self.direction == 3:
                self.direction = 1
            return
        elif self.x == 75*4 and self.y == 75*4:
            if self.direction == 0:
                self.direction = 3
            elif self.direction == 2:
                self.direction = 1
            return

        r = random.random()
        if r < 0.5:  # no turn
            pass
        elif r < 1 / 3 + 0.5:  # turn right
            if self.direction == 0:
                self.direction = 2
            elif self.direction == 1:
                self.direction = 3
            elif self.direction == 2:
                self.direction = 1
            elif self.direction == 3:
                self.direction = 0
        else:  # turn left
            if self.direction == 0:
                self.direction = 3
            elif self.direction == 1:
                self.direction = 2
            elif self.direction == 2:
                self.direction = 0
            elif self.direction == 3:
                self.direction = 1

    def move(self):
        if self.direction == 0:
            self.x += self.speed
        elif self.direction == 1:
            self.x -= self.speed
        elif self.direction == 2:
            self.y += self.speed
        elif self.direction == 3:
            self.y -= self.speed
        # test for out bound
        if self.x < 0 or self.y < 0 or self.x > 75 * 4 or self.y > 75 * 4:
            self.active = False
        else:
            # update power
            hold = self.hold
            bs = bs1 if hold == 1 else bs2 if hold == 2 else bs3 if hold == 3 else bs4
            self.power = bs[self.y][self.x]

    def change(self, hold):
        if self.hold != hold:
            # update power
            self.hold = hold
            bs = bs1 if hold == 1 else bs2 if hold == 2 else bs3 if hold == 3 else bs4
            self.power = bs[self.y][self.x]
            self.duration = 0

    def elapse(self):
        self.duration += 1

    def __str__(self):
        return str(self.x) + " " + str(self.y)

    def __repr__(self):
        return str(self)


def setup():
    for a in range(0, 4):
        bs = bs1 if a == 0 else bs2 if a == 1 else bs3 if a == 2 else bs4
        if os.path.exists(map[a] + ".txt"):
            print("skip setup " + map[a])
            f = open(map[a] + ".txt", "r")
            for i in range(0, height + 1):
                bs.append(f.readline().split(" "))
                for j in range(0, width + 1):
                    bs[i][j] = float(bs[i][j])
            f.close()
        else:
            print("setup " + map[a])
            f = open(map[a] + ".txt", "w")
            for i in range(0, height + 1):
                bs.append([])
                for j in range(0, width + 1):
                    bs[i].append(0)
                    dis = math.sqrt((j - mappos[a][0]) ** 2 + (i - mappos[a][1]) ** 2) * unitlen
                    bs[i][j] = pt - 20 * math.log10(math.ceil(dis) / 1) if dis != 0 else pt
                    f.write(str(bs[i][j]))
                    if j < width:
                        f.write(" ")
                f.write("\n")
            f.close()


def generate(carlist1):
    l = []
    for a in range(0, 3):
        if random.random() < arrival_prob:
            x = entry[a][0]
            y = entry[a][1]
            d = entry[a][2]
            c = Car(hold=1, power=bs1[y][x], x=x, y=y, direction=d)
            carlist1.append(c)
            c = Car(hold=1, power=bs1[y][x], x=x, y=y, direction=d)
            l.append(c)
        else:
            l.append(None)
        pass
    for a in range(3, 6):
        if random.random() < arrival_prob:
            x = entry[a][0]
            y = entry[a][1]
            d = entry[a][2]
            c = Car(hold=2, power=bs2[y][x], x=x, y=y, direction=d)
            carlist1.append(c)
            c = Car(hold=2, power=bs2[y][x], x=x, y=y, direction=d)
            l.append(c)
        else:
            l.append(None)
        pass
    for a in range(6, 9):
        if random.random() < arrival_prob:
            x = entry[a][0]
            y = entry[a][1]
            d = entry[a][2]
            c = Car(hold=3, power=bs3[y][x], x=x, y=y, direction=d)
            carlist1.append(c)
            c = Car(hold=3, power=bs3[y][x], x=x, y=y, direction=d)
            l.append(c)
        else:
            l.append(None)
        pass
    for a in range(9, 12):
        if random.random() < arrival_prob:
            x = entry[a][0]
            y = entry[a][1]
            d = entry[a][2]
            c = Car(hold=4, power=bs4[y][x], x=x, y=y, direction=d)
            l.append(c)
            c = Car(hold=4, power=bs4[y][x], x=x, y=y, direction=d)
            carlist1.append(c)
        else:
            l.append(None)
        pass
    return l


def best_policy(car):
    # hand off ...
    old = car.hold
    pold = car.power
    pnew = pold
    new = old
    for a in range(0, 4):  # find p max
        bs = bs1 if a == 0 else bs2 if a == 1 else bs3 if a == 2 else bs4
        if pnew < bs[car.y][car.x]:
            pnew = bs[car.y][car.x]
            new = a + 1
    if pnew > pold or pold < pmin:  # old not the max
        car.change(new)
        return True
    else:
        return False
    pass


def threshold_policy(car):
    # hand off ...
    old = car.hold
    pold = car.power
    pnew = pold
    new = old
    for a in range(0, 4):  # find p max
        bs = bs1 if a == 0 else bs2 if a == 1 else bs3 if a == 2 else bs4
        if pnew < bs[car.y][car.x]:
            pnew = bs[car.y][car.x]
            new = a + 1
    if (pnew > pold and pold < threshold) or pold < pmin:  # old not the max and < threshold
        car.change(new)
        return True
    else:
        return False
    pass


def entropy_policy(car):
    # hand off ...
    old = car.hold
    pold = car.power
    pnew = pold
    new = old
    for a in range(0, 4):  # find p max
        bs = bs1 if a == 0 else bs2 if a == 1 else bs3 if a == 2 else bs4
        if pnew < bs[car.y][car.x]:
            pnew = bs[car.y][car.x]
            new = a + 1
    if pold + entro < pnew or pold < pmin:  # old not the max and diff entropy
        car.change(new)
        return True
    else:
        return False
    pass
    pass


def my_policy(car):
    # hand off ...
    old = car.hold
    pold = car.power
    pnew = pold
    new = old
    for a in range(0, 4):  # find p max
        bs = bs1 if a == 0 else bs2 if a == 1 else bs3 if a == 2 else bs4
        if pnew < bs[car.y][car.x]:
            pnew = bs[car.y][car.x]
            new = a + 1
    if (pnew > pold and car.duration > 75*3) or pold < pmin:  # old not the max and last ? sec
        car.change(new)
        return True
    elif pold < pnew:  # time for pold not the max
        car.elapse()
        return False
    else:
        return False
    pass
    pass


def my_policy2(car):
    # hand off ...
    old = car.hold
    pold = car.power
    pnew = pold
    new = old
    for a in range(0, 4):  # find p max
        bs = bs1 if a == 0 else bs2 if a == 1 else bs3 if a == 2 else bs4
        if pnew < bs[car.y][car.x]:
            pnew = bs[car.y][car.x]
            new = a + 1
    if pold < pmin:  # until pmin
        car.change(new)
        return True
    else:
        return False
    pass
    pass


if __name__ == '__main__':
    setup()
    img = [[], [], [], [], []]

    m = [best_policy, threshold_policy, entropy_policy, my_policy, my_policy2]
    rec = []
    total = 0
    psum = []
    for j in range(0, len(m)):
        method = m[j]
        print("start " + method.__name__)
        time = 0  # sec
        timelimit = 86400  # sec
        carlist = []
        handoff = 0
        psum.append(0)
        for i in range(0, timelimit):
            ptemp = 0
            for car in carlist:
                # add power
                ptemp += car.power
                # hand off ...
                if method(car):
                    handoff += 1
                # move and turn ...
                car.step()
            # sum power
            ptemp /= 1 if len(carlist) == 0 else len(carlist)
            psum[j] += ptemp
            # remove out cars
            carlist[:] = [x for x in carlist if x.active]
            # new cars
            if j == 0:  # first loop to build rec list
                rec.append(copy.deepcopy(generate(carlist)))
            else:  # after first loop use the same as first generating list
                for k in range(0, 12):
                    if not rec[i][k] is None:
                        carlist.append(copy.deepcopy(rec[i][k]))
                        total += 1
            # step log
            if i % 5000 == 0:
                print(str(i) + " sec car:" + str(len(carlist)) + " handoff:" + str(handoff))
            img[j].append(handoff)
        print("86400 sec car:" + str(len(carlist)) + " handoff:" + str(handoff))
        plt.plot(img[j], label=str(method.__name__))
        plt.legend(loc='upper left')
    total /= len(m)-1
    print("total car:"+str(total))
    print()
    for j in range(0, len(m)):
        method = m[j]
        print(method.__name__+" average power:"+str(psum[j]/timelimit))

    plt.xlabel("per sec")
    plt.ylabel("handoff times")
    plt.show()
