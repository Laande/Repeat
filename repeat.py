import sys
from g_python.gextension import Extension
from g_python.hmessage import Direction, HMessage

extension_info = {
    "title": "Repeat",
    "description": "Repeat a message",
    "version": "2.0",
    "author": "Lande"
}

ext = Extension(extension_info, sys.argv)
ext.start()


def on_connection_start():
    print('Connected with: {}:{}'.format(ext.connection_info['host'], ext.connection_info['port']))
    if ext.harble_api: print("Harble API :" + ext.harble_api)
    else: print("No Harble API detected")


ext.on_event('connection_start', on_connection_start)


messages = {}
enable = True


def speech_in(message):
    global enable
    if enable:
        message.packet.read_int()
        mess = message.packet.read_string(encoding='utf-8')
        message.packet.read_int()
        message.packet.read_int()
        message.packet.read_int()
        message.packet.read_int()

        for i in range(len(messages), 0, -1):
            if i < 10:
                if messages[f"{i}"]:
                    messages[f"{i+1}"] = messages[f"{i}"]
        messages["1"] = mess

        print(messages)


def speech(message):
    (text, color, index) = message.packet.read('sii')
    if text == ":say":
        message.is_blocked = True
        for i in range(len(messages), 0, -1):
            ext.send_to_client("{l}{h:1446}{i:0}{s:\""+f"{i}"+": "+messages[f"{i}"]+"\"}{i:0}{i:1}{i:0}{i:0}")
        if not messages:
            ext.send_to_client("{l}{h:1446}{i:0}{s:\"No message found\"}{i:0}{i:1}{i:0}{i:0}")

    global enable

    if text == ":say start":
        message.is_blocked = True
        if enable:
            ext.send_to_client("{l}{h:1446}{i:0}{s:\"Log message are already enabled\"}{i:0}{i:1}{i:0}{i:0}")
        else:
            enable = True
            ext.send_to_client("{l}{h:1446}{i:0}{s:\"Log message enabled\"}{i:0}{i:1}{i:0}{i:0}")
        return

    if text == ":say stop":
        message.is_blocked = True
        if not enable:
            ext.send_to_client("{l}{h:1446}{i:0}{s:\"Log message are already stopped\"}{i:0}{i:1}{i:0}{i:0}")
        else:
            enable = False
            ext.send_to_client("{l}{h:1446}{i:0}{s:\"Log message stopped\"}{i:0}{i:1}{i:0}{i:0}")
        return

    if text == ":say clear":
        message.is_blocked = True
        messages.clear()
        ext.send_to_client("{l}{h:1446}{i:0}{s:\"Messages clear\"}{i:0}{i:1}{i:0}{i:0}")
        return

    if text.startswith(":say "):
        message.is_blocked = True
        arg = text[5:]
        num = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        if arg in num:
            ext.send_to_server("{l}{h:1314}{s:\""+messages[arg]+"\"}{i:0}{i:0}")
        else:
            ext.send_to_client("{l}{h:1446}{i:0}{s:\"Invalid argument\"}{i:0}{i:1}{i:0}{i:0}")


ext.intercept(Direction.TO_CLIENT, speech_in, 1446)
ext.intercept(Direction.TO_SERVER, speech, 1314)