from typing import Dict

from space_tycoon_client.models.move_command import MoveCommand
from space_tycoon_client.models.attack_command import AttackCommand
from space_tycoon_client.models.repair_command import RepairCommand
from space_tycoon_client.models.rename_command import RenameCommand
from space_tycoon_client.models.data import Data
from space_tycoon_client.models.ship import Ship
from space_tycoon_client.models.destination import Destination
# from space_tycoon_client.models.target import Target
import logging

logger = logging.getLogger(__name__)

from utils.general import countDistanceShips
from utils.ship_helpers import get_my_attack_ships, get_enemy_attack_ships,\
    get_mothership, get_distance_ships_ms_extra, get_enemy_ships, get_closest_ships, get_my_ships

mapping = {"1": "Motherlode",
           "2": "Sysiphus",
           "3": "Worm",
           "4": "Redeye",
           "5": "Tyrant",
           "6": "Balrog",
           "7": "GiantFortress",
           "X": "Ninja"}

def rename_ships(data: Data, player_id: str):
    commands = {}
    my_ships = get_my_ships(data, player_id)
    ship_names = [my_ships[ship_id].name for ship_id in my_ships]
    for ship_id in my_ships:
        ship = my_ships[ship_id]
        if ship.ship_class == "4" and "Ninja" not in ship_names:
            commands[ship_id] = RenameCommand("Ninja")
            ship_names.append("Ninja")
            continue
        if f"{mapping[ship.ship_class]}" not in ship.name and ship.name != "Ninja":
            name = f"{mapping[ship.ship_class]}_1"
            i = 1
            while name in ship_names:
                i += 1
                name = f"{mapping[ship.ship_class]}_{i}"
            commands[ship_id] = RenameCommand(name)
            ship_names.append(name)
    return commands


# def run_command()


def kill_specific_player_fighters(data: Data, player_id: str, player_name: str):
    commands = {}
    specific_player_id = [player_id for player_id, player in data.players.items() if player.name == player_name][0]
    specific_player_fighters = {ship_id: ship for ship_id, ship in data.ships.items() if
            ship.player == specific_player_id and ship.ship_class == "4"}
    logger.info(f'Fighters for player {player_name} ({specific_player_id}) are priority targets: {list(specific_player_fighters.keys())}')
    my_fighters = get_my_attack_ships(data, player_id, False)
    if specific_player_fighters:
        for fighter_id in my_fighters:
            closest_specific_player_fighters = get_closest_ships(data, player_id, {fighter_id: my_fighters[fighter_id]}, specific_player_fighters)
            commands[fighter_id] = AttackCommand(list(closest_specific_player_fighters[0].keys())[0])
    return commands