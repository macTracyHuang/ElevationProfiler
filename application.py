from elevation import getElevation
import matplotlib.pyplot as plt
import csv
import math
import sys
import os


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python application.py xxx.csv")
    else:
        print('Loading')
        filename = sys.argv[1]
        paths = load_data(filename)
        foldername = filename.replace('.csv', '')
        if not os.path.exists(f'Photos/{foldername}/'):
            os.mkdir(f'Photos/{foldername}/')
        plt.figure(figsize=(10, 3))
        finished = False
        i = 0
        retry = 1
        j = 0
        while not finished:
            try:
                plotChart(paths[i], foldername)
            except ConnectionError:
                # retry
                while j < retry:
                    print(f'{j} retry: to plot {paths[i]} again')
                    plotChart(paths[i], foldername)
                    j += 1
            else:
                j = 0
                i += 1
                if i == len(paths):
                    finished = True
                    break

        print('Done')
        sys.exit(f'{i} Photos are saved')


def load_data(filename):
    """
    Load data from csv
    """
    paths = []
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name_a = row["name_a"]
            lat_a = row["lat_a"]
            lng_a = row["lng_a"]
            name_b = row["name_b"]
            lat_b = row["lat_b"]
            lng_b = row["lng_b"]
            path = [[name_a, lat_a, lng_a], [name_b, lat_b, lng_b]]
            paths.append(path)
    return paths


# return elevations and distance
def getElevations(data):
    startStr = data[0][1] + "," + data[0][2]
    endStr = data[1][1] + "," + data[1][2]
    pathStr = startStr + "|" + endStr
    d = getDistance((data[0][1], data[0][2]), (data[1][1], data[1][2]))
    return [getElevation(pathStr), d]


def getDistance(mk1, mk2):
    R = 6371.0710
    rlat1 = float(mk1[0]) * (math.pi/180)
    rlat2 = float(mk2[0]) * (math.pi/180)
    difflat = rlat2-rlat1
    difflon = (float(mk2[1])-float(mk1[1])) * (math.pi/180)
    d = 2 * R * math.asin(math.sqrt(math.sin(difflat/2)*math.sin(difflat / 2)
                          + math.cos(rlat1)*math.cos(rlat2) *
                          math.sin(difflon/2)*math.sin(difflon/2)))
    return round(d, 2)


def plotChart(path, foldername):
    xaxis = [i for i in range(256)]
    title = f'{path[0][0]} - {path[1][0]}'
    if not os.path.exists(f'Photos/{foldername}/' + title + '.png'):
        result = getElevations(path)
        elevations = result[0]
        if elevations == []:
            raise ConnectionError('cannot connect google api')
        distance = result[1]
        plt.bar(xaxis, elevations)
        plt.plot([0, 255], [elevations[0], elevations[-1]],
                 color="#FF0000")
        plt.title(f'Distance(km):{distance}')

        # Finde intersection
        intersection = {}
        m = (elevations[255] - elevations[0]) / 255
        for i in range(256):
            point = m * i + elevations[0]
            if point < elevations[i]:
                intersection[i] = point
        plt.plot(list(intersection.keys()),
                 list(intersection.values()), "y*")
        plt.savefig(f'Photos/{foldername}/' + title + '.png')
        plt.clf()
        print(f'{title} is saved')
        return 1
    else:
        print(f'{title} has already been saved')


if __name__ == '__main__':
    main()
