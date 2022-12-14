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
    get_mothership, get_distance_ships_ms_extra, get_enemy_ships, get_closest_ships, get_ships_in_range


logger = logging.getLogger(__name__)



def get_ms_fighting_commands(data: Data, player_id: str) -> dict:
    """Mothership control"""
    commands = {}
    # if not SharedComms().allied_players:
    #     SharedComms().add_allied_players(data, "amazon")
    # print(f"Ignoring {SharedComms().allied_players}")
    # Init
    my_attack_ships: Dict[Ship] = get_my_attack_ships(data, player_id)
    ms = [ship_id for ship_id, ship in my_attack_ships.items() if ship.ship_class == "1"]
    mothership = get_mothership(data, player_id)
    if not ms:
        return commands  # If MS dead

    # Store MS values
    SharedComms().past_mothership_positions = SharedComms().past_mothership_positions[-29:] + [list(mothership.values())[0].position]
    logger.info(f"Past MS positions: {SharedComms().past_mothership_positions}")
    logger.info(f"MS distance from enemies: {SharedComms().mothership_distance_from_enemies}")
    # Prioritize targets, MSs first, then fighters, then rest
    chosen_enemy_ships: Dict[Ship] = get_enemy_ships(data, player_id, ["1"])
    no_enemy_attack_ships = False
    if chosen_enemy_ships == {}:
        chosen_enemy_ships: Dict[Ship] = get_enemy_attack_ships(data, player_id)
        if chosen_enemy_ships == {}:
            chosen_enemy_ships: Dict[Ship] = get_enemy_ships(data, player_id)
            no_enemy_attack_ships = True
            SharedComms().galaxy_at_peace = True
    else:
        SharedComms().galaxy_at_peace = False
    # Get closest ships from the targeted category
    closest_filtered_enemy_ships = get_closest_ships(data, player_id, mothership, chosen_enemy_ships)
    player_data = [data.players[x] for x in data.players if x == player_id][0]

    # Main decision
    if len(chosen_enemy_ships):
        # Update comms
        SharedComms().mothership_distance_from_enemies = min([list(x.values())[0] for x in closest_filtered_enemy_ships])
        if player_data.net_worth.money > 300000 or SharedComms().mothership_distance_from_enemies < 200 or no_enemy_attack_ships:
            # Recalculate ships, if any attack ships are close, defend
            recalculated_enemy_ships = get_enemy_attack_ships(data, player_id)
            if recalculated_enemy_ships:
                closest_filtered_enemy_ships = get_closest_ships(data, player_id, mothership, recalculated_enemy_ships)
            # Attack selected ship
            commands[ms[0]] = AttackCommand(list(closest_filtered_enemy_ships[0].keys())[0])
            logger.info(f'MS ({list(mothership.values())[0].name}) attacking enemy ship ID {list(closest_filtered_enemy_ships[0].keys())[0]}')

    return commands


def get_fighter_fighting_commands(data: Data, player_id: str, aggro_distance: int, follow_distance:int = 20) -> dict:
    commands = {}
    my_attack_ships: Dict[Ship] = get_my_attack_ships(data, player_id)
    my_attack_ships_without_ms: Dict[Ship] = get_my_attack_ships(data, player_id, False)

    if not my_attack_ships_without_ms:
        return commands
    ms = [ship_id for ship_id, ship in my_attack_ships.items() if ship.ship_class == "1"]
    # Prioritize targets
    chosen_enemy_ships: Dict[Ship] = get_enemy_attack_ships(data, player_id, True)  # All attack enemy ships including MS
    if chosen_enemy_ships == {}:
        chosen_enemy_ships: Dict[Ship] = get_enemy_attack_ships(data, player_id)  # All enemy attack ships
    if chosen_enemy_ships == {}:
        chosen_enemy_ships: Dict[Ship] = get_enemy_ships(data, player_id)  # All enemy ships

    # Main decision
    if len(chosen_enemy_ships):
        # If MS not dead/not under attack/peaceful, follow it
        if ms and SharedComms().mothership_distance_from_enemies > aggro_distance and not SharedComms().galaxy_at_peace:
            for attack_ship in my_attack_ships_without_ms:
                past_ms_positions = SharedComms().past_mothership_positions
                mothership_follow_pos = past_ms_positions[-min(len(past_ms_positions), follow_distance)]
                commands[attack_ship] = MoveCommand(destination=Destination(coordinates=mothership_follow_pos))
                logger.info(f'Fighter {attack_ship} is staying with MS')
        else:
            # Attack trade ships if possible, leave battles to MSs
            enemy_trade_ships = get_enemy_ships(data, player_id, ['2', '3', '7'])
            for attack_ship in my_attack_ships_without_ms:
                closest_filtered_enemy_ships = get_closest_ships(data, player_id, {ship_id: my_attack_ships_without_ms[ship_id] for ship_id in my_attack_ships_without_ms}, enemy_trade_ships)
                if len(closest_filtered_enemy_ships) > 0:
                    commands[attack_ship] = AttackCommand(list(closest_filtered_enemy_ships[0].keys())[0])
                    logger.info(f'Fighter {attack_ship} is going crazy!')

    return commands


def get_sabotage_commands(data: Data, player_id: str) -> dict:
    pass


def get_repair_commands(data: Data, player_id: str) -> dict:
    """Repairs attack ships if critical HP, fighters optional"""
    commands = {}

    my_attack_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                   data.ships.items() if ship.player == player_id and ship.ship_class in ["1","4","5"]}
    my_mothership: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                  data.ships.items() if
                                  ship.player == player_id and ship.ship_class == "1"}
    my_bombers: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                   data.ships.items() if
                                   ship.player == player_id and ship.ship_class == "5"}
    my_fighter_ships: Dict[Ship] = {ship_id: ship for ship_id, ship in
                                   data.ships.items() if
                                   ship.player == player_id and ship.ship_class == "4"}

    if len(my_attack_ships):
        logger.info(f'Ship health log: {[(my_attack_ships[attack_ship].name, my_attack_ships[attack_ship].life) for attack_ship in my_attack_ships]}')
    else:
        return commands

    enemy_ships = get_enemy_ships(data, player_id)

    for attack_ship in my_mothership:
        if my_attack_ships[attack_ship].life < 250:
            logger.info(f"Healing mothership ({attack_ship}) {my_attack_ships[attack_ship].name}")
            commands[attack_ship] = RepairCommand()
    for attack_ship in my_bombers:
        if len(get_ships_in_range(data, player_id, attack_ship, enemy_ships, 300)) > 1:
            if my_attack_ships[attack_ship].life < 190:
                logger.info(f"Healing bomber ({attack_ship}) {my_attack_ships[attack_ship].name} in danger")
                commands[attack_ship] = RepairCommand()
        else:
            if my_attack_ships[attack_ship].life < 150:
                logger.info(f"Healing bomber ({attack_ship}) {my_attack_ships[attack_ship].name} safely")
                commands[attack_ship] = RepairCommand()

    if SharedComms().fighter_regen_enabled:
        for attack_ship in my_fighter_ships:
            if my_attack_ships[attack_ship].life < 70:
                logger.info(f"Healing attack ship {my_attack_ships[attack_ship].name}")
                commands[attack_ship] = RepairCommand()

    return commands