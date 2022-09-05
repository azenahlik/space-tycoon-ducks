from typing import Dict

from space_tycoon_client.models.move_command import MoveCommand
from space_tycoon_client.models.attack_command import AttackCommand
from space_tycoon_client.models.repair_command import RepairCommand
from space_tycoon_client.models.data import Data
from space_tycoon_client.models.ship import Ship
from space_tycoon_client.models.destination import Destination
# from space_tycoon_client.models.target import Target
import logging

from utils.general import countDistanceShips


logger = logging.getLogger(__name__)


def get_ms_fighting_commands(data: Data, player_id: str) -> dict:
    commands = {}

    my_attack_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                   data.ships.items() if ship.player == player_id and ship.ship_class in ["1","4","5"]}
    ms = [ship_id for ship_id, ship in my_attack_ships.items() if ship.ship_class == "1"]

    if not ms:
        return commands

    chosen_enemy_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                      data.ships.items() if ship.player != player_id and ship.ship_class in ["1","4","5"]}
    no_enemy_attack_ships = False
    if chosen_enemy_ships == {}:
        chosen_enemy_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                          data.ships.items() if
                                          ship.player != player_id}
        no_enemy_attack_ships = True
    distances = [(x, countDistanceShips(list(my_attack_ships.values())[0], chosen_enemy_ships[x])) for x in chosen_enemy_ships]
    distances_by_shortest = sorted(distances, key=lambda d: d[1])
    player_data = [data.players[x] for x in data.players if x == player_id][0]

    if len(chosen_enemy_ships):
        if player_data.net_worth.money > 300000 or distances_by_shortest[0][1] < 200 or no_enemy_attack_ships:
            commands[ms[0]] = AttackCommand(distances_by_shortest[0][0])
            logger.info(f'MS attacking enemy fighter ID {list(chosen_enemy_ships.keys())[0]}')

    return commands


def get_fighter_fighting_commands(data: Data, player_id: str, aggro_distance: int) -> dict:
    commands = {}
    my_attack_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                   data.ships.items() if ship.player == player_id and ship.ship_class in ["1","4","5"]}
    my_attack_ships_without_ms: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                   data.ships.items() if ship.player == player_id and ship.ship_class in ["4","5"]}
    if not my_attack_ships_without_ms:
        return commands
    ms = [ship_id for ship_id, ship in my_attack_ships.items() if ship.ship_class == "1"]
    chosen_enemy_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                      data.ships.items() if ship.player != player_id and ship.ship_class in ["4","5"]}
    if chosen_enemy_ships == {}:
        chosen_enemy_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                          data.ships.items() if
                                          ship.player != player_id and ship.ship_class in ["1"]}
    no_enemy_attack_ships = False
    if chosen_enemy_ships == {}:
        chosen_enemy_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                          data.ships.items() if
                                          ship.player != player_id}
        no_enemy_attack_ships = True
    distances = [(x, countDistanceShips(list(my_attack_ships_without_ms.values())[0], chosen_enemy_ships[x])) for x in chosen_enemy_ships]
    distances_by_shortest = sorted(distances, key=lambda d: d[1])

    if len(chosen_enemy_ships):
        if ms and min([x[1] for x in distances_by_shortest]) > aggro_distance and not no_enemy_attack_ships:
            for attack_ship in my_attack_ships_without_ms:
                commands[attack_ship] = MoveCommand(destination=Destination(target=ms[0]))
                print(f'Fighter {attack_ship} is staying with MS')
        else:
            for attack_ship in my_attack_ships_without_ms:
                commands[attack_ship] = AttackCommand(distances_by_shortest[0][0])
                print(f'Fighter {attack_ship} attacking enemy fighter ID {list(chosen_enemy_ships.keys())[0]}')

    return commands


def get_repair_commands(data: Data, player_id: str) -> dict:
    commands = {}

    my_attack_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                   data.ships.items() if ship.player == player_id and ship.ship_class in ["1","4","5"]}

    if len(my_attack_ships):
        logger.info(f'{[(my_attack_ships[attack_ship].name, my_attack_ships[attack_ship].life) for attack_ship in my_attack_ships]}')
        print(f'{[(my_attack_ships[attack_ship].name, my_attack_ships[attack_ship].life) for attack_ship in my_attack_ships]}')

    for attack_ship in my_attack_ships:
        if my_attack_ships[attack_ship].life < 100:
            try:
                logger.info(f"Healing attack ship {my_attack_ships[attack_ship].name}")
                print(f"Healing attack ship {my_attack_ships[attack_ship].name}")
            except:
                pass  # just before sleep and not taking chances
            commands[attack_ship] = RepairCommand()

    return commands