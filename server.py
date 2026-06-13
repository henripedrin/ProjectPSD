import socket, threading

class ServerMessages:
    SERVER_RUNNING = "Server running on {HOST}:{PORT}.\nWaiting for connections..."

    USER_CONNECTED = "[Server] {user} connected."
    USER_DISCONNECTED = "[Server] {user} disconnected."
    USER_JOIN_CHAT = "[Server] {user} joined the chat!"
    USER_LEFT_CHAT = "[Server] {user} left the chat."
    USER_JOIN_GROUP = "[Server] {user} joined the {group} group!"
    USER_LEFT_GROUP = "[Server] {user} left the {group} group."
    USER_EXIST_IN_GROUP = "[Server] User is already part of this group."
    USER_NOT_EXIST_IN_GROUP = "[Server] User is not part of this group."
    ERROR_USER_EXISTS = "[Server] Nickname already in use!"

    GROUP_EXISTS = "[Server] Group already exists."
    GROUP_NOT_EXISTS = "[Server] Group not exists."
    GROUP_CREATED = "[Server] Group '{group}' created successfully."

    ERROR_COMMAND_HAS_NOT_ARGUMENTS = "[Server] Command '{command}' does not accept arguments."
    ERROR_COMMAND_EXPECTS_ARGUMENTS = "[Server] Command '{command}' expects arguments."

class ServerCommands:
    EXIT = "-exit"
    LIST_USERS = "-listusers"
    LIST_GROUPS = "-listgroups"
    LIST_USERS_IN_GROUP = "-listgroupU"
    CREATE_GROUP = "-creategroup"
    JOIN_GROUP = "-joingroup"
    LEAVE_GROUP = "-leavegroup"

def exitCommand(client, message):
    if commandHasArguments(message):
        sendToClient(ServerMessages.ERROR_COMMAND_HAS_NOT_ARGUMENTS.format(command=ServerCommands.EXIT), client)
        return
    
    removeClient(client)
    return

def listAllUsers(client, message):
    if commandHasArguments(message):
        sendToClient(ServerMessages.ERROR_COMMAND_HAS_NOT_ARGUMENTS.format(command=ServerCommands.LIST_USERS), client)
        return

    users = []

    for name in clients.values():
        users.append(name)

    listUsers = f"Online: {users}"

    sendToClient(listUsers, client)
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
    return

def listAllGroups(client, message):
    if commandHasArguments(message):
        sendToClient(ServerMessages.ERROR_COMMAND_HAS_NOT_ARGUMENTS.format(command=ServerCommands.LIST_GROUPS), client)
        return

    groupsCurrent = []

    for groupName in groups.keys():
        groupsCurrent.append(groupName)

    listGroups = f"Groups: {groupsCurrent}"

    sendToClient(listGroups, client)
    return

def listAllUsersInGroup(client, message):
    if not commandHasArguments(message):
        sendToClient(ServerMessages.ERROR_COMMAND_EXPECTS_ARGUMENTS.format(command=ServerCommands.LIST_USERS_IN_GROUP), client)
        return
    
    groupName = message.replace(ServerCommands.LIST_USERS_IN_GROUP, "", 1).strip()

    if groupName not in groups:
        sendToClient(ServerMessages.GROUP_NOT_EXISTS, client)
        return
    
    groupUsers = []
    for users in groups[groupName]:
        groupUsers.append(users)
    
    listGroupsUsers = f"Group Users: {groupUsers}"

    sendToClient(listGroupsUsers, client)
    return

HOST = '127.0.0.1'
PORT = 55555

clients = {}
groups = {}

commands = {
    ServerCommands.EXIT: exitCommand,
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

def removeClient(client):
    if client in clients:
        del clients[client]
    
    client.close()

def receiveMessage(client):
    try:
        message = decodeMessage(client.recv(1024))

        if not message:
            return None

        return message
    except:
        return None

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

    print(ServerMessages.USER_CONNECTED.format(user=user))
    sendToAll(ServerMessages.USER_JOIN_CHAT.format(user=user), client)

    while True:
        message = receiveMessage(client)

        if not message:
            break

        command = getCommand(message)

        if command in commands:
            commands[command](client, message)
            continue

        messageFormatted = f"{user}: {message}"
        print(messageFormatted)
        sendToAll(messageFormatted, client)

    removeClient(client)
    print(ServerMessages.USER_DISCONNECTED.format(user=user))
    sendToAll(ServerMessages.USER_LEFT_CHAT.format(user=user), client)

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