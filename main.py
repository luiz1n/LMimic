# -*- coding: utf-8 -*-

from g_python.gextension import Extension
from g_python.hdirection import Direction
from g_python.hpacket import HPacket
from g_python.hparsers import HEntity, HEntityType
import sys, re

headers = {

    'Outgoing': {
        'RoomUserTalk': 1314,
        'UserTyping': 1597,
        'UserStopTyping': 1474,
        'UserSaveLook': 2730,
        "RoomUserWalk": 3320,
        "RoomUserAction": 2456,
        "RoomUserShout": 2085,
        "RoomUserDance": 2080,
        "SaveMotto": 2228,
        "RoomUserWhisper": 1543,
        "RoomUserSign": 1975
    },

    'Incoming': {
        'RoomUsers': 374,
        'RoomUserTalk': 1446,
        'UserTyping': 1717,
        'RoomUserWalk': 1640,
        "RoomUserAction": 1631,
        "RoomUserShout": 1036,
        "RoomUserDance": 2233,
        "UserSaveLook": 3920,
        'OnUserEffect': 1167,
        "RoomUserWhisper": 2704,
        "RoomUserSign": 1640
    }

}

extension_info = {
    "title": "LMimic",
    "description": "Mimic user actions",
    "author": "Luizin",
    "version": "1.0"
}

extension = Extension(extension_info, sys.argv)
extension.start()

users = {  }
users_figure = {  }
users_motto = {  }


prefix_command = "!"
aliases_command = ["copy", "mimic", "copiar"]
Copy = False
username = ""

def get_index(message):
    pkt = message.packet
    for user in HEntity.parse(pkt):
        if user.entity_type == HEntityType.HABBO:
            users[user.name] = user.index
            users_figure[user.name] = user.figure_id
            users_motto[user.name] = user.motto

def send_message(message):
    extension.send_to_client(HPacket(headers['Incoming']['RoomUserTalk'], 9, f'[LMimic] ~ {message}', 0, 31, 0, 3))

def on_talk(msg):
    global username, Copy
    pkt = msg.packet
    (message, bubble) = pkt.read('si')
    msg.is_blocked = True
    message = str(message)

    if message.startswith(f'{prefix_command}'):
        try:
            command = re.search(f'{prefix_command}(.+) ', message).group(1)
        except:
            command = message
    else:
        command = message

    if not message.startswith(prefix_command):
        msg.is_blocked = False
        
    if command in aliases_command:
        username = message.replace(f'{prefix_command}{command} ', "")
        if Copy == True:
            if command == f'{prefix_command}{command}':
                Copy = False
                send_message("Mimic Disabled.")
        else:
            Copy = True
            if len(users) >= 1:
                if username in users:
                    send_message(f"Mimic Enabled -> {username}")
                    extension.send_to_server(HPacket(headers['Outgoing']['UserSaveLook'], "M", users_figure[username]))
                    extension.send_to_server(HPacket(headers['Outgoing']['SaveMotto'], users_motto[username]))
            else:
                send_message(f"No users.")
    else:
        if command == f"{prefix_command}stop":
            if Copy:
                Copy = False
                send_message(f'Mimic Disabled.')

# --> Actions <--

def on_user_talk(msg):
    if Copy and len(users) >= 1:
        packet = msg.packet
        (index, message, idk, bubble) = packet.read('isii')
        if index == users[username]:
            message = str(message)
            extension.send_to_server(HPacket(headers['Outgoing']['RoomUserTalk'], message, bubble))

def on_user_typing(msg):
    if Copy and len(users) >= 1:
        packet = msg.packet
        (index, mode) = packet.read('ii')
        if index == users[username]:
            if mode == 1:
                extension.send_to_server(HPacket(headers['Outgoing']['UserTyping']))
            else:
                extension.send_to_server(HPacket(headers['Outgoing']['UserStopTyping']))

