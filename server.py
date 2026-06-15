import socket, threading
from datetime import datetime

class ServerMessages:
    HELP = """
Available Commands:

-help
    Show this help message.

-exit
    Disconnect from the server.

-listusers
    List all online users.

-listgroups
    List all existing groups.

-listgroupU <group_name>
    List all users in the specified group.

-creategroup <group_name>
    Create a new group.

-joingroup <group_name>
    Join an existing group.

-leavegroup <group_name>
    Leave a group you are part of.
    
-msg <U/G> <Target> <Message>
    Send a message to a user (U) or group (G).
    
-msgt <C/D/T> <Message>
    Broadcast to Connected(C), Log for Disconnected (D), or Total/All(T)
"""

    SERVER_RUNNING = "Server running on {HOST}:{PORT}.\nWaiting for connections..."
    DISCONNECT_WARING = "[Server] Press 'Enter' to exit..."

    LOG_HELP = "[INFO] User '{user}' used help command."
    LOG_USER_TYPE_UNKNOWN_COMMAND = "[INFO] User '{user}' try type command '{command}'."
    LOG_USER_CONNECTED = "[INFO] User '{user}' connected."
    LOG_USER_DISCONNECTED = "[INFO] User '{user}' disconnected."
    LOG_USER_LIST_USERS = "[INFO] User '{user}' listed online users."
    LOG_USER_LIST_GROUPS = "[INFO] User '{user}' listed active groups."
    LOG_USER_LIST_USER_GROUP = "[INFO] User '{user}' listed users in group '{group}'."
    LOG_USER_CREATE_GROUP = "[INFO] User '{user}' create group '{group}'."
    LOG_USER_JOIN_GROUP = "[INFO] User '{user}' join in the group '{group}'."
    LOG_USER_LEFT_GROUP = "[INFO] User '{user}' left the group '{group}'."
    LOG_MSG_PRIVATE = "[MSG PRIVATE] From '{sender}' to '{target}': {msg}"
    LOG_MSG_GROUP = "[MSG GROUP] From '{sender}' to Group '{target}': {msg}"
    LOG_MSGT = "[BROADCAST {scope}] From '{sender}': {msg}"
   
    USER_JOIN_CHAT = "[Server] '{user}' joined the chat!"
    USER_LEFT_CHAT = "[Server] '{user}' left the chat."
    USER_JOIN_GROUP = "[Server] '{user}' joined the '{group}' group!"
    USER_LEFT_GROUP = "[Server] '{user}' left the '{group}' group."
    USER_EXIST_IN_GROUP = "[Server] User is already part of this group."
    USER_NOT_EXIST_IN_GROUP = "[Server] User is not part of this group."
    ERROR_USER_EXISTS = "[Server] Nickname already in use!"

    GROUP_EXISTS = "[Server] Group already exists."
    GROUP_NOT_EXISTS = "[Server] Group not exists."
    GROUP_CREATED = "[Server] Group '{group}' created successfully."
    NO_GROUPS_CREATED = "[Server] No groups created."
    NO_USERS_IN_GROUP =  "[Server] No users in this group."
    ERROR_USER_NOT_FOUND = "[Server] User '{target}' not found."

    ERROR_COMMAND_NOT_EXISTS = "[Server] Unknown command. Type '-help' to see available commands."
    ERROR_COMMAND_HAS_NOT_ARGUMENTS = "[Server] Command '{command}' does not accept arguments."
    ERROR_COMMAND_EXPECTS_ARGUMENTS = "[Server] Command '{command}' expects arguments."

    ERROR_INVALID_FORMAT = "[Server] Invalid command format. Type '-help' for guidance."

    ERROR_NO_ONE_ONLINE = "[Server] There are no others online users in the server."
    ERROR_NO_ONE_OFFLINE = "[Server] There are no others offline users in the server."
    ERROR_NO_CLIENTS = "[Server] There are no others users in the server."

class ServerCommands:
    HELP = "-help"
    EXIT = "-exit"
    LIST_USERS = "-listusers"
    LIST_GROUPS = "-listgroups"
    LIST_USERS_IN_GROUP = "-listgroupU"
    CREATE_GROUP = "-creategroup"
    JOIN_GROUP = "-joingroup"
    LEAVE_GROUP = "-leavegroup"
    MSG = "-msg"
    MSGT = "-msgt"

