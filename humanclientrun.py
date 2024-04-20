from client import HumanClient
import random
player_names = [
    "Yael",
    "Avraham",
    "Shira",
    "David",
    "Tamar",
    "Yosef",
    "Rivka",
    "Eitan",
    "Maya",
    "Itzhak",
    "Hadar",
    "Moshe",
    "Shoshana",
    "Ariel",
    "Esther",
    "Yitzhak",
    "Lior",
    "Sara",
    "Omer",
    "Rachel"
]

random.shuffle(player_names)

client = HumanClient(player_names.pop())
client.run()