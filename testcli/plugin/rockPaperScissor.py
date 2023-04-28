# -*- coding: utf-8 -*-
import random

COMMAND = "GAME"


def cmdEntry(cmdArgs: list):
    if len(cmdArgs) != 1:
        # 至少有一个选择，剪刀，石头，布
        yield {
            "type": "error",
            "message": "Please enter your choise [rock|paper|scissor].",
        }
        return

    computer = random.choice(["rock", "paper", "scissor"])
    user = str(cmdArgs[0])

    # 必须是剪刀，石头，布的一个
    if user.lower() not in ["rock", "paper", "scissor"]:
        yield {
            "type": "error",
            "message": "Please enter correct choise [rock|paper|scissor].",
        }
        return

    message = "opponent choice : {}".format(computer) + "\n"
    if computer == user:
        message = message + "Tie!"
    elif computer == "paper" and user == "scissor":
        message = message + "{0} cuts {1}. Congrats You win!".format(user, computer)
    elif computer == "paper" and user == "rock":
        message = message + "{1} covers {0}. Oops You lost!".format(user, computer)
    elif computer == "scissor" and user == "paper":
        message = message + "{1} cuts {0}. Oops You lost!".format(user, computer)
    elif computer == "scissor" and user == "rock":
        message = message + "{0} smashes {1}. Congrats You win!".format(user, computer)
    elif computer == "rock" and user == "scissor":
        message = message + "{1} smashes {0}. Oops You lost!".format(user, computer)
    elif computer == "rock" and user == "paper":
        message = message + "{0} covers {1}. Congrats You win!".format(user, computer)
    yield {
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": message
    }
