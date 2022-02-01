import datetime
import matplotlib.pyplot as plot
import numpy
import random
import requests
import os


def get_curr_timestamp():
    return str(datetime.datetime.now().replace(microsecond=0))


def get_plot_3D(generator, amount):
    numbers = get_random_numbers(generator, amount)

    numbers_x = []
    numbers_y = []
    numbers_z = []

    fig = plot.figure()

    ax = fig.add_subplot(projection='3d')

    i = 0
    while i < len(numbers) - 3:
        numbers_x.append(numbers[i + 0])
        numbers_y.append(numbers[i + 1])
        numbers_z.append(numbers[i + 2])
        i += 3

    ax.scatter(numbers_x, numbers_y, numbers_z, marker=".", s=1)

    ax.set_xlabel('X Feld')
    ax.set_ylabel('Y Feld')
    ax.set_zlabel('Z Feld')

    plot.show()


def get_plot_2D(generator, amount):

    numbers = get_random_numbers(generator, amount)

    numbers_x = []
    numbers_y = []

    fig = plot.figure()

    ax = fig.add_subplot()

    i = 0
    while i < len(numbers) - 2:
        numbers_x.append(numbers[i + 0])
        numbers_y.append(numbers[i + 1])
        i += 2

    ax.scatter(numbers_x, numbers_y, marker=".", s=0.5)

    ax.set_xlabel('X Feld')
    ax.set_ylabel('Y Feld')

    plot.show()


def get_random_numbers(generator, amount, write=False):
    result = []

    try:
        amount = int(amount)
    except Exception:
        print("Incorrect amount value provided.")
        return None

    if amount < 1:
        print("Provided too low amount.")
        return None

    if generator == "random_lib":
        result = generator_random(amount)
    if generator == "numpy_lib":
        result = generator_numpy(amount)
    if generator == "lcg":
        result = generator_lcg(amount)
    # if generator == "random_org":
    #     write = True
    #     result = generator_random_org(amount)

    if write:
        try:
            file_name = generator + "_" + get_curr_timestamp().replace(" ", "_").replace(":", "-") + ".txt"
            with open("output_data/" + file_name, "w", encoding="utf-8") as out:
                for number in result:
                    out.write(str(number) + "\n")
            print("Wrote results to: output_data/" + file_name)
        except Exception as e:
            print("An error occurred: " + str(e))

    return result


# Random generator of the random library
def generator_random(amount):
    results = []
    print(f"Getting {amount} random numbers from random.random().")
    for i in range(amount):
        results.append(random.random())
    return results


# Random generator of the numpy library
def generator_numpy(amount):
    results = []
    print(f"Getting {amount} random numbers from numpy.random.random().")
    for i in range(amount):
        results.append(numpy.random.random())
    return results


# LCG generator from the course
def generator_lcg(amount):
    results = []
    print(f"Getting {amount} random numbers from a LCG.")
    a, n, c, k = 24298, 0, 99991, 199017
    for i in range(amount):
        n = (a * n + c) % k
        results.append(n)
    return results


# To automate random.org requests you need to check quota
def quota_exceeded_random_org():
    print("Checking quota of random.org.")
    try:
        header = {'User-Agent': 'alexander dot aw64 at gmail dot com'}
        request = requests.get(url=f"https://www.random.org/quota/?format=plain", headers=header)
        if request.status_code == 200:
            response = int(request.text)
            if response < 0:
                print(f"Quota exceeded, {response}. Can't request new random numbers.")
                return True
            else:
                print(f"Quota not exceeded, {response}. Can request new random numbers.")
                return False
        elif request.status_code == 503:
            print("An error occurred: " + str(request.text).removeprefix("Error:"))
            return True
    except Exception as e:
        print("An error occurred: " + str(e))
        return True


# Random.org generator
def generator_random_org(amount, start, end):
    if amount > 1e4:
        print("Amount value is too high, random.org can only process an amount up to 10000.")
        return None
    if start < -1e9 or start > 1e9 or end < -1e9 or end > 1e9:
        print("To broad range, random.org does only process numbers between -1e9 and 1e9.")
        return None

    # Quota check, to be done
    quota = False
    if not quota:
        print("Quota not implemented.")
        return None

    quota_exceeded_random_org()
    print(f"Getting {amount} random numbers from random.org, in range from {start} to {end}.")
    try:
        header = {'User-Agent': 'alexander at jwallrodt dot com'}
        request = requests.get(
            url=f"https://www.random.org/integers/?num={amount}&min={start}&max={end}&col=1&base=10&format=plain&rnd=new",
            headers=header)
        if request.status_code == 200:
            quota_exceeded_random_org()
            return request.text.split("\n")
        elif request.status_code == 503:
            if quota_exceeded_random_org():
                return None
            print("An error occurred: " + str(request.text).removeprefix("Error:"))
            return None
    except Exception as e:
        print("An error occurred: " + str(e))
        return None


def run():
    # quota_exceeded_random_org()
    #
    # print(get_random_numbers("random_org", input("Amount?\n"), input("Start?\n"), input("End?\n"), True))
    # quota_exceeded_random_org()
    get_plot_3D("lcg", 10000)
    get_plot_2D("lcg", 100000)


run()
