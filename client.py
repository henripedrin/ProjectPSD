import socket, threading, os

class ClientMessages:
    CONNECTION_CLOSED = "[-] Connection closed by server..."
    ERROR_CONNECTING = "[!] Error connecting to the server."
    COULD_NOT_CONNECT = "[!] Could not connect to server at {HOST}:{PORT}"

    USERNAME = "Username: "
    USERNAME_MESSAGES = "You: "

HOST = '127.0.0.1'
PORT = 55555

history = []
historyLock = threading.Lock()

def sendMessage(client):
    while True:
        try:
            message = input()
            
            client.send(encodeMessage(message))
            addHistory(ClientMessages.USERNAME_MESSAGES + message)
        except:
            break

def receiveMessages(client):
    while True:
        try:
            message = decodeMessage(client.recv(1024))
            
            if not message:
                print(ClientMessages.CONNECTION_CLOSED)
                client.close()
                break

            addHistory(message)
        except:
            print(ClientMessages.ERROR_CONNECTING)
            client.close()
            break

def encodeMessage(message):
    return message.encode('utf-8')

def decodeMessage(message):
    return message.decode('utf-8')

def refreshTerminal():
        os.system('cls' if os.name == 'nt' else 'clear')

        for message in history:
            print(message)

def addHistory(message):
    with historyLock:
        history.append(message)
        refreshTerminal()
        
def startClient():
    name = input(ClientMessages.USERNAME)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except:
        print(ClientMessages.COULD_NOT_CONNECT.format(HOST=HOST, PORT=PORT))

    client.send(encodeMessage(name))

    thread = threading.Thread(
        target=receiveMessages, args=(client,)
    )

    thread.start()

    sendMessage(client)
        
if __name__ == "__main__":
    startClient()

