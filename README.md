# Trivia King - Python Multiplayer Network Game

---

## Overview
**Trivia King** is a multiplayer trivia game implemented over a custom TCP/UDP protocol in Python.

Players auto-discover a server over the LAN via UDP broadcasting, then join a trivia game where they answer Pokémon-themed True/False questions. Last player standing wins!

Originally developed as a university networking project.

---

## Features
-  **Client-server architecture** (TCP gameplay + UDP discovery)
-  **Multiple players support** (each in its own thread)
-  **Human-controlled players** (keyboard inputs)
-  **Bot players** (automatic random answers)
-  **Leaderboard tracking** (Top 10 scores across games)
-  **Resilient communication** (handles disconnections gracefully)
-  **Colored terminal output** for better UX

---

## Technologies
- Python 3
- TCP Sockets
- UDP Broadcast
- Multithreading
- Object-Oriented Programming

---

## How to Run

### 1. Start the Server
```bash
python server.py
```

Server starts broadcasting offers across LAN on UDP port 13117 and listens for TCP connections from clients.

Server listens 

### 2. Run the Client
```bash
python humanclientrun.py
```
### Playing as a Human Client

- A **random player name** will be assigned to you automatically when you join.
- You will **manually answer** True/False trivia questions during the game.
- To answer a question, **press one of the following keys**:

| Key Press | Meaning |
|:---|:---|
| `y`, `Y`, `T`, `1` | Answer **True** |
| `n`, `N`, `F`, `0` | Answer **False** |

---
