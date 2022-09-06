from math import sqrt

from space_tycoon_client.models.ship import Ship
from utils.patterns import Singleton
import logging


logger = logging.getLogger(__name__)


def countDistanceShips(ship1: Ship, ship2: Ship):
    extra = 0  # Hack to prefer fighters over motherships
    if "ship_class" in ship2.__dict__.keys() and ship2.ship_class == "1":
        extra = 10
    return sqrt((ship1.position[0] - ship2.position[0])**2+(ship1.position[1] - ship2.position[1])**2) + extra


class SharedComms(metaclass=Singleton):
    def __init__(self):
        self._galaxy_at_peace = False
        self.mothership_distance_from_enemies = 1
        self.past_mothership_positions = []

    @property
    def galaxy_at_peace(self) -> bool:
        return self._galaxy_at_peace

    @galaxy_at_peace.setter
    def galaxy_at_peace(self, value: bool):
        if self._galaxy_at_peace != value:
            logger.info(f"Galaxy {'at peace' if value else 'at war'}!")
        self._galaxy_at_peace = value
