import math
from logic.utils.ships import HAULER, SHIPPER
from space_tycoon_client.models.data import Data
from space_tycoon_client.models.ship import Ship
from space_tycoon_client.models.planet import Planet
from utils.general import countDistanceShips, count_distance_between_positions, get_ship_speed
from utils.ship_helpers import get_enemy_attack_ships
from typing import Dict, List


def normalize_vector(vector):
    vector_size = math.sqrt(
        vector[0]**2 + vector[1]**2
    )
    vector_size = max(vector_size, 1)
    return [vector[0] / vector_size, vector[1] / vector_size];


def select_enemy_ships_in_radius_by_distance(trader: Ship, enemy_battle_ships: Dict):
    enemy_ships_in_radius = {ship_id: ship for ship_id, ship in enemy_battle_ships.items() if countDistanceShips(trader, ship) < 350}
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
            # Prepared code for commision of traders if we dont have any fighters left and no ms
            # if countDistanceShips(trader, enemy_ships[0][1]) < 30:
            #     commands[trader_id] = {
            #         "type": "decommission"
            #     }
            #     continue
            # evasion tactics
            nearest_enemy_touple = enemy_ships[0]
            nearest_enemy_ship_position = nearest_enemy_touple[1].position
            vector_x = trader.position[0] - nearest_enemy_ship_position[0]
            vector_y = trader.position[1] - nearest_enemy_ship_position[1]

            # if on same position then dont evade just continue trade
            if vector_x == 0 and vector_y == 0:
                continue

            normalized = normalize_vector([vector_x, vector_y])
            evade_position = [
                trader.position[0] + math.ceil(40 * normalized[0]),
                trader.position[1] + math.ceil(40 * normalized[1])
            ]
            commands[trader_id] = {
                "destination": {
                    "coordinates": evade_position,
                },
                "type": "move"
            }

    return commands

