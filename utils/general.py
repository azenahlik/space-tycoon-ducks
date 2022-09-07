from math import sqrt

from space_tycoon_client.models.ship import Ship
from utils.patterns import Singleton
import logging
from space_tycoon_client.models.data import Data


logger = logging.getLogger(__name__)


def count_distance_between_positions(positionA, positionB):
    return sqrt((positionA[0] - positionB[0])**2+(positionA[1] - positionB[1])**2)

def countDistanceShips(ship1: Ship, ship2: Ship):
    extra = 0  # Hack to prefer fighters over motherships
    if "ship_class" in ship2.__dict__.keys() and ship2.ship_class == "1":
        extra = 10
    return sqrt((ship1.position[0] - ship2.position[0])**2+(ship1.position[1] - ship2.position[1])**2) + extra

def get_ship_speed(ship: Ship):
    if ship.ship_class == "3":
        return 13
    elif ship.ship_class == "3":
        return 18


class SharedComms(metaclass=Singleton):
    def __init__(self):
        self._galaxy_at_peace = False
        self.mothership_distance_from_enemies = 1
        self.past_mothership_positions = []
        self._fighter_regen_enabled = False
        self.allied_players = []

    def add_allied_players(self, data: Data, player_name):
        player_ids = [player_id for player_id, player in data.players.items() if player.name == player_name]
        if player_ids:
            self.allied_players.append(player_ids[0])

    @property
    def fighter_regen_enabled(self) -> bool:
        return self._fighter_regen_enabled

    @fighter_regen_enabled.setter
    def fighter_regen_enabled(self, value: bool):
        if self._fighter_regen_enabled != value:
            logger.info(f"Fighter regen {'enabled' if value else 'disabled'}!")
        self._fighter_regen_enabled = value

    @property
    def galaxy_at_peace(self) -> bool:
        return self._galaxy_at_peace

    @galaxy_at_peace.setter
    def galaxy_at_peace(self, value: bool):
        if self._galaxy_at_peace != value:
            logger.info(f"Galaxy {'at peace' if value else 'at war'}!")
        self._galaxy_at_peace = value
