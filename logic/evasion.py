import math
from logic.utils.ships import HAULER, SHIPPER
from space_tycoon_client.models.data import Data
from space_tycoon_client.models.ship import Ship
from space_tycoon_client.models.planet import Planet
from utils.general import countDistanceShips, count_distance_between_positions, get_ship_speed
from utils.ship_helpers import get_enemy_attack_ships
from typing import Dict, List


def select_enemy_ships_in_radius_by_distance(trader: Ship, enemy_battle_ships: Dict):
    enemy_ships_in_radius = {ship_id: ship for ship_id, ship in enemy_battle_ships.items() if countDistanceShips(trader, ship) >= 20}
    return sorted(enemy_ships_in_radius.items(), key=lambda x: countDistanceShips(trader, x[1]))


def get_evasion_commands(data: Data, player_id):
    commands = {}
    # TRADERS
    my_traders: Dict[Ship] = {
        ship_id: ship for ship_id, ship in data.ships.items() if ship.player == player_id and ship.ship_class in [HAULER, SHIPPER]
    }

    # ENEMY SHIPS
    enemy_attak_ships = get_enemy_attack_ships(data, player_id)

    for trader_id, trader in my_traders.items():
        enemy_ships = select_enemy_ships_in_radius_by_distance(trader, enemy_attak_ships)
        if len(enemy_ships) > 0:
            # evasion tactics
            nearest_enemy_touple = enemy_ships[0]
            nearest_enemy_ship_position = nearest_enemy_touple[1].position
            evade_position = [
                trader.position[0] + (nearest_enemy_ship_position[0] - trader.position[0]) + 10,
                trader.position[1] + (nearest_enemy_ship_position[1] - trader.position[1]) + 10
            ]
            commands[trader_id] = {
                "destination": {
                    "coordinates": evade_position,
                },
                "type": "move"
            }

    return commands

