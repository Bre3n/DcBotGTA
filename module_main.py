import json
import os
import sqlite3
from asyncio import sleep
from datetime import date, datetime
import coloredlogs
import logging
from os import path

import requests

import database_main

players_js = os.environ.get("PLAYERS")
dynamic_js = os.environ.get("DYNAMIC")
bot_id_js = os.environ.get("BOT_ID")
update_channel_js = os.environ.get("UPDATE_CHANNEL")
update_message_js = os.environ.get("UPDATE_MESSAGE")
update_channel_black_js = os.environ.get("UPDATE_CHANNEL_BLACK")
update_massage_black_js = os.environ.get("UPDATE_MESSAGE_BLACK")


def logs():
    now_date = str(date.today())
    i = 1
    if path.exists(f"logs") == False:
        os.mkdir(f"logs")
    if path.exists(f"logs/SORT_BY_MODIFICATION_TIME.txt") == False:
        f = open(f"logs/SORT_BY_MODIFICATION_TIME.txt", "w")
        f.write("")
        f.close()
    if path.exists(f"logs/{now_date}-9.log") == True:
        os.remove(f"logs/{now_date}-9.log")
    if path.exists(f"logs/{now_date}.log") == True:
        while path.exists(f"logs/{now_date}-{i}.log") == True:
            i = i + 1
        os.rename(f"logs/{now_date}.log", f"logs/{now_date}-{i}.log")
    else:
        if path.exists(f"logs/latest.log") == True:
            os.rename(
                f"logs/latest.log",
                f"logs/{now_date}.log",
            )


logs()

logging.Formatter(fmt="%(asctime)s.%(msecs)03d", datefmt="%Y-%m-%d,%H:%M:%S")
logging.basicConfig(
    filename=f"logs/latest.log", format="%(asctime)s %(message)s", filemode="w"
)
logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.DEBUG, logger=logger)


def log(type, string):
    if type == "info":
        logger.info(string)
    elif type == "debug":
        logger.debug(string)
    elif type == "error":
        logger.error(string)
    elif type == "critical":
        logger.critical(string)


def czas():
    now_time = datetime.now()
    current_time = now_time.strftime("%H:%M:%S")
    current_day = now_time.strftime("%d:%m")
    return current_day, current_time


def get_item(item):
    itemek = []
    bufor = f"```\nCurrently supported items:\n\n"
    for i in range(len(item)):
        itemek = item[i].split(";")
        itemek = itemek[1]
        bufor += str(itemek)
        if i < len(item) - 1:
            bufor += ", "
    bufor += "\n```"
    return bufor


def get_dynamic():
    try:
        response = requests.get(dynamic_js)
        json_data = json.loads(response.text)
        buf = str(json_data["clients"]) + "/" + str(json_data["sv_maxclients"])
        return buf
    except requests.exceptions.Timeout:
        return "error"
    except requests.exceptions.TooManyRedirects:
        return "error"
    except requests.exceptions.RequestException:
        return "error"


def get_players(ctx):
    try:
        response = requests.get(players_js)
        json_data = json.loads(response.text)
        j = 0
        buf = 0
        member_list = []
        member_name = []
        server_list = []
        for member in ctx.guild.members:
            if str(member.id) != str(bot_id_js):
                buf += 1
                member_list.append(str(member.id))
        for i in range(len(json_data)):
            json_data_buf = str(json_data[i])
            server_list = json_data_buf.split("'")
            for j in range(len(member_list)):
                exist = "discord:" + str(member_list[j]) in server_list
                if exist == True:
                    member_name.append(member_list[j])
        return member_name
    except requests.exceptions.Timeout:
        return "error"
    except requests.exceptions.TooManyRedirects:
        return "error"
    except requests.exceptions.RequestException:
        return "error"


async def get_update(ctx, bot, user):
    conn = sqlite3.connect("database.sqlite")
    sql = conn.cursor()
    row1 = []
    row2 = []
    tablica = user
    if user != "black":
        if user == "chest":
            bufor = f"```\n\t\t\t\t\tItems in a shared locker:\n\n"
        else:
            user = str(user).replace("U", "")
            user = await bot.fetch_user(int(user))
            bufor = f"```\n\t\t\t\t\tItems in {user} locker:\n\n"
        for row in sql.execute(f"SELECT przedmiot FROM {tablica}"):
            row = str(row)
            row = (
                row.replace("'", "").replace(",", "").replace("(", "").replace(")", "")
            )
            row1.append(row)
        for row in sql.execute(f"SELECT ile FROM {tablica}"):
            row = str(row)
            row = (
                row.replace("'", "").replace(",", "").replace("(", "").replace(")", "")
            )
            row2.append(row)
        for i in range(len(row1)):
            bufor += f"\t\t\t\t\t{row1[i]} - {row2[i]}\n"
        bufor += "```"
        conn.close()
    else:
        bufor = await database_main.blacklist(ctx, bot, "info", "", "")
    return bufor


def get_user(ctx, bot, user):
    for member in ctx.guild.members:
        if str(member.id) != str(bot_id_js) and str(
            bot.get_user(int(member.id))
        ) == str(user):
            user = member.id
            user = (
                str(user)
                .replace("(", "")
                .replace(")", "")
                .replace("'", "")
                .replace(",", "")
                .replace("@", "")
                .replace("<", "")
                .replace(">", "")
                .replace("!", "")
            )
            return user


def check_ids():
    if update_channel_js == "None":
        log(
            "error",
            "The channel ID for updating global locker has not been set correctly!",
        )
    else:
        if update_message_js == "None":
            log(
                "error",
                "The message ID for updating global locker has not been set correctly!",
            )
    if update_channel_black_js == "None":
        log(
            "error", "The channel ID for updating blacklist has not been set correctly!"
        )
    else:
        if update_massage_black_js == "None":
            log(
                "error",
                "The message ID for updating blacklist has not been set correctly!",
            )
