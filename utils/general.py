from math import sqrt

from space_tycoon_client.models.ship import Ship


def countDistanceShips(ship1: Ship, ship2: Ship):
    return sqrt((ship1.position[0] - ship2.position[0])**2+(ship1.position[1] - ship2.position[1])**2)