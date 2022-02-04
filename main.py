import glob
import matplotlib.pyplot as plot
import numpy
import random
import requests


def get_user_mail():
    # Please paste here your email address in order to use the random.org api
    return "alexander dot aw64 at gmail dot com"


# Create a  3D plot with random numbers
def get_plot_3D(generator, amount, dataset=None, old=False, write=False):
    numbers = None

    if old is False:
        numbers = get_new_random_numbers(generator, amount, write)
    elif old is True:
        numbers = get_old_random_numbers(generator, amount, dataset)

    if numbers is None:
        print("No numbers provided to create a graph.")
        return

    numbers_x = []
    numbers_y = []
    numbers_z = []

    title = f"Random numbers by {generator} with an amount of {amount} numbers in 3D"

    figure = plot.figure(num=title)

    plot.rc('font', size=15)

    axis = figure.add_subplot(projection='3d')

    i = 0
    while i < len(numbers) - 3:
        numbers_x.append(numbers[i + 0])
        numbers_y.append(numbers[i + 1])
        numbers_z.append(numbers[i + 2])
        i += 3

    axis.scatter(numbers_x, numbers_y, numbers_z, marker=".", s=1)

    axis.set_xlabel('X Feld')
    axis.set_ylabel('Y Feld')
    axis.set_zlabel('Z Feld')

    plot.show()


# Create a  2D plot with random numbers
def get_plot_2D(generator, amount, dataset=None, old=False, write=False):
    numbers = None

    if old is False:
        numbers = get_new_random_numbers(generator, amount, write)
    elif old is True:
        numbers = get_old_random_numbers(generator, amount, dataset)

    if numbers is None:
        print("No numbers provided to create a graph.")
        return

    numbers_x = []
    numbers_y = []

    title = f"Random numbers by {generator} with an amount of {amount} numbers in 2D"

    figure = plot.figure(num=title)

    plot.rc('font', size=15)

    axis = figure.add_subplot()

    i = 0
    while i < len(numbers) - 2:
        numbers_x.append(numbers[i + 0])
        numbers_y.append(numbers[i + 1])
        i += 2

    axis.scatter(numbers_x, numbers_y, marker=".", s=0.5)

    axis.set_xlabel('X Feld')
    axis.set_ylabel('Y Feld')

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
            dataset = len(glob.glob(f"output_data/{generator}_{amount}_*.txt")) + 1
            file_name = f"{generator}_{amount}_{dataset}.txt"
            with open("output_data/" + file_name, "w", encoding="utf-8") as file:
                for number in result:
                    file.write(str(number) + "\n")
            print("Wrote results to: output_data/" + file_name)
        except Exception as e:
            print("An error occurred: " + str(e))

    return result


# Method to retrieve old generated numbers
def get_old_random_numbers(generator, amount, dataset):
    result = []

    try:
        amount = int(amount)
        dataset = int(dataset)
    except Exception:
        print("Incorrect value provided.")
        return None

    file_path = glob.glob(f"output_data/{generator}_{amount}_{dataset}.txt")

    if not file_path:
        print("File not found.")
        return None

    try:
        with open(file_path[0], "r", encoding="utf-8") as file:
            print(f"Reading file '{file_path[0]}'.")
            for line in file.readlines():
                stripped_line = line.strip("\n")
                if stripped_line != "":
                    try:
                        result.append(float(stripped_line))
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
        result = float(n) / 199017
        results.append(result)
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
    print("Welcome to the generator test script!")

    """ Methods for the result table """

    """ XY-tuple of the lcg with 100000 numbers in 2D """
    # get_plot_2D("lcg", 100000)
    """ XYZ-tuple of the lcg with 100000 numbers in 3D """
    # get_plot_3D("lcg", 100000)

    """ XY-tuple by random.random() with 100000 numbers in 2D """
    # get_plot_2D("random_lib", 100000)
    """ XYZ-tuple by random.random() with 100000 numbers in 3D """
    # get_plot_3D("random_lib", 100000)

    """ XY-tuple by numpy.random.random() with 100000 numbers in 2D """
    # get_plot_2D("numpy_lib", 100000)
    """ XYZ-tuple by numpy.random.random() with 100000 numbers in 3D """
    # get_plot_3D("numpy_lib", 100000)

    """ 
    Watch out! You could exceed the quota and not be able to request new numbers for that day
    Because of that, every request to random.org is saved in output_data/ 
    """
    """ XY-tuple by Random.org with 10000 numbers in 2D """
    # get_plot_2D("random_org", 10000)
    """ XYZ-tuple by Random.org with 10000 numbers in 3D """
    # get_plot_3D("random_org", 10000)
    
    """ Other useful methods """

    """ You can request new numbers in a list
        Possible generator string are 'random_lib', 'numpy_lib', 'lcg', 'random_org'
        The amount can be from 1 to ..., except for random_org there is the max 10000 """
    # print(get_new_random_numbers("numpy_lib", 100000, write=True))

    """ You can use write=True as parameter to safe the generated numbers to output_data/ """
    # get_plot_2D("numpy_lib", 100000, write=True)
    # print(get_new_random_numbers("numpy_lib", 100000, write=True))

    """ You can use numbers which are saved to output_data/
        It searches in the folder for files with the generator name, amount of numbers and dataset index
        Now is the parameter write= ignored and dataset= specifies the file index of same generator and amount """
    # get_plot_3D("numpy_lib", 100000, dataset=1, old=True)
    # print(get_old_random_numbers("numpy_lib", 100000, dataset=1))
    
    print("Bye, have a good day. :)")


run()
