from typing import Dict
from math import sqrt
from space_tycoon_client.models.move_command import MoveCommand
from space_tycoon_client.models.attack_command import AttackCommand
from space_tycoon_client.models.repair_command import RepairCommand
from space_tycoon_client.models.data import Data
from space_tycoon_client.models.ship import Ship
from space_tycoon_client.models.destination import Destination
from logic.utils.ships import HAULER, SHIPPER
# from space_tycoon_client.models.target import Target
from utils.general import countDistanceShips, SharedComms


def get_distance_ships_ms_extra(ship1: Ship, ship2: Ship):
    """Extra distance to motherships to dissuade squads from prioritizing them in firefights"""
    extra = 0  # Hack to prefer fighters over motherships
    if "ship_class" in ship2.__dict__.keys() and ship2.ship_class == "1":
        extra = 10
    return sqrt((ship1.position[0] - ship2.position[0])**2+(ship1.position[1] - ship2.position[1])**2) + extra


def get_my_attack_ships(data: Data, player_id: str, include_ms: bool = True) -> Dict:
    return {ship_id: ship for ship_id, ship in data.ships.items() if
            ship.player == player_id and ship.ship_class in ["1" if include_ms else "X", "4", "5"]}


def get_my_ships(data: Data, player_id: str, include_ms: bool = True) -> Dict:
    return {ship_id: ship for ship_id, ship in data.ships.items() if
            ship.player == player_id}


def get_enemy_attack_ships(data: Data, player_id: str, include_ms: bool = True) -> Dict:
    return {ship_id: ship for ship_id, ship in data.ships.items() if
            ship.player not in [player_id] + SharedComms().allied_players and ship.ship_class in ["1" if include_ms else "X", "4", "5"]}


def get_enemy_ships(data: Data, player_id: str, class_filter_list: list = []) -> Dict:
    if not class_filter_list:
        class_filter_list = [str(x) for x in range(1, 8)]
    return {ship_id: ship for ship_id, ship in data.ships.items() if
            ship.player not in [player_id] + SharedComms().allied_players and ship.ship_class in class_filter_list}


def get_mothership(data: Data, player_id: str) -> Dict:
    return {ship_id: ship for ship_id, ship in data.ships.items() if
            ship.player == player_id and ship.ship_class in ["1"]}


def get_distance_ships(ship1: Ship, ship2: Ship, ms_penalty: bool = True):
    extra = 10 if ship2.ship_class == "1" and ms_penalty else 0
    return sqrt((ship1.position[0] - ship2.position[0])**2+(ship1.position[1] - ship2.position[1])**2) + extra


def get_closest_ships(data: Data, player_id: str, my_ship: Ship, enemy_ship_dict: dict) -> list:
    distances = [{x: get_distance_ships(list(my_ship.values())[0], enemy_ship_dict[x])} for x in
                 enemy_ship_dict]
    distances_by_shortest = sorted(distances, key=lambda d: list(d.values())[0])
    return distances_by_shortest


def get_ships_in_range(data: Data, player_id: str, my_ship: Ship, enemy_ship_dict: dict, distance: int) -> dict:
    ships = {x: enemy_ship_dict[x] for x in enemy_ship_dict if
             get_distance_ships(list(my_ship.values())[0], enemy_ship_dict[x]) < distance}
    return ships

def get_ship_cargo_size(ship: Ship):
    if ship.ship_class == HAULER:
        return 40
    elif ship.ship_class == SHIPPER:
        return 10
