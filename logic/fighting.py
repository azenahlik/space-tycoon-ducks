from typing import Dict

from space_tycoon_client.models.attack_command import AttackCommand
from space_tycoon_client.models.data import Data
from space_tycoon_client.models.ship import Ship

from utils.general import countDistanceShips


def get_fighting_commands(data: Data, player_id: str) -> dict:
    commands = {}

    my_attack_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                   data.ships.items() if ship.player == player_id and ship.ship_class in ["1","4","5"]}
    chosen_enemy_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                      data.ships.items() if ship.player != player_id and ship.ship_class in ["1","4","5"]}
    if chosen_enemy_ships == {}:
        chosen_enemy_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                          data.ships.items() if
                                          ship.player != player_id}
    distances = [(x, countDistanceShips(list(my_attack_ships.values())[0], chosen_enemy_ships[x])) for x in chosen_enemy_ships]
    distances_by_shortest = sorted(distances, key=lambda d: d[1])
    if len(chosen_enemy_ships):
        for attack_ship in my_attack_ships:
            commands[attack_ship] = AttackCommand(chosen_enemy_ships[distances_by_shortest[0][0]])
            print(f'Fighter {attack_ship} attacking enemy fighter ID {list(chosen_enemy_ships.keys())[0]}')

    return commands
