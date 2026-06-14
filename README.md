# 💬 Chat Cliente-Servidor

Aplicação de chat em tempo real utilizando **Python** com comunicação via **sockets TCP**, suportando mensagens privadas, grupos e entrega de mensagens offline.

---

## 🚀 Como executar

**Requisitos:** Python 3.x

```bash
# 1. Inicie o servidor
python server.py

# 2. Em outro terminal, inicie o cliente
python client.py
```

O servidor roda por padrão em `127.0.0.1:55555`.

---

## 🔌 Conexão

Ao conectar, o cliente deve informar um **nickname** único. Caso o nome já esteja em uso, a conexão é recusada.

---

## 📋 Comandos disponíveis

| Comando | Descrição |
|---|---|
| `-help` | Exibe a lista de comandos disponíveis |
| `-exit` | Desconecta do servidor |
| `-listusers` | Lista todos os usuários online |
| `-listgroups` | Lista todos os grupos existentes |
| `-listgroupU <grupo>` | Lista os usuários de um grupo específico |
| `-creategroup <grupo>` | Cria um novo grupo |
| `-joingroup <grupo>` | Entra em um grupo existente |
| `-leavegroup <grupo>` | Sai de um grupo |
| `-msg U <nick> <mensagem>` | Envia mensagem privada para um usuário |
| `-msg G <grupo> <mensagem>` | Envia mensagem para um grupo |
| `-msgt C <mensagem>` | Broadcast para todos os usuários **online** |
| `-msgt D <mensagem>` | Envia para todos os usuários **offline** (entregue ao reconectar) |
| `-msgt T <mensagem>` | Envia para **todos** os usuários (online + offline) |

Qualquer texto que não seja um comando válido retorna uma mensagem de erro.

---

## 📦 Formato das mensagens

**Mensagem privada:**
```
[PV-MSG] (NickRemetente, DD/MM/AA HH:MM:SS): mensagem
```

**Mensagem de grupo:**
```
[GP-MSG] (NickRemetente, NomeGrupo, DD/MM/AA HH:MM:SS) mensagem
```

**Broadcast:**
```
(NickRemetente, DD/MM/AA HH:MM:SS) [BROADCAST] mensagem
```

---

## 📬 Mensagens offline

Caso o destinatário (usuário ou membro de grupo) esteja **offline** no momento do envio, a mensagem é armazenada no servidor. Ao reconectar, o usuário recebe automaticamente todas as mensagens pendentes.

---

## 🗂 Estrutura do projeto

```
├── server.py   # Lógica do servidor: conexões, comandos, grupos e mensagens offline
└── client.py   # Interface do cliente para conexão e envio de comandos
```

---

## 🛠 Tecnologias

- Python 3
- `socket` — comunicação TCP
- `threading` — múltiplos clientes simultâneos
- `datetime` — timestamp nas mensagens