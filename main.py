import sys
from time import sleep
from g_python.gextension import Extension
from g_python.hmessage import Direction, HMessage
from g_python.hpacket import HPacket


extension_info = {
    "title": "G-Spam",
    "description": "Application to spam in rooms",
    "author": "denio4321",
    "version": "1.0"
}

ext = Extension(extension_info, args=sys.argv)
ext.start()

FLOOD = list()
ROOM = int()
RUNNING = bool()
SPEED = 4
ACTUAL_ROOM = int()

def get_actual_room(message: HMessage):
    global ACTUAL_ROOM
    ACTUAL_ROOM = message.packet.read_int()

def send_spam(message: HMessage):
    command, m, n = message.packet.read_string(), message.packet.read_int(), message.packet.read_int()

    global FLOOD
    global ROOM
    global RUNNING
    global SPEED
    global ACTUAL_ROOM

    if command[0: len(":setflood")].lower() == ":setflood":
        FLOOD.append(command[len(":setflood")::])
        message.is_blocked = True
        ext.send_to_client(HPacket('Whisper', -1, "Defined Flood: " + FLOOD[-1], 0, 30, 0, -1))

    elif command[0: len(":setroom")].lower() == ":setroom":
        args = command.split()
        if args[1].lower() == "actual":
            ROOM = ACTUAL_ROOM
        else:
            ROOM = int(command[len(":setroom")::].replace(" ", ""))

        message.is_blocked = True
        ext.send_to_client(HPacket('Whisper', -1, "Defined Room: " + str(ROOM), 0, 30, 0, -1))

    elif command[0: len(":setspeed")].lower() == ":setspeed":
        SPEED = int(command[len(":setspeed")::].replace(" ", ""))
        message.is_blocked = True
        ext.send_to_client(HPacket('Whisper', -1, "Defined Speed: " + str(SPEED) + " seconds", 0, 30, 0, -1))

    elif command[0: len(":config")].lower() == ":config":
        message.is_blocked = True
        ext.send_to_client(HPacket('Whisper', -1, "Total floods: " + str(len(FLOOD)), 0, 30, 0, -1))
        index = 1
        for flood_message in FLOOD:
            ext.send_to_client(HPacket('Whisper', -1, "Flood " + str(index) + ": "+ flood_message, 0, 30, 0, -1))
            index += 1
        ext.send_to_client(HPacket('Whisper', -1, "Defined Room: " + str(ROOM), 0, 30, 0, -1))
        ext.send_to_client(HPacket('Whisper', -1, "Defined Speed: " + str(SPEED) + " seconds", 0, 30, 0, -1))

    elif command[0: len(":start")].lower() == ":start":
        RUNNING = True
        message.is_blocked = True
        index = 0
        while RUNNING == True:
            ext.send_to_server(HPacket('GetGuestRoom', ROOM, 0, 1))
            sleep(SPEED)
            ext.send_to_server(HPacket('Chat', FLOOD[index], m, n))
            index += 1
            if index > len(FLOOD)-1:
                index = 0

    elif command[0: len(":stop")].lower() == ":stop":
        RUNNING = False
        message.is_blocked = True

    elif command[0: len(":help")].lower() == ":help":
        message.is_blocked = True
        ext.send_to_client(HPacket('Whisper', -1, "List of commands:", 0, 30, 0, -1))
        sleep(0.1)
        ext.send_to_client(HPacket('Whisper', -1, ":setflood (string, required, cand add more than one): Define the flooding message.", 0, 30, 0, -1))
        sleep(0.1)
        ext.send_to_client(HPacket('Whisper', -1, ":setroom  (integer, required): Define the targeted room (Use :setroom actual for most recent visited room).", 0, 30, 0, -1))
        sleep(0.1)
        ext.send_to_client(HPacket('Whisper', -1, ":setspeed (integer, default: 4 seconds) :Define flooding speed.", 0, 30, 0, -1))
        sleep(0.1)
        ext.send_to_client(HPacket('Whisper', -1, ":config : Displays actual configuration.", 0, 30, 0, -1))
        sleep(0.1)
        ext.send_to_client(HPacket('Whisper', -1, ":start : Begin flooding with previous configuration.", 0, 30, 0, -1))
        sleep(0.1)
        ext.send_to_client(HPacket('Whisper', -1, ":stop  : Stops flooding.", 0, 30, 0, -1))

ext.intercept(Direction.TO_SERVER, send_spam, 'Chat', mode='async_modify')
ext.intercept(Direction.TO_SERVER, get_actual_room, 'GetGuestRoom')
