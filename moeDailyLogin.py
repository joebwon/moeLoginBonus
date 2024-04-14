#!/usr/bin/python3
import time
import json
from dotenv import load_dotenv
import os
import glob
import sqlite3
import csv
from datetime import datetime
import requests
import subprocess


load_dotenv()

log_directory = os.getenv('LOG_DIRECTORY', 'C:\\moenew\\MatrixServerTool\\chat_logs\\')
channel_names = {channel.split('=')[0]: channel.split('=')[1] for channel in os.getenv('CHANNEL_FRIENDLY_NAMES', '').split(',') if '=' in channel}
local_channels = list(channel_names.keys())
webhook_url = os.getenv('DISCORD_WEBHOOK')
rcon_password = os.getenv('RCON_PASSWORD')

db_path = os.getenv('DATABASE_PATH', 'C:\\Moenew\\WindowsPrivateServer\\MOE\\Saved\\SaveGames\\BigPrivate\\moe_role.db')


csv_file_path = 'account_log.csv'


def initialize_csv():
    try:
        with open(csv_file_path, 'a+', newline='') as csvfile:
            csvfile.seek(0)
            if not csvfile.read(1):
                writer = csv.writer(csvfile)
                writer.writerow(['s_account_uid', 'from_nick', 'Date', 'Status'])
    except IOError as e:
        print(f"IO Error while initializing CSV file: {e}")


initialize_csv()


def execute_commands(channel_friendly_name, s_account_uid):

    # Mapping of channel friendly names to RCON Ports.
    port_mapping = {
        "Eastern": "5030",
        "Central": "5060"
    }
    port = port_mapping.get(channel_friendly_name, "1234")

    # Modify stuff here to change what people get from the daily.
    # You can get the commands/IDs by spawning an item to a player and watching the game's log.
    commands = [
        f"mcrcon.exe -H 127.0.0.1 -P {port} -p {rcon_password} -w 5 \"AddCopper {s_account_uid} 10000\"",
        f"mcrcon.exe -H 127.0.0.1 -P {port} -p {rcon_password} -w 5 \"AddSkillPublicExpToPlayer {s_account_uid} 25000\"",
        f"mcrcon.exe -H 127.0.0.1 -P {port} -p {rcon_password} -w 5 \"AddItemToPlayer {s_account_uid} 4532 1 1 1 -1 1.000000\"",
        f"mcrcon.exe -H 127.0.0.1 -P {port} -p {rcon_password} -w 5 \"AddItemToPlayer {s_account_uid} 4534 1 1 1 -1 1.000000\"",
        f"mcrcon.exe -H 127.0.0.1 -P {port} -p {rcon_password} -w 5 \"AddItemToPlayer {s_account_uid} 4747 1 1 1 -1 1.000000\"",
        f"mcrcon.exe -H 127.0.0.1 -P {port} -p {rcon_password} -w 5 \"AddItemToPlayer {s_account_uid} 4544 3 1 1 1 -1 1.000000\"",
        f"mcrcon.exe -H 127.0.0.1 -P {port} -p {rcon_password} -w 5 \"AddItemToPlayer {s_account_uid} 4549 1 1 1 1 -1 1.000000\""
    ]

    for command in commands:
        subprocess.run(command, check=True, shell=True)


def process_account(account_id, from_nick, to_channel):
    today = datetime.now().strftime("%Y-%m-%d")
    found = False
    accounts = []

    channel_friendly_name = channel_names.get(to_channel, "Unknown Channel")

    try:
        with open(csv_file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)

            for row in reader:
                if row[0] == account_id:
                    found = True
                    if row[2] == today and row[3] == '0':
                        print(f"User {from_nick} has already executed the command today.")
                        return
                    elif row[3] != '0':
                        print(f"User {from_nick} is banned.")
                        return
                    else:
                        row[2] = today
                        print(f"Date for user {from_nick} is being updated to today.")
                        execute_commands(channel_friendly_name, account_id)
                        send_to_discord(channel_friendly_name, from_nick, "Claimed their daily login reward by typing /dailyreward into Nearby chat")
                accounts.append(row)

        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(accounts)
            if not found:
                writer.writerow([account_id, from_nick, today, '0'])
                print(f"Entry for user {from_nick} has been added.")
                execute_commands(channel_friendly_name, account_id)
                send_to_discord(channel_friendly_name, from_nick, "Claimed their daily login reward by typing /dailyreward into Nearby chat")

    except IOError as e:
        print(f"IOError while processing account: {e}")


