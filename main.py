import datetime
import matplotlib.pyplot as plot
import numpy
import random
import requests
import os


def get_timestamp():
    return str(datetime.datetime.now().replace(microsecond=0))


def get_plot_3D(generator, amount, old=False, write=False):
    numbers = None

    if old is False:
        numbers = get_new_random_numbers(generator, amount, write)
    elif old is True:
        numbers = get_old_random_numbers()

    if numbers is None:
        print("No numbers provided to create a graph.")
        return

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


def get_plot_2D(generator, amount, old=False, write=False):
    numbers = None

    if old is False:
        numbers = get_new_random_numbers(generator, amount, write)
    elif old is True:
        numbers = get_old_random_numbers()

    if numbers is None:
        print("No numbers provided to create a graph.")
        return

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


# Method to retrieve new generated numbers
def get_new_random_numbers(generator, amount, write=False):
    result = []

    try:
        amount = int(amount)
        write = bool(write)
    except Exception:
        print("Incorrect value provided.")
        return None

    if amount < 1:
        print("Provided too low amount.")
        return None

    if generator == "random_lib":
        result = generator_random(amount)
    elif generator == "numpy_lib":
        result = generator_numpy(amount)
    elif generator == "lcg":
        result = generator_lcg(amount)
    elif generator == "random_org":
        write = True
        result = generator_random_org(amount)
    else:
        print("No generator specified.")
        return None

    if write:
        try:
            file_name = generator + "_" + get_timestamp().replace(" ", "_").replace(":", "-") + ".txt"
            with open("output_data/" + file_name, "w", encoding="utf-8") as file:
                for number in result:
                    file.write(str(number) + "\n")
            print("Wrote results to: output_data/" + file_name)
        except Exception as e:
            print("An error occurred: " + str(e))

    return result


# Method to retrieve old generated numbers
def get_old_random_numbers():
    result = []

    try:
        file_path = input("Which file do you want to use? Please provide the full path to the file: \n")

        if file_path == "":
            print("Incorrect file path provided.")
            return None
        elif os.path.exists(file_path) is False:
            print("File does not exist.")
            return None
        elif os.path.getsize(file_path) <= 0:
            print("File is empty.")
            return None

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file.readlines():
                stripped_line = line.strip("\n")
                if stripped_line != "":
                    try:
                        result.append(int(stripped_line))
                    except Exception as e:
                        print("An error occurred: " + str(e))
                        return None

    except Exception as e:
        print("An error occurred: " + str(e))
        return None

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
    if get_user_mail() == "":
        print("No user mail provided, can't use the random.org api quota checker.")
        return True

    print("Checking quota of random.org.")
    try:
        header = {'User-Agent': f'{get_user_mail()}'}
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
def generator_random_org(amount):
    results = []

    if get_user_mail() == "":
        print("No user mail provided, can't use the random.org api.")
        return None

    if amount > 1e4:
        print("Amount value is too high, random.org can only process an amount up to 10000.")
        return None

    # Quota check
    quota = quota_exceeded_random_org()
    if quota:
        return None

    print(f"Getting {amount} random numbers from random.org.")
    try:
        header = {'User-Agent': f'{get_user_mail()}'}
        request = requests.get(
            url=f"https://www.random.org/integers/?num={amount}&min=0&max=1000000000&col=1&base=10&format=plain&rnd=new",
            headers=header)
        if request.status_code == 200:
            results = request.text.split("\n")
        elif request.status_code == 503:
            if quota_exceeded_random_org():
                return None
            print("An error occurred: " + str(request.text).removeprefix("Error:"))
            return None
    except Exception as e:
        print("An error occurred: " + str(e))
        return None

    new_results = []
    for result in results:
        if result == "":
            continue
        result = float(result)
        new_results.append(result / 1e9)

    quota_exceeded_random_org()
    return new_results


def run():
    # quota_exceeded_random_org()
    #
    # print(get_random_numbers("random_org", input("Amount?\n"), input("Start?\n"), input("End?\n"), True))
    # quota_exceeded_random_org()
    get_plot_3D("lcg", 10000)
    get_plot_2D("lcg", 100000)


run()
