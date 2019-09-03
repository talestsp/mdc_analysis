import math
import geopy.distance as gp


def calculateMidPoint(points):
    x = 0
    y = 0
    z = 0

    for i in range(len(points)):
        latitude = points[i][0] * (math.pi / 180)
        longitude = points[i][1] * (math.pi / 180)

        x += math.cos(latitude) * math.cos(longitude)
        y += math.cos(latitude) * math.sin(longitude)
        z += math.sin(latitude)

    total = len(points)

    x = x / total
    y = y / total
    z = z / total

    centralLongitude = math.atan2(y, x)
    centralSquareRoot = math.sqrt(x * x + y * y)
    centralLatitude = math.atan2(z, centralSquareRoot)

    midPointLat = centralLatitude * (180 / math.pi)
    midPointLon = centralLongitude * (180 / math.pi)

    midPoint = (midPointLat, midPointLon)

    return midPoint


def calculateDistance(lat1, lon1, lat2, lon2):
    coords1 = (lat1, lon1)
    coords2 = (lat2, lon2)
    distance = gp.distance(coords1, coords2).m  # utiliza o modelo WGS-84
    return distance


def calculateRadiusOfGyration(points, point=None):
    sum = 0
    if point is None:
        point = calculateMidPoint(points)
    for i in range(len(points)):
        base = calculateDistance(points[i][0], points[i][1], point[0], point[1])
        sum += math.pow(base, 2)
    sum = math.sqrt(sum / len(points))
    return sum


# print
# calculateDistance(41.49008, -71.312796, 41.499498, -81.695391)
# points = [(41.49008, -71.312796), (41.499498, -81.695391)]
# print
# calculateMidPoint(points)
