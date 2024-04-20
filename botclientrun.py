from client import BotClient
import random

bot_names = [
    "BOT John",
    "BOT Emily",
    "BOT Michael",
    "BOT Sarah",
    "BOT William",
    "BOT Jessica",
    "BOT David",
    "BOT Ashley",
    "BOT James",
    "BOT Jennifer",
    "BOT Robert",
    "BOT Amanda",
    "BOT Joseph",
    "BOT Brittany",
    "BOT Daniel",
    "BOT Samantha",
    "BOT Christopher",
    "BOT Megan",
    "BOT Matthew",
    "BOT Lauren"
]

random.shuffle(bot_names)

client = BotClient(bot_names.pop())
client.run()