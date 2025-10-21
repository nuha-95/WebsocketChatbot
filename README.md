# WebSocket Chatbot

A real-time chat application built with FastAPI and WebSockets.

## Features

- Real-time messaging using WebSockets
- Multiple client support
- Simple web-based chat interface
- Client ID assignment for user identification
- Broadcast messaging to all connected clients

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nuha-95/WebsocketChatbot.git
cd WebsocketChatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Open your browser and navigate to `http://127.0.0.1:8002`

3. Enter a client ID and start chatting!

## API Endpoints

- `GET /` - Serves the chat interface
- `WebSocket /ws/{client_id}` - WebSocket endpoint for real-time communication

## Technologies Used

- FastAPI - Web framework
- WebSockets - Real-time communication
- HTML/CSS/JavaScript - Frontend interface
- Uvicorn - ASGI server