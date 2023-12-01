import math
import shutil
import logging
import threading
import traceback
import time
from os.path import join, exists, dirname
from os import getcwd, system


logging.basicConfig(level=logging.WARNING)

current_dirname = getcwd()
folder_iotlab = join(current_dirname, "iot-lab")
if not exists(folder_iotlab):
    logging.warning("Folder iot-lab not found.")
    logging.warning("Did you clone the repository with `git clone --recursive` ?")
    exit(1)

folder_contiki = join(folder_iotlab, "parts", "contiki")
if not exists(folder_contiki):
    logging.warning("Folder contiki not found.")
    logging.warning("Did you read the README ?")
    exit(1)

try:
    import enoslib as en
except ImportError:
    logging.warning("Enoslib not found.")
    logging.warning("Did you try to do `python -m pip install enoslib[iotlab]` ?")
    exit(1)


en.init_logging(level=logging.WARNING)
en.check(["IOT-lab"])

stop_reading = False


def reading_thread(serial, name):
    """
    Reading thread. Continuously read the serial from node.

    Necessary since the getting started tutorial supposes a user interaction
    to send and receive packets at the same time.
    """
    while not stop_reading:
        data = serial.read()
        if data:
            displayer[name] = data


def check_code(codes):
    """check if code exists and compile it if not"""
    for one_code in codes:
        if not exists(one_code):
            logging.warning("File %s not found.", one_code)
            logging.warning("Did you do the compilation ?")
            logging.warning("We are going to try to compile it for you.")
        dir_code = dirname(one_code)
        system(f"cd {dir_code} && make TARGET=iotlab-m3")
        if exists(one_code):
            logging.warning("Compilation successful")
            continue
        exit(1)


displayer = {}


def display(length):
    """display thread"""
    global displayer
    while not stop_reading:
        terminal_width, _ = shutil.get_terminal_size()
        rows = []
        for i in range(length):
            val = displayer.get(i)
            if val:
                val = val.replace("\n", " ")
            else:
                val = " "
            rows.append(val)
        col_width = math.floor(terminal_width / length) - (length - 1)
        max_len = max([len(row) for row in rows])
        chunks = []
        i = 0
        while i < max_len:
            for row in rows:
                c = row[i : i + col_width].ljust(col_width)
                chunks.append(c)
            i = i + col_width
        total = "|".join(chunks)
        print(total)
        displayer = {}
        time.sleep(2)


def main():
    """main fn"""
    examples_folder = join(folder_contiki, "examples", "iotlab")

    provider_conf = {
        "walltime": "01:00",
        "resources": {
            "machines": [
                # {
                #     "roles": ["sensor", "captor"],
                #     "archi": "m3:at86rf231",
                #     "site": "lille",
                #     "number": 1,
                #     "image": code_echo_captor,
                # },
                {
                    "roles": [
                        "router",
                    ],
                    "hostname": ["m3-65.lille.iot-lab.info"],
                    "image": join(
                        examples_folder,
                        "05-rpl-tsch-border-router",
                        "border-router.iotlab-m3",
                    ),
                },
                {
                    "roles": ["sensor", "toto"],
                    "hostname": ["m3-66.lille.iot-lab.info"],  # 1857
                    "image": join(
                        examples_folder,
                        "04-er-rest-example",
                        "er-example-client.iotlab-m3",
                    ),
                },
                {
                    "roles": ["sensor", "captor"],
                    "hostname": ["m3-67.lille.iot-lab.info"],  # 1957
                    "image": join(
                        examples_folder,
                        "04-er-rest-example",
                        "er-example-server.iotlab-m3",
                    ),
                },
            ],
            "networks": [
                {
                    "id": "my_network",
                    "type": "prod",
                    "roles": ["sensor"],
                    "site": "lille",
                }
            ],
        },
    }
    codes = [
        one_machine["image"] for one_machine in provider_conf["resources"]["machines"]
    ]
    check_code(codes)

    conf = en.IotlabConf.from_dictionary(provider_conf)

    p = en.Iotlab(conf)
    try:
        roles, networks = p.init()
        sender = roles["captor"][0]
        receiver = roles["toto"][0]
        with en.IotlabSerial(sender, interactive=True) as s_sender, en.IotlabSerial(
            receiver, interactive=True
        ) as s_receiver:
            print("starting experiment")
            display_thread = threading.Thread(target=display, args=(2,))
            display_thread.start()
            read_thread = threading.Thread(target=reading_thread, args=(s_receiver, 0))
            read_thread.start()
            a = threading.Thread(target=reading_thread, args=(s_sender, 1))
            a.start()
            time.sleep(10)
            stop_reading = True
            display_thread.join()
            read_thread.join()
            a.join()

    except Exception as e:
        stop_reading = True
        print(e)
        traceback.print_exc()
    finally:
        # Delete testbed reservation
        # p.destroy()
        return


if __name__ == "__main__":
    main()