def get_account_id(s_role_uid):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT s_account_id FROM moe_roles WHERE s_role_uid = ?", (s_role_uid,))
        account_id = cursor.fetchone()
        conn.close()
        return account_id[0] if account_id else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

#
# If we wanted to use MySQL or a variant, this might be a viable replacement for get_account_id. I have no way to test this, so it's commented.
# If you want to try this out, just comment the old get_account_id, uncomment this one (maybe move the imports to the top of the script...)
#   and add your mysql connection information to the conn = mysqlconnector.connect block.
#

# import mysql.connector
# from mysql.connector import Error

# def get_account_id(s_role_uid, db_config):
#     try:
#         conn = mysql.connector.connect(
#             host=db_config['host'],
#             user=db_config['user'],
#             password=db_config['password'],
#             database=db_config['database']
#         )
#         cursor = conn.cursor()
#         cursor.execute("SELECT s_account_id FROM moe_roles WHERE s_role_uid = %s", (s_role_uid,))
#         account_id = cursor.fetchone()
#         cursor.close()
#         conn.close()
#         return account_id[0] if account_id else None
#     except Error as e:
#         print(f"Database error: {e}")
#         return None

def find_latest_file(directory):
    list_of_files = glob.glob(f'{directory}*')
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def watch_log_file(directory):
    current_file = find_latest_file(directory)
    file_position = os.path.getsize(current_file)

    while True:
        try:
            new_file = find_latest_file(directory)
            if new_file != current_file:
                current_file = new_file
                file_position = 0

            with open(current_file, 'r', encoding='utf-8') as file:
                file.seek(file_position)
                lines = file.readlines()
                file_position = file.tell()

            for line in lines:
                process_line(line)

        except Exception as e:
            print(f"Error encountered: {e}")
            time.sleep(5)
            continue

        time.sleep(1)


def check_csv_for_entry(from_role_uid):
    today = datetime.now().strftime("%Y-%m-%d")
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['s_account_uid'] == from_role_uid:
                is_today = row['Date'] == today
                return True, is_today
    return False, False


def process_line(line):
    try:
        log_entry = json.loads(line)
        to_channel = log_entry.get("to")
        if to_channel in local_channels:
            from_role_uid = log_entry.get("from")
            from_nick = log_entry.get("from nick", "Unknown")
            content = log_entry.get("content", "")

            if "/dailyreward" in content:
                entry_exists, is_today = check_csv_for_entry(from_role_uid)

                if entry_exists and is_today:
                    print(f"User {from_nick} has already executed the command today, skipping database query.")
                    return

                account_id = get_account_id(from_role_uid)
                if account_id:
                    process_account(account_id, from_nick, to_channel)
                else:
                    print(f"Account ID not found for the given role UID: {from_role_uid}.")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")


def send_to_discord(channel_friendly_name, from_nick, content):
    def escape_markdown(text):
        markdown_chars = ['\\', '*', '_', '~', '`', '>', '|']
        for char in markdown_chars:
            text = text.replace(char, '\\' + char)
        return text


    def truncate_message(text, max_length=2000):
        return text if len(text) <= max_length else text[:max_length-3] + '...'
    from_nick = escape_markdown(from_nick)
    content = escape_markdown(content)
    content = truncate_message(content)
    message = f"{channel_friendly_name}: {from_nick}: {content}"
    data = {"content": message}
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        print(f"Error sending message to Discord: {response.status_code} - {response.text}")


watch_log_file(log_directory)
