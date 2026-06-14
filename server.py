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

    ERROR_COMMAND_NOT_EXISTS = "[Server] Unknown command. Type '-help' to see available commands."
    ERROR_COMMAND_HAS_NOT_ARGUMENTS = "[Server] Command '{command}' does not accept arguments."
    ERROR_COMMAND_EXPECTS_ARGUMENTS = "[Server] Command '{command}' expects arguments."
class ServerCommands:
    HELP = "-help"
    EXIT = "-exit"
    LIST_USERS = "-listusers"
    LIST_GROUPS = "-listgroups"
    LIST_USERS_IN_GROUP = "-listgroupU"
    CREATE_GROUP = "-creategroup"
    JOIN_GROUP = "-joingroup"
    LEAVE_GROUP = "-leavegroup"

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
    serverLog(ServerMessages.LOG_USER_LEFT_GROUP.format(user=clients[client]))
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

HOST = '127.0.0.1'
PORT = 55555

clients = {}
groups = {}

commands = {
    ServerCommands.HELP: help,
    ServerCommands.LIST_USERS: listAllUsers,
    ServerCommands.LIST_GROUPS: listAllGroups,
    ServerCommands.LIST_USERS_IN_GROUP: listAllUsersInGroup,
    ServerCommands.CREATE_GROUP: createGroup,
    ServerCommands.JOIN_GROUP: joinGroup,
    ServerCommands.LEAVE_GROUP: leaveGroup
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

    while True:
        message = receiveMessage(client)

        if not message:
            break

        command = getCommand(message)

        if command in commands:

            if command == ServerCommands.EXIT:
                break

            commands[command](client, message)
            continue

        if command.startswith("-"):
            sendToClient(ServerMessages.ERROR_COMMAND_NOT_EXISTS, client)
            serverLog(ServerMessages.LOG_USER_TYPE_UNKNOWN_COMMAND.format(user=clients[client], command=command))
            continue

        messageFormatted = f"[CHAT] {user}: {message}"
        serverLog(messageFormatted)
        sendToAll(messageFormatted, client)

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