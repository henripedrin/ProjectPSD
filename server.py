import socket, threading

class ServerMessages:
    SERVER_RUNNING = "Server running on {HOST}:{PORT}.\nWaiting for connections..."
    USER_CONNECTED = "[+] {name} connected."
    USER_DISCONNECTED = "[-] {name} disconnected."
    USER_JOIN_CHAT = "[Server] {name} joined the chat!"
    USER_LEFT_CHAT = "[Server] {name} left the chat."
    NICKNAME_ALREADY_EXISTS = "[Server] Nickname already in use!"

class ServerCommands:
    EXIT = "-exit"
    LIST_ALL_USERS = "-listAllUsers"

def exitCommand(client):
    removeClient(client)

def listAllUsers(client):
    users = []

    for name in clients.values():
        users.append(name)

    message = f"Online: {users}"

    sendToClient(encodeMessage(message), client)

HOST = '127.0.0.1'
PORT = 55555

clients = {}
commands = {
    ServerCommands.EXIT: exitCommand,
    ServerCommands.LIST_ALL_USERS: listAllUsers
            }

def sendToClient(message, client):
    client.send(message)

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
    name = receiveMessage(client)

    if not name:
        removeClient(client)
        return

    if nickNameExists(name):
        sendToClient(encodeMessage(ServerMessages.NICKNAME_ALREADY_EXISTS), client)
        client.close()
        return

    clients[client] = name

    print(ServerMessages.USER_CONNECTED.format(name=name))
    sendToAll(encodeMessage(ServerMessages.USER_JOIN_CHAT.format(name=name)), client)

    while True:
        message = receiveMessage(client)

        if not message:
            break

        if message in commands:
            commands[message](client)
            continue

        messageFormatted = f"{name}: {message}"
        print(messageFormatted)
        sendToAll(encodeMessage(messageFormatted), client)

    removeClient(client)
    print(ServerMessages.USER_DISCONNECTED.format(name=name))
    sendToAll(encodeMessage(ServerMessages.USER_LEFT_CHAT.format(name=name)), client)

def nickNameExists(name):
    if name in clients.values():
        return True

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