def on_user_move(msg):
    if Copy and len(users) >= 1:
        packet = msg.packet
        (idk, index, x, y, z, idk, idk, flatctrl) = packet.read('iiiiiiis')

        if index == users[username]:
            extension.send_to_server(HPacket(headers['Outgoing']['RoomUserWalk'], x, y))

def on_user_action(msg):
    if Copy and len(users) >= 1:
        packet = msg.packet
        (index, action) = packet.read('ii')
        if index == users[username]:
            extension.send_to_server(HPacket(headers['Outgoing']['RoomUserAction'], action))

def on_user_change_figure(msg):
    if Copy and len(users) >= 1:
        packet = msg.packet
        (index, figure, gender, motto, idk) = packet.read('isssi')
        if index != -1:
            if index == users[username]:
                extension.send_to_server(HPacket(headers['Outgoing']['UserSaveLook'], gender, figure))

def on_user_shout(msg):
    if Copy and len(users) >= 1: 
        packet = msg.packet
        (index, message, idk, bubble, idk, idk) = packet.read('isiiii')
        if index == users[username]:
            extension.send_to_server(HPacket(headers['Outgoing']['RoomUserShout'], message, bubble))

def on_user_effect(msg):
    if Copy and len(users) >= 1:
        packet = msg.packet
        (index, effect, idk) = packet.read('iii')
        if index == users[username]:
            extension.send_to_server(HPacket(headers['Outgoing']['RoomUserTalk'], f":enable {effect}", 12, 3))

def on_user_dance(msg):
    if Copy and len(users) >= 1:
        packet = msg.packet
        (index, dance) = packet.read('ii')
        if index == users[username]:
            extension.send_to_server(HPacket(headers['Outgoing']['RoomUserDance'], dance))

def on_user_whisper(msg):
    if Copy and len(users) >= 1:
        packet = msg.packet
        (index, message, idk, idk, idk, idk) = packet.read('isiiii')
        if index == users[username]:
            extension.send_to_server(HPacket(headers['Outgoing']['RoomUserWhisper'], f'{username} {message}', 0))

def on_user_sign(msg):
    packet = msg.packet
    (idk, index, idk, idk, idk, idk, idk, flatctrl_sign) = packet.read('iiiisiis')
    if flatctrl_sign.__contains__("sign"):
        if index == users[username]:
            sign = re.match("/flatctrl 4/sign (.+)//", str(flatctrl_sign)).group(1)
            extension.send_to_server(HPacket(headers['Outgoing']['RoomUserSign'], int(sign)))

##############################################################################################################
#                                LMimic made by Luiz1n                                                       #
extension.intercept(Direction.TO_CLIENT, get_index, headers['Incoming']['RoomUsers'])                        #
extension.intercept(Direction.TO_SERVER, on_talk, headers['Outgoing']['RoomUserTalk'])                       #
extension.intercept(Direction.TO_CLIENT, on_user_typing, headers['Incoming']['UserTyping'])                  #
extension.intercept(Direction.TO_CLIENT, on_user_talk, headers['Incoming']['RoomUserTalk'])                  #
extension.intercept(Direction.TO_CLIENT, on_user_move, headers['Incoming']['RoomUserWalk'])                  # 
extension.intercept(Direction.TO_CLIENT, on_user_shout, headers['Incoming']['RoomUserShout'])                #
extension.intercept(Direction.TO_CLIENT, on_user_change_figure, headers['Incoming']['UserSaveLook'])         #
extension.intercept(Direction.TO_CLIENT, on_user_action, headers['Incoming']['RoomUserAction'])              #
extension.intercept(Direction.TO_CLIENT, on_user_effect, headers['Incoming']['OnUserEffect'])                #
extension.intercept(Direction.TO_CLIENT, on_user_dance, headers['Incoming']['RoomUserDance'])                #
extension.intercept(Direction.TO_CLIENT, on_user_whisper, headers['Incoming']['RoomUserWhisper'])            #
extension.intercept(Direction.TO_CLIENT, on_user_sign, headers['Incoming']['RoomUserSign'])                  #
##############################################################################################################