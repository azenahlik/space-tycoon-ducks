from typing import Dict

from space_tycoon_client.models.move_command import MoveCommand
from space_tycoon_client.models.attack_command import AttackCommand
from space_tycoon_client.models.construct_command import ConstructCommand
from space_tycoon_client.models.data import Data
from space_tycoon_client.models.ship import Ship
from space_tycoon_client.models.destination import Destination
# from space_tycoon_client.models.target import Target
from utils.general import countDistanceShips
import logging


logger = logging.getLogger(__name__)


def get_fighter_construction_commands(data: Data, player_id: str, min_fighters: int, min_money: int) -> dict:
    commands = {}

    my_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                            data.ships.items() if ship.player == player_id}

    my_fighters: Dict[Ship] = {ship_id: ship for ship_id, ship in
                            data.ships.items() if ship.player == player_id and ship.ship_class == "4"}

    # Mothership Init
    ms = [ship_id for ship_id, ship in my_ships.items() if ship.ship_class == "1"]
    player_data = [data.players[x] for x in data.players if x == player_id][0]

    if ms:
        if len(my_fighters) < min_fighters and player_data.net_worth.money >= min_money:
            mothership_id: str = ms[0]
            commands[mothership_id] = ConstructCommand("4")
        else:
            logger.info('No need to build!')
            return commands
    else:
        logger.info("No MS to build fighters!")
        return commands

    return commands
