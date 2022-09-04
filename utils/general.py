from math import sqrt

from space_tycoon_client.models.ship import Ship


def countDistanceShips(ship1: Ship, ship2: Ship):
    return sqrt(
        (ship.position[0] - planet.position[0])**2
        (ship.position[1] - planet.position[1])**2
    )