def help(client, message):
    if commandHasArguments(message):
        sendToClient(ServerMessages.ERROR_COMMAND_HAS_NOT_ARGUMENTS.format(command=ServerCommands.HELP), client)
        return
    
    sendToClient(ServerMessages.HELP,client)
    serverLog(ServerMessages.LOG_HELP.format(user=clients[client]))
    return

def listAllUsers(client, message):
    if commandHasArguments(message):
        sendToClient(ServerMessages.ERROR_COMMAND_HAS_NOT_ARGUMENTS.format(command=ServerCommands.LIST_USERS), client)
        return

    users = []

    for user in clients.values():
        users.append(user)

    listUsers = f"Online: {users}"

    sendToClient(listUsers, client)
    serverLog(ServerMessages.LOG_USER_LIST_USERS.format(user=clients[client]))
    return

def createGroup(client, message):
    if not commandHasArguments(message):
        sendToClient(ServerMessages.ERROR_COMMAND_EXPECTS_ARGUMENTS.format(command=ServerCommands.CREATE_GROUP), client)
        return
    
    groupName = message.replace(ServerCommands.CREATE_GROUP, "", 1).strip()

    if groupName in groups:
        sendToClient(ServerMessages.GROUP_EXISTS, client)
        return

    groups[groupName] = set()
    sendToClient(ServerMessages.GROUP_CREATED.format(group=groupName), client)
    serverLog(ServerMessages.LOG_USER_CREATE_GROUP.format(user=clients[client], group=groupName))
    return

def joinGroup(client, message):
    if not commandHasArguments(message):
        sendToClient(ServerMessages.ERROR_COMMAND_EXPECTS_ARGUMENTS.format(command=ServerCommands.JOIN_GROUP), client)
        return
    
    groupName = message.replace(ServerCommands.JOIN_GROUP, "", 1).strip()

    if groupName not in groups:
        sendToClient(ServerMessages.GROUP_NOT_EXISTS, client)
        return
    
    user = clients[client]

    if user in groups[groupName]:
        sendToClient(ServerMessages.USER_EXIST_IN_GROUP, client)
        return
    
    groups[groupName].add(clients[client])
    sendToClient(ServerMessages.USER_JOIN_GROUP.format(user=user, group=groupName), client)
    serverLog(ServerMessages.LOG_USER_JOIN_GROUP.format(user=user, group=groupName))
    return

def leaveGroup(client, message):
    if not commandHasArguments(message):
        sendToClient(ServerMessages.ERROR_COMMAND_EXPECTS_ARGUMENTS.format(command=ServerCommands.LEAVE_GROUP), client)
        return
    
    groupName = message.replace(ServerCommands.LEAVE_GROUP, "", 1).strip()

    if groupName not in groups:
        sendToClient(ServerMessages.GROUP_NOT_EXISTS, client)
        return
    
    user = clients[client]

    if user not in groups[groupName]:
        sendToClient(ServerMessages.USER_NOT_EXIST_IN_GROUP, client)
        return
    
    groups[groupName].remove(clients[client])
    sendToClient(ServerMessages.USER_LEFT_GROUP.format(user=user, group=groupName), client)
    serverLog(ServerMessages.LOG_USER_LEFT_GROUP.format(user=user, group=groupName))
    return

def listAllGroups(client, message):
    if commandHasArguments(message):
        sendToClient(ServerMessages.ERROR_COMMAND_HAS_NOT_ARGUMENTS.format(command=ServerCommands.LIST_GROUPS), client)
        return
    
    if not groups:
        sendToClient(ServerMessages.NO_GROUPS_CREATED, client)
        return

    groupsCurrent = []

    for groupName in groups.keys():
        groupsCurrent.append(groupName)

    listGroups = f"Groups: {groupsCurrent}"

    sendToClient(listGroups, client)
    serverLog(ServerMessages.LOG_USER_LIST_GROUPS.format(user=clients[client]))
    return

def listAllUsersInGroup(client, message):
    if not commandHasArguments(message):
        sendToClient(ServerMessages.ERROR_COMMAND_EXPECTS_ARGUMENTS.format(command=ServerCommands.LIST_USERS_IN_GROUP), client)
        return
    
    groupName = message.replace(ServerCommands.LIST_USERS_IN_GROUP, "", 1).strip()

    if groupName not in groups:
        sendToClient(ServerMessages.GROUP_NOT_EXISTS, client)
        return
    
    if not groups[groupName]:
        sendToClient(ServerMessages.NO_USERS_IN_GROUP, client)
        return
    
    groupUsers = []

    for users in groups[groupName]:
        groupUsers.append(users)
    
    listGroupsUsers = f"Group Users: {groupUsers}"

    sendToClient(listGroupsUsers, client)
    serverLog(ServerMessages.LOG_USER_LIST_USER_GROUP.format(user=clients[client], group=groupName))
    return

def handleMsgCommand(client, message):
    parts = message.split(maxsplit=3)
    if len(parts) < 4:
        sendToClient(ServerMessages.ERROR_INVALID_FORMAT, client)
        return

    sub_command = parts[1].upper()
    target = parts[2]
    text_message = parts[3]
    sender = clients[client]

    if sub_command == "U":
        handleMsgToUser(client, sender, target, text_message)
    elif sub_command == "G":
        handleMsgToGroup(client,sender, target, text_message)
    else:
        sendToClient(ServerMessages.ERROR_INVALID_FORMAT, client)

def handleMsgToUser(client, sender, target, message):
    target_client = None
    timestamp = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    online_users = list(clients.values())

    user_exists = (target in online_users) or (target in offline_messages)

    if not user_exists:
        sendToClient(ServerMessages.ERROR_USER_NOT_FOUND.format(target=target), client)
        return

    for c, name in clients.items():
        if name == target:
            target_client = c
            break

    messageFormatted = f"{timestamp} [PV-MSG] {sender}: [PV] {message}"

    if target_client:
        sendToClient(messageFormatted, target_client)
        sendToClient(f"[PV-MSG] send to {target}]: {message}", client)
    else:
        saveOfflineMessage(target, messageFormatted)
        sendToClient(f"[Send to {target}: {message}]", client)

    serverLog(ServerMessages.LOG_MSG_PRIVATE.format(sender=sender, target=target, msg=message))

def handleMsgToGroup(client, sender, target, message):
    timestamp = datetime.now().strftime("%d/%m/%y %H:%M:%S")

    if target not in groups:
        sendToClient(ServerMessages.GROUP_NOT_EXISTS, client)
        return

    if sender not in groups[target]:
        sendToClient(ServerMessages.USER_NOT_EXIST_IN_GROUP, client)
        return

    messageFormatted = f"{timestamp} [GP-MSG] ({sender}, {target}) {message}"
    online_users = list(clients.values())

    for member in groups[target]:
        if member == sender:
            continue
        
        if member in online_users:
            for c, name in clients.items():
                if name == member:
                    sendToClient(messageFormatted, c)
                    break
        else:
            saveOfflineMessage(member, messageFormatted)

    serverLog(ServerMessages.LOG_MSG_GROUP.format(sender=sender, target=target, msg=message))

def handleMsgtCommand(client, message):
    parts = message.split(maxsplit=2)
    if len(parts) < 3:
        sendToClient(ServerMessages.ERROR_INVALID_FORMAT, client)
        return

    scope = parts[1].upper()
    text_message = parts[2]
    sender = clients[client]
    online_users = list(clients.values())
    timestamp = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    messageFormatted = f"{timestamp} [BROADCAST] ({sender}): {text_message}"

    if scope == "C":
        if len(online_users) <= 1:
            sendToClient(ServerMessages.ERROR_NO_ONE_ONLINE, client)
            return
        sendToAll(messageFormatted, client)
        serverLog(ServerMessages.LOG_MSGT.format(scope="ONLINE (C)", sender=sender, msg=text_message))

    elif scope == "D":
        disconnected_users = [user for user in offline_messages.keys() if user not in online_users]
        if not disconnected_users:
            sendToClient(ServerMessages.ERROR_NO_ONE_OFFLINE, client)
            return
        for member in disconnected_users:
            saveOfflineMessage(member, messageFormatted)
        sendToClient("[Server] Broadcast message sent to all offline users.", client)
        serverLog(ServerMessages.LOG_MSGT.format(scope="OFFLINE (D)", sender=sender, msg=text_message))

    elif scope == "T":
        has_others_online = len(online_users) > 1
        disconnected_users = [user for user in offline_messages.keys() if user not in online_users]
        has_others_offline = len(disconnected_users) > 0
        if not has_others_online and not has_others_offline:
            sendToClient(ServerMessages.ERROR_NO_CLIENTS, client)
            return
        sendToAll(messageFormatted, client)
        saveOfflineMessageToAll(offline_messages.keys(), messageFormatted)
        serverLog(ServerMessages.LOG_MSGT.format(scope="TOTAL (T)", sender=sender, msg=text_message))
    else:
        sendToClient(ServerMessages.ERROR_INVALID_FORMAT, client)

