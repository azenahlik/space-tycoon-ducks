from math import sqrt

from space_tycoon_client.models.ship import Ship


def countDistanceShips(ship1: Ship, ship2: Ship):
    extra = 0  # Hack to prefer fighters over motherships
    if "ship_class" in ship2.__dict__.keys() and ship2.ship_class == "1":
        extra = 10
    return sqrt((ship1.position[0] - ship2.position[0])**2+(ship1.position[1] - ship2.position[1])**2) + extra