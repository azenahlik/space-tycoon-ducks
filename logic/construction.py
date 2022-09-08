from typing import Dict

from space_tycoon_client.models.move_command import MoveCommand
from space_tycoon_client.models.attack_command import AttackCommand
from space_tycoon_client.models.construct_command import ConstructCommand
from space_tycoon_client.models.data import Data
from space_tycoon_client.models.ship import Ship
from space_tycoon_client.models.destination import Destination
from logic.utils.ships import HAULER, SHIPPER, BOMBER, FIGHTER, MOTHERSHIP
# from space_tycoon_client.models.target import Target
from utils.general import countDistanceShips
import logging
from utils.general import SharedComms


logger = logging.getLogger(__name__)


def get_fighter_construction_commands(data: Data, player_id: str, min_fighters: int) -> dict:
    commands = {}

    my_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                            data.ships.items() if ship.player == player_id}

    my_bombers: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                my_ships.items() if ship.ship_class == BOMBER}

    my_fighters: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                my_ships.items() if ship.ship_class == FIGHTER}

    my_shippers: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                my_ships.items() if ship.ship_class == SHIPPER}

    my_haulers: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                my_ships.items() if ship.ship_class == HAULER}

    
    shippers_count = len(my_shippers)
    haulers_count = len(my_haulers)
    fighters_count = len(my_fighters)

    expected_number_of_haulers = 0
    minimal_money_for_trade_ships_to_buy = 1800000

    # Are we at peace?
    if SharedComms().galaxy_at_peace:
        minimal_money_for_trade_ships_to_buy = 800000
        expected_number_of_haulers = max((shippers_count - 10) // 2, 0)

    # Mothership Init
    ms = [ship_id for ship_id, ship in my_ships.items() if ship.ship_class == MOTHERSHIP]
    player_data = [data.players[x] for x in data.players if x == player_id][0]

    if ms:
        # Build first fighters
        if fighters_count < min_fighters and player_data.net_worth.money >= 4000000 and not SharedComms().galaxy_at_peace:
            logger.info(f"Building fighter ships. Money: {player_data.net_worth.money}, GaP: {SharedComms().galaxy_at_peace}")
            mothership_id: str = ms[0]
            commands[mothership_id] = ConstructCommand(FIGHTER)
        # build haulers
        elif player_data.net_worth.money >= minimal_money_for_trade_ships_to_buy and fighters_count >= min_fighters and SharedComms().galaxy_at_peace:
            logger.info(f"Building hauler trading ships. Money: {player_data.net_worth.money}, GaP: {SharedComms().galaxy_at_peace}")
            mothership_id: str = ms[0]
            commands[mothership_id] = ConstructCommand(HAULER)
        # Build shipper army
        elif player_data.net_worth.money >= minimal_money_for_trade_ships_to_buy and fighters_count >= min_fighters and expected_number_of_haulers <= haulers_count:
            logger.info(f"Building trading ships. Money: {player_data.net_worth.money}, GaP: {SharedComms().galaxy_at_peace}")
            mothership_id: str = ms[0]
            commands[mothership_id] = ConstructCommand(SHIPPER)
        # Build more fighters after domination if necessary to quell unrest in galaxy
        elif fighters_count < min_fighters and player_data.net_worth.money >= 1500000 and SharedComms().galaxy_at_peace:
            logger.info(f"Building fighters. Money: {player_data.net_worth.money}, GaP: {SharedComms().galaxy_at_peace}")
            mothership_id: str = ms[0]
            commands[mothership_id] = ConstructCommand(FIGHTER)
        else:
            logger.info(f'No need to build! Money remaining: {player_data.net_worth.money}, GaP: {SharedComms().galaxy_at_peace}')
            return commands
    else:
        logger.info("No MS to build fighters!")
        return commands

    return commands