HOST = '127.0.0.1'
PORT = 55555

clients = {}
groups = {}
offline_messages = {}

commands = {
    ServerCommands.HELP: help,
    ServerCommands.LIST_USERS: listAllUsers,
    ServerCommands.LIST_GROUPS: listAllGroups,
    ServerCommands.LIST_USERS_IN_GROUP: listAllUsersInGroup,
    ServerCommands.CREATE_GROUP: createGroup,
    ServerCommands.JOIN_GROUP: joinGroup,
    ServerCommands.LEAVE_GROUP: leaveGroup,
    ServerCommands.MSG: handleMsgCommand,
    ServerCommands.MSGT: handleMsgtCommand
    }

def sendToClient(message, client):
    encodedMessage = encodeMessage(message)
    client.send(encodedMessage)

def sendToAll(message, senderClient):
    for client in clients:
        if client != senderClient:
            try:
                sendToClient(message, client)
            except:
                removeClient(client)

def sendOfflineMessages(messages, client):
    inbox = ""
    for message in messages:
        if message is not None:
            inbox += str(message) + "\n"

    offlineInbox = f"""[Server] You have OFFLINE messages:
{inbox}[Server]
"""
    sendToClient(offlineInbox, client)

def saveOfflineMessage(target_user, formatted_message):
    if target_user not in offline_messages:
        offline_messages[target_user] = []
    offline_messages[target_user].append(formatted_message)

def saveOfflineMessageToAll(target_users, formatted_message):
    online_users = list(clients.values())
    for member in list(offline_messages.keys()):
            if member not in online_users:
                saveOfflineMessage(member, formatted_message)

def receiveMessage(client):
    try:
        message = decodeMessage(client.recv(1024))

        if not message:
            return None

        return message
    except:
        return None

def serverLog(log):
    currentDate = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    print(f"[{currentDate}] {log}")
    
def removeClient(client):
    if client in clients:
        del clients[client]
    
    client.close()

def disconnectClient(client, user):
    removeClient(client)
    serverLog(ServerMessages.LOG_USER_DISCONNECTED.format(user=user))
    sendToAll(ServerMessages.USER_LEFT_CHAT.format(user=user), client)

def clientService(client):
    user = receiveMessage(client)

    if not user:
        removeClient(client)
        return

    if nickNameExists(user):
        sendToClient(ServerMessages.ERROR_USER_EXISTS, client)
        client.close()
        return

    clients[client] = user

    serverLog(ServerMessages.LOG_USER_CONNECTED.format(user=user))
    sendToAll(ServerMessages.USER_JOIN_CHAT.format(user=user), client)
    
    if user in offline_messages and offline_messages[user]:
        sendOfflineMessages(offline_messages[user], client)
        offline_messages[user] = []
    else:
        if user not in offline_messages:
            offline_messages[user] = []

    while True:
        message = receiveMessage(client)

        if not message:
            break

        command = getCommand(message)

        if command == ServerCommands.EXIT:
            break

        if command in commands:
            commands[command](client, message)
            continue

        else:
            sendToClient(ServerMessages.ERROR_COMMAND_NOT_EXISTS, client)
            serverLog(ServerMessages.LOG_USER_TYPE_UNKNOWN_COMMAND.format(user=clients[client], command=command))

    disconnectClient(client, user)

def nickNameExists(name):
    if name in clients.values():
        return True

def getCommand(message):
    parts = message.split()
    command = parts[0]
    return command

def commandHasArguments(message):
    parts = message.split()

    if len(parts) != 1:
        return True
    
    return False

def encodeMessage(message):
    return message.encode('utf-8')

def decodeMessage(message):
    return message.decode('utf-8')

def startServer():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(ServerMessages.SERVER_RUNNING.format(HOST=HOST, PORT=PORT))

    while True:
        client, address = server.accept()

        thread = threading.Thread(target=clientService, args=(client,))
        thread.start()

if __name__ == "__main__":
    startServer()