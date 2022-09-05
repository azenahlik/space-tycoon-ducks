from math import sqrt
from logic.utils.ships import HAULER, SHIPPER
from space_tycoon_client.models.data import Data
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

def findTradingOption(ship, data):
    planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if hasPlanetResourcesToSell(planet)}

    sortedPlanets = sorted(planetsWithTradingOptions.items(), key=lambda x: countDistance(ship, x[1]))

    return sortedPlanets[0]

    # if ship == SHIPPER:

    #     planetsWithinRadius = {key: planet for key, planet in data.planets.items() if isPlanetInRadius(ship, planet, 250)}


    #     for planetId, planet in planetsWithinRadius:

    #         for resourceId, resource in planet.resources:
    #             if 'buyPrice' in resource

    #         bestResoure = [[key, resource] planet.resources
    #         pass

def findSellOption(ship, data):
    resourceIdToSell = list(ship.resources.keys())[0]
    planetsWithTradingOptions = {key: planet for key, planet in data.planets.items() if isPlanetBuyingResource(planet, resourceIdToSell)}
    sortedPlanets = sorted(planetsWithTradingOptions.items(), key=lambda x: x[1].resources[resourceIdToSell].sell_price, reverse=True)
    return sortedPlanets[0]


def getResourcesRanges(data: Data):
    planets = data.planets
    resources = ["1","10","11","12","13","14","15","16","17","18","19","2","20","21","22","23","3","4","5","6","7","8","9"]
    ranges = {}
    for i in resources:
        ranges[i] = {
            'sell': 0,
            'buy': 99999999,
            'diff': 0,
        }

    for i in self.data.planets.keys():
        for j in planets[i].resources:
            if (planets[i].resources[j].buy_price != None and ranges[j]['buy'] > planets[i].resources[j].buy_price):
                ranges[j]['buy'] = planets[i].resources[j].buy_price
            if (planets[i].resources[j].sell_price != None and ranges[j]['sell'] < planets[i].resources[j].sell_price):
                ranges[j]['sell'] = planets[i].resources[j].sell_price
    for i in ranges:
        ranges[i]['diff'] = ranges[i]['sell'] - ranges[i]['buy']

    return ranges

def getTrandingOptions(data: Data):
    
    commands = {}

    for shipId, ship in data.ships.items():
        if ship.ship_class in [str(HAULER), str(SHIPPER)] and not ship.command:

            if hasResourceWithAmount(ship):
                targetPlanet = findSellOption(ship, data)
                resourceIdToSell = list(ship.resources.keys())[0]
                commands[shipId] = {
                    "amount": -10,
                    "resource": resourceIdToSell,
                    "target": targetPlanet[0],
                    "type": 'trade'
                }
            else:
                targetPlanet = findTradingOption(ship, data)
                
                resourceToBuy = getResourceWithLowestPrice(targetPlanet[1].resources)

                commands[shipId] = {
                    "amount": 10,
                    "resource": resourceToBuy,
                    "target": targetPlanet[0],
                    "type": 'trade'
                }

    return commands
    


# if __name__ == "__main__":
#     print(MOTHERSHIP)