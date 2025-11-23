# Video

## Overview

Build video conferencing applications with SignalWire's Video API, supporting rooms with up to 300 participants, custom layouts, and low latency (<50ms round-trip).

## Key Concepts

- **Room**: A video conference space
- **Room Token**: Limited-scope token for client access (never expose API token to browser)
- **Layout**: Visual arrangement of participant videos
- **Moderator**: Participant with full control
- **Member/Guest**: Regular participant with limited permissions

## Creating Video Rooms

### Option 1: Via REST API (Server-Side)

```
POST https://{space}.signalwire.com/api/video/rooms
```

#### Python Example

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["requests"]
# ///

import os
import requests
from requests.auth import HTTPBasicAuth

project_id = os.getenv('SIGNALWIRE_PROJECT_ID')
api_token = os.getenv('SIGNALWIRE_API_TOKEN')
space_url = os.getenv('SIGNALWIRE_SPACE_URL')

response = requests.post(
    f"{space_url}/api/video/rooms",
    auth=HTTPBasicAuth(project_id, api_token),
    headers={"Content-Type": "application/json"},
    json={
        "name": "my-meeting-room",
        "display_name": "Team Meeting",
        "max_participants": 50,
        "quality": "1080p",
        "layout": "grid-responsive",
        "enable_chat": True,
        "enable_room_previews": True
    }
)

if response.status_code == 201:
    room = response.json()
    print(f"Room created: {room['id']}")
    print(f"Room name: {room['name']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

#### Node.js Example

```javascript
const axios = require('axios');

const projectId = process.env.SIGNALWIRE_PROJECT_ID;
const apiToken = process.env.SIGNALWIRE_API_TOKEN;
const spaceUrl = process.env.SIGNALWIRE_SPACE_URL;

async function createRoom() {
  try {
    const response = await axios.post(
      `${spaceUrl}/api/video/rooms`,
      {
        name: 'my-meeting-room',
        display_name: 'Team Meeting',
        max_participants: 50,
        quality: '1080p',
        layout: 'grid-responsive',
        enable_chat: true,
        enable_room_previews: true
      },
      {
        auth: {
          username: projectId,
          password: apiToken
        },
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );

    console.log(`Room created: ${response.data.id}`);
    console.log(`Room name: ${response.data.name}`);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

createRoom();
```

### Room Parameters

- **name**: Unique room identifier (slug)
- **display_name**: Human-readable name
- **max_participants**: Maximum number of participants (default: unlimited)
- **quality**: Video quality (`720p`, `1080p`, `1440p`)
- **layout**: Default layout (`grid-responsive`, `highlight-1-responsive`, etc.)
- **enable_chat**: Enable text chat (default: `true`)
- **enable_room_previews**: Show video preview before joining (default: `true`)
- **record_on_start**: Auto-start recording (default: `false`)

### Option 2: Auto-Creation

Rooms are automatically created when requesting a token for a non-existent room.

### Option 3: Via Dashboard

1. Go to **Video** section in Dashboard
2. Click **Create Room**
3. Configure settings
4. Save

## Room Tokens (Client Access)

**CRITICAL**: Never expose API tokens to browsers. Always use room tokens.

### Creating Room Tokens (Server-Side)

```
POST https://{space}.signalwire.com/api/video/room_tokens
```

#### Python Example

```python
response = requests.post(
    f"{space_url}/api/video/room_tokens",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "room_name": "my-meeting-room",
        "user_name": "Alice",
        "permissions": [
            "room.self.audio_mute",
            "room.self.video_mute"
        ]
    }
)

room_token = response.json()['token']
# Send this token to the browser
```

#### Node.js Example

```javascript
const response = await axios.post(
  `${spaceUrl}/api/video/room_tokens`,
  {
    room_name: 'my-meeting-room',
    user_name: 'Alice',
    permissions: [
      'room.self.audio_mute',
      'room.self.video_mute'
    ]
  },
  {
    auth: {
      username: projectId,
      password: apiToken
    }
  }
);

const roomToken = response.data.token;
// Send to browser
```

### Token Types

**Moderator Token** (full permissions):
```python
json={
    "room_name": "my-meeting-room",
    "user_name": "Moderator",
    "mod_permissions": True  # All permissions
}
```

**Guest Token** (limited permissions):
```python
json={
    "room_name": "my-meeting-room",
    "user_name": "Guest User",
    "permissions": [
        "room.self.audio_mute",
        "room.self.video_mute",
        "room.self.audio_unmute",
        "room.self.video_unmute"
    ]
}
```

### Common Permissions

- `room.self.audio_mute` / `room.self.audio_unmute`
- `room.self.video_mute` / `room.self.video_unmute`
- `room.member.remove` - Kick participants
- `room.recording` - Start/stop recording
- `room.screen_share` - Share screen
- `room.layout_change` - Change layout

## Browser Client (JavaScript)

### Installation

```bash
npm install @signalwire/js
```

### Basic Room Join

```html
<!DOCTYPE html>
<html>
<head>
  <title>Video Conference</title>
</head>
<body>
  <div id="video-container"></div>

  <script type="module">
    import { Video } from '@signalwire/js';

    async function joinRoom(roomToken) {
      const roomSession = new Video.RoomSession({
        token: roomToken,
        rootElementId: 'video-container',
        audio: true,
        video: true
      });

      // Event listeners
      roomSession.on('room.joined', () => {
        console.log('Joined room successfully');
      });

      roomSession.on('member.joined', (member) => {
        console.log(`${member.name} joined`);
      });

      roomSession.on('member.left', (member) => {
        console.log(`${member.name} left`);
      });

      // Join the room
      await roomSession.join();
    }

    // Get token from your server
    const response = await fetch('/api/get-room-token');
    const { token } = await response.json();

    joinRoom(token);
  </script>
</body>
</html>
```

### Full-Featured Client

```javascript
import { Video } from '@signalwire/js';

let roomSession;
let screenShareSession;

async function setupVideoConference(roomToken) {
  roomSession = new Video.RoomSession({
    token: roomToken,
    rootElementId: 'video-container',
    audio: true,
    video: true
  });

  // Event handlers
  roomSession.on('room.joined', handleRoomJoined);
  roomSession.on('room.updated', handleRoomUpdated);
  roomSession.on('member.joined', handleMemberJoined);
  roomSession.on('member.left', handleMemberLeft);
  roomSession.on('member.talking', handleMemberTalking);
  roomSession.on('layout.changed', handleLayoutChanged);

  await roomSession.join();
}

function handleRoomJoined(e) {
  console.log('Room joined:', e.room);
  document.getElementById('participant-count').textContent =
    `Participants: ${e.room.members.length}`;
}

function handleMemberJoined(e) {
  console.log('Member joined:', e.member.name);
  updateParticipantList();
}

function handleMemberLeft(e) {
  console.log('Member left:', e.member.name);
  updateParticipantList();
}

function handleMemberTalking(e) {
  // Highlight active speaker
  document.querySelectorAll('.participant').forEach(el => {
    el.classList.remove('talking');
  });
  document.getElementById(`participant-${e.member.id}`)?.classList.add('talking');
}

// Controls
async function toggleMicrophone() {
  if (roomSession.audioMuted) {
    await roomSession.audioUnmute();
  } else {
    await roomSession.audioMute();
  }
}

async function toggleCamera() {
  if (roomSession.videoMuted) {
    await roomSession.videoUnmute();
  } else {
    await roomSession.videoMute();
  }
}

async function leaveRoom() {
  await roomSession.leave();
}

async function startScreenShare() {
  screenShareSession = new Video.RoomSession({
    token: roomToken,
    rootElementId: 'screen-share-container',
    audio: false,
    video: {
      deviceId: 'screen'
    }
  });

  await screenShareSession.join();
}

async function stopScreenShare() {
  await screenShareSession?.leave();
  screenShareSession = null;
}

async function changeLayout(layoutName) {
  await roomSession.setLayout({ name: layoutName });
}

// Attach to buttons
document.getElementById('mute-btn').onclick = toggleMicrophone;
document.getElementById('camera-btn').onclick = toggleCamera;
document.getElementById('leave-btn').onclick = leaveRoom;
document.getElementById('screenshare-btn').onclick = startScreenShare;
```

## Layouts

### Available Layouts

- **grid-responsive**: Equally-sized participant tiles
- **highlight-1-responsive**: One large video, others in sidebar
- **highlight-2-responsive**: Two large videos, others in sidebar
- **full-screen**: Single participant fills screen

### Changing Layout (Browser)

```javascript
await roomSession.setLayout({
  name: 'highlight-1-responsive'
});
```

### Changing Layout (REST API)

```python
response = requests.put(
    f"{space_url}/api/video/rooms/{room_id}",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "layout": "grid-responsive"
    }
)
```

## Recording

### Start Recording (Browser)

```javascript
await roomSession.startRecording();
```

### Stop Recording (Browser)

```javascript
await roomSession.stopRecording();
```

### Auto-Record on Room Creation

```python
response = requests.post(
    f"{space_url}/api/video/rooms",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "name": "recorded-meeting",
        "record_on_start": True
    }
)
```

### Access Recordings

Recordings are available in Dashboard > Video > Recordings

## Complete Backend + Frontend Example

### Backend (Python/Flask)

```python
from flask import Flask, request, jsonify, render_template
import os
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

project_id = os.getenv('SIGNALWIRE_PROJECT_ID')
api_token = os.getenv('SIGNALWIRE_API_TOKEN')
space_url = os.getenv('SIGNALWIRE_SPACE_URL')

@app.route('/')
def index():
    return render_template('video.html')

@app.route('/api/create-room', methods=['POST'])
def create_room():
    data = request.json
    room_name = data.get('room_name')

    # Create room
    response = requests.post(
        f"{space_url}/api/video/rooms",
        auth=HTTPBasicAuth(project_id, api_token),
        json={
            "name": room_name,
            "display_name": data.get('display_name', room_name),
            "max_participants": data.get('max_participants', 50)
        }
    )

    if response.status_code == 201:
        return jsonify(response.json())
    else:
        return jsonify({"error": response.text}), response.status_code

@app.route('/api/join-room', methods=['POST'])
def join_room():
    data = request.json
    room_name = data.get('room_name')
    user_name = data.get('user_name')
    is_moderator = data.get('is_moderator', False)

    # Create room token
    token_data = {
        "room_name": room_name,
        "user_name": user_name
    }

    if is_moderator:
        token_data["mod_permissions"] = True
    else:
        token_data["permissions"] = [
            "room.self.audio_mute",
            "room.self.video_mute",
            "room.self.audio_unmute",
            "room.self.video_unmute"
        ]

    response = requests.post(
        f"{space_url}/api/video/room_tokens",
        auth=HTTPBasicAuth(project_id, api_token),
        json=token_data
    )

    if response.status_code == 200:
        return jsonify({"token": response.json()['token']})
    else:
        return jsonify({"error": response.text}), response.status_code

if __name__ == '__main__':
    app.run(port=5000)
```

### Frontend (HTML/JavaScript)

```html
<!DOCTYPE html>
<html>
<head>
  <title>Video Conference</title>
  <style>
    #video-container {
      width: 100%;
      height: 600px;
      background: #000;
    }
    .controls {
      margin-top: 20px;
    }
    button {
      padding: 10px 20px;
      margin: 5px;
    }
  </style>
</head>
<body>
  <h1>Video Conference</h1>

  <div>
    <input type="text" id="username" placeholder="Your name">
    <input type="text" id="roomname" placeholder="Room name">
    <button onclick="joinRoom()">Join Room</button>
  </div>

  <div id="video-container"></div>

  <div class="controls">
    <button id="mute-btn" onclick="toggleMic()">Mute</button>
    <button id="camera-btn" onclick="toggleCamera()">Camera Off</button>
    <button id="leave-btn" onclick="leaveRoom()">Leave</button>
    <button onclick="changeLayout('grid-responsive')">Grid Layout</button>
    <button onclick="changeLayout('highlight-1-responsive')">Highlight Layout</button>
  </div>

  <script type="module">
    import { Video } from 'https://cdn.jsdelivr.net/npm/@signalwire/js@latest/dist/cdn/index.js';

    let roomSession;

    window.joinRoom = async function() {
      const username = document.getElementById('username').value;
      const roomname = document.getElementById('roomname').value;

      if (!username || !roomname) {
        alert('Please enter your name and room name');
        return;
      }

      // Get token from server
      const response = await fetch('/api/join-room', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          room_name: roomname,
          user_name: username,
          is_moderator: false
        })
      });

      const { token } = await response.json();

      // Join room
      roomSession = new Video.RoomSession({
        token: token,
        rootElementId: 'video-container',
        audio: true,
        video: true
      });

      roomSession.on('room.joined', () => {
        console.log('Joined room');
      });

      await roomSession.join();
    };

    window.toggleMic = async function() {
      if (roomSession.audioMuted) {
        await roomSession.audioUnmute();
        document.getElementById('mute-btn').textContent = 'Mute';
      } else {
        await roomSession.audioMute();
        document.getElementById('mute-btn').textContent = 'Unmute';
      }
    };

    window.toggleCamera = async function() {
      if (roomSession.videoMuted) {
        await roomSession.videoUnmute();
        document.getElementById('camera-btn').textContent = 'Camera Off';
      } else {
        await roomSession.videoMute();
        document.getElementById('camera-btn').textContent = 'Camera On';
      }
    };

    window.leaveRoom = async function() {
      await roomSession.leave();
      window.location.reload();
    };

    window.changeLayout = async function(layoutName) {
      await roomSession.setLayout({ name: layoutName });
    };
  </script>
</body>
</html>
```

## Managing Rooms

### List All Rooms

```python
response = requests.get(
    f"{space_url}/api/video/rooms",
    auth=HTTPBasicAuth(project_id, api_token)
)

rooms = response.json()['data']
for room in rooms:
    print(f"Room: {room['name']} - {room['display_name']}")
```

### Update Room Settings

```python
response = requests.put(
    f"{space_url}/api/video/rooms/{room_id}",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "max_participants": 100,
        "layout": "highlight-1-responsive"
    }
)
```

### Delete Room

```python
response = requests.delete(
    f"{space_url}/api/video/rooms/{room_id}",
    auth=HTTPBasicAuth(project_id, api_token)
)
```

## Best Practices

1. **Token Security**: Never expose API tokens to browsers - always use room tokens
2. **Token Generation**: Generate tokens server-side on-demand
3. **Permissions**: Use least-privilege permissions for guest tokens
4. **Quality**: Match video quality to user bandwidth
5. **Layout**: Start with responsive layouts for flexibility
6. **Recording**: Inform participants when recording is active
7. **Error Handling**: Handle network disconnections gracefully

## Next Steps

- [Webhooks & Events](webhooks-events.md) - Track video room events
- [Fabric & Relay](fabric-relay.md) - Advanced video integration
