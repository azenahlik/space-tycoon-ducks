from typing import Dict

from space_tycoon_client.models.move_command import MoveCommand
from space_tycoon_client.models.attack_command import AttackCommand
from space_tycoon_client.models.repair_command import RepairCommand
from space_tycoon_client.models.data import Data
from space_tycoon_client.models.ship import Ship
from space_tycoon_client.models.destination import Destination
# from space_tycoon_client.models.target import
import logging

from utils.general import SharedComms
from utils.ship_helpers import get_my_attack_ships, get_enemy_attack_ships,\
    get_mothership, get_distance_ships_ms_extra, get_enemy_ships, get_closest_ships


logger = logging.getLogger(__name__)



def get_ms_fighting_commands(data: Data, player_id: str) -> dict:
    commands = {}

    my_attack_ships: Dict[Ship] = get_my_attack_ships(data, player_id)
    ms = [ship_id for ship_id, ship in my_attack_ships.items() if ship.ship_class == "1"]
    mothership = get_mothership(data, player_id)
    if not ms:
        return commands

    SharedComms().past_mothership_positions = SharedComms().past_mothership_positions[-29:] + [list(mothership.values())[0].position]
    logger.info(f"Past MS positions: {SharedComms().past_mothership_positions}")
    chosen_enemy_ships: Dict[Ship] = get_enemy_attack_ships(data, player_id)
    no_enemy_attack_ships = False
    if chosen_enemy_ships == {}:
        chosen_enemy_ships: Dict[Ship] = get_enemy_ships(data, player_id)
        no_enemy_attack_ships = True
        SharedComms().galaxy_at_peace = True
    closest_filtered_enemy_ships = get_closest_ships(data, player_id, mothership, chosen_enemy_ships)
    player_data = [data.players[x] for x in data.players if x == player_id][0]

    SharedComms().mothership_distance_from_enemies = min([list(x.values())[0] for x in closest_filtered_enemy_ships])

    if len(chosen_enemy_ships):
        if player_data.net_worth.money > 300000 or SharedComms().mothership_distance_from_enemies < 200 or no_enemy_attack_ships:
            commands[ms[0]] = AttackCommand(list(closest_filtered_enemy_ships[0].keys())[0])
            logger.info(f'MS ({list(mothership.values())[0].name}) attacking enemy ship ID {list(chosen_enemy_ships.keys())[0]}')

    return commands


def get_fighter_fighting_commands(data: Data, player_id: str, aggro_distance: int, follow_distance:int = 20) -> dict:
    commands = {}
    my_attack_ships: Dict[Ship] = get_my_attack_ships(data, player_id)
    my_attack_ships_without_ms: Dict[Ship] = get_my_attack_ships(data, player_id, False)

    if not my_attack_ships_without_ms:
        return commands
    ms = [ship_id for ship_id, ship in my_attack_ships.items() if ship.ship_class == "1"]
    mothership = get_mothership(data, player_id)
    chosen_enemy_ships: Dict[Ship] = get_enemy_attack_ships(data, player_id, False)
    if chosen_enemy_ships == {}:
        chosen_enemy_ships: Dict[Ship] = get_enemy_attack_ships(data, player_id)
    no_enemy_attack_ships = False
    if chosen_enemy_ships == {}:
        chosen_enemy_ships: Dict[Ship] = get_enemy_ships(data, player_id)
        no_enemy_attack_ships = True
    closest_filtered_enemy_ships = get_closest_ships(data, player_id, mothership, chosen_enemy_ships)

    if len(chosen_enemy_ships):
        if ms and SharedComms().mothership_distance_from_enemies > aggro_distance and not no_enemy_attack_ships:
            for attack_ship in my_attack_ships_without_ms:
                past_ms_positions = SharedComms().past_mothership_positions
                mothership_follow_pos = past_ms_positions[-min(len(past_ms_positions), follow_distance)]
                commands[attack_ship] = MoveCommand(destination=Destination(coordinates=mothership_follow_pos))
                logger.info(f'Fighter {attack_ship} is staying with MS')
        else:
            for attack_ship in my_attack_ships_without_ms:
                commands[attack_ship] = AttackCommand(list(closest_filtered_enemy_ships[0].keys())[0])
                logger.info(f'Fighter {attack_ship} attacking enemy fighter ID {list(chosen_enemy_ships.keys())[0]}')

    return commands


def get_repair_commands(data: Data, player_id: str) -> dict:
    commands = {}

    my_attack_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                   data.ships.items() if ship.player == player_id and ship.ship_class in ["1","4","5"]}
    my_heavy_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                   data.ships.items() if
                                   ship.player == player_id and ship.ship_class in ["1", "5"]}
    my_fighter_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                   data.ships.items() if
                                   ship.player == player_id and ship.ship_class in ["4"]}

    if len(my_attack_ships):
        logger.info(f'Ship health log: {[(my_attack_ships[attack_ship].name, my_attack_ships[attack_ship].life) for attack_ship in my_attack_ships]}')
    else:
        return commands

    for attack_ship in my_heavy_ships:
        if my_attack_ships[attack_ship].life < 190:
            try:
                logger.info(f"Healing attack ship {my_attack_ships[attack_ship].name}")
            except:
                pass  # just before sleep and not taking chances
            commands[attack_ship] = RepairCommand()

    for attack_ship in my_fighter_ships:
        if my_attack_ships[attack_ship].life < 100:
            try:
                logger.info(f"Healing attack ship {my_attack_ships[attack_ship].name}")
            except:
                pass  # just before sleep and not taking chances
            commands[attack_ship] = RepairCommand()

    return commands