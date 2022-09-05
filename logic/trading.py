from math import sqrt
from logic.utils.ships import HAULER, SHIPPER
from space_tycoon_client.models.data import Data
from space_tycoon_client.models.ship import Ship
from utils.general import countDistanceShips

def getResourceWithLowestPrice(resources):
    lowestPrice = 99999999999
    resourceIdToBuy = -1
    # resourceToBuy = NULL

    for resourceId, resource in resources.items():
        if resource.buy_price != None and resource.buy_price < lowestPrice and resource.amount >= 10:
            lowestPrice = resource.buy_price
            resourceIdToBuy = resourceId

    return resourceIdToBuy

def select_nearest_trader(traders, planet):
    lowest_distance = 999999999999
    trader_id = list(traders.items())[0][0]

    for t_id, trader in traders.items():
        distance_to_planet = countDistanceShips(trader, planet)
        if distance_to_planet < lowest_distance:
            lowest_distance = distance_to_planet
            trader_id = t_id

    return trader_id

def canBeTradeCommandFullfiled(ship, data):
    target_resource = ship.command.resource
    target_amount = ship.command.amount
    target_target = ship.command.target

    planet_resource = data.planets[target_target].resources[target_resource]

    if not planet_resource:
        return False
    elif planet_resource.amount < target_amount:
        return False
    elif (ship.position[0] == ship.prev_position[0] and ship.position[1] == ship.prev_position[1]):
        return False
    else:
        return True

def hasPlanetResourcesToSell(planet):
    for id, resource in planet.resources.items():
        if resource.buy_price != None and resource.amount >= 10:
            return True
    return False

def hasResourceWithAmount(ship):
    for id, resource in ship.resources.items():
        if resource['amount'] > 0:
            return True
    return False

def isPlanetBuyingResource(planet, resourceId):
    for id, resource in planet.resources.items():
        if resource.sell_price != None and id == resourceId:
            return True
    return False

def isPlanetInRadius(ship, planet, radius):
    pass

def countDistance(ship, planet):
    return countDistanceShips(ship, planet)



def findTradingOption(ship, data, planetsToExclude, resource_ranges):
    # OLD
    # planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if key not in planetsToExclude and hasPlanetResourcesToSell(planet)}

    # sortedPlanets = sorted(planetsWithTradingOptions.items(), key=lambda x: countDistance(ship, x[1]))


    planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if key not in planetsToExclude and hasPlanetResourcesToSell(planet)}

    sortedPlanets = sorted(planetsWithTradingOptions.items(), key=lambda x: countDistance(ship, x[1]))

    return sortedPlanets[0]


def findSellOption(ship, data):
    resourceIdToSell = list(ship.resources.keys())[0]
    planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if isPlanetBuyingResource(planet, resourceIdToSell)}
    sortedPlanets = sorted(planetsWithTradingOptions.items(), key=lambda x: x[1].resources[resourceIdToSell].sell_price, reverse=True)
    return sortedPlanets[0]


def orderRanges(ranges):
    return sorted(ranges.items(), key=lambda x: x[1]['diff'], reverse=True)

def distanceSqr(A, B):
    x = (A[0] - B[0])
    y = (A[1] - B[1])
    return x * x + y * y + 1

def getResourcesRanges(planets, position):
    planets = planetsInrange(planets, position, 300)
    resources = ["1","10","11","12","13","14","15","16","17","18","19","2","20","21","22","23","3","4","5","6","7","8","9"]
    ranges = {}

    # prepare dict
    for i in resources:
        ranges[i] = {
            'from': None,
            'to': None,
            'sell': 0,
            'buy': 99999999,
            'diff': 0,
            'resource': i
        }

    # find ranges
    print(planets)
    for i in planets.keys():
        for j in planets[i].resources:
            if (planets[i].resources[j].amount > 10):
                d = distanceSqr(position, planets[i].position)
                d = d * d
                if (planets[i].resources[j].buy_price != None and ranges[j]['buy'] > planets[i].resources[j].buy_price / d):
                    ranges[j]['buy'] = planets[i].resources[j].buy_price
                    ranges[j]['from'] = i
                if (planets[i].resources[j].sell_price != None and ranges[j]['sell'] < planets[i].resources[j].sell_price / d):
                    ranges[j]['sell'] = planets[i].resources[j].sell_price
                    ranges[j]['to'] = i

    # compute diff
    for i in ranges:
        ranges[i]['diff'] = ranges[i]['sell'] - ranges[i]['buy']

    return ranges

def planetsInrange(planets, position, maxDistance):
    return {i: planets[i] for i in planets if distanceSqr(planets[i].position, position) < maxDistance * maxDistance}

def get_trading_commands(data: Data, player_id):
    my_traders: Dict[Ship] = {
        ship_id: ship for ship_id, ship in data.ships.items() if ship.player == player_id and ship.ship_class in [HAULER, SHIPPER]
    }

    traders_without_command = {
        ship_id: ship for ship_id, ship in my_traders.items() if not ship.command or not canBeTradeCommandFullfiled(ship, data)
    }

    traders_without_cargo = {
        ship_id: ship for ship_id, ship in my_traders.items() if not hasResourceWithAmount(ship)
    }

    traders_with_cargo = {
        ship_id: ship for ship_id, ship in my_traders.items() if hasResourceWithAmount(ship)
    }

    traders_without_cargo_keys = list(traders_without_cargo.keys())

    commands = {}
    # planetsToExclude = []
    traders_with_new_command = []

    # buy_command_index = 0

    # buy commands
    for index in range(len(traders_without_cargo_keys)):
        # Resoure buying options
        resources_ranges = getResourcesRanges(data.planets, data.ships[traders_without_cargo_keys[index]].position)
        sorted_ranges = orderRanges(resources_ranges)

        planet_trade = sorted_ranges[index]
        # print('FROM', planet_trade)
        planet = data.planets[planet_trade[1]['from']]

        the_chosen_one_id = select_nearest_trader({
            ship_id: ship for ship_id, ship in traders_without_cargo.items() if ship_id not in traders_with_new_command
        }, planet)

        traders_with_new_command.append(the_chosen_one_id)

        commands[the_chosen_one_id] = {
            "amount": 10,
            "resource": planet_trade[1]['resource'],
            "target": planet_trade[1]['from'],
            "type": 'trade'
        }

    # sell commands
    for shipId, ship in traders_with_cargo.items():
        resourceIdToSell = list(ship.resources.keys())[0]
        resources_ranges = getResourcesRanges(data.planets, ship.position)
        targetPlanet = resources_ranges[resourceIdToSell]['to']
        commands[shipId] = {
            "amount": -10,
            "resource": resourceIdToSell,
            "target": targetPlanet,
            "type": 'trade'
        }


    # for shipId, ship in traders_without_command.items():
    #     if hasResourceWithAmount(ship):
    #         ## Selling based on finding
    #         # targetPlanet = findSellOption(ship, data)
    #         ## based on table
    #         resourceIdToSell = list(ship.resources.keys())[0]
    #         targetPlanet = resources_ranges[resourceIdToSell].to
    #         commands[shipId] = {
    #             "amount": -10,
    #             "resource": resourceIdToSell,
    #             "target": targetPlanet[0],
    #             "type": 'trade'
    #         }
    #     else:
    #         # Buying
    #         targetPlanet = findTradingOption(ship, data, planetsToExclude, resources_ranges)
    #         planetsToExclude.append(targetPlanet[0])
            
    #         resourceToBuy = getResourceWithLowestPrice(targetPlanet[1].resources)

    #         commands[shipId] = {
    #             "amount": 10,
    #             "resource": resourceToBuy,
    #             "target": targetPlanet[0],
    #             "type": 'trade'
    #         }
    #         buy_command_index += 1

    return commands
    


# if __name__ == "__main__":
#     print(MOTHERSHIP)