# Video

## Overview

Build video conferencing applications with SignalWire's Video API, supporting rooms with up to 300 participants, custom layouts, and low latency (<50ms round-trip).

## Key Concepts

- **Video Room**: A Resource several people join at once. The REST reference calls it a conference room. Names are unique in a project and use letters, numbers, `_`, and `-`.
- **Address**: What the page dials. Copy `channels.video` from the address list (for example `/public/team-standup?channel=video`). SignalWire names the address after the room's display name and adds a suffix when that name is already taken, so don't build it from the room name.
- **Guest token**: Token the page signs in with. Issued for the room address. Never send the API token to the browser.
- **Layout**: Visual arrangement of participant videos

## Create a Video Room and join it

The room is the Resource. The server lists its address and issues a guest token for that address. The page signs in with the token and dials the address. All three REST calls accept a token with the **Voice**, **Messaging**, **Fax**, or **Video** permission. When phone callers join over Relay, the token also needs **Voice**.

### Create the room

```
POST https://{space}.signalwire.com/api/fabric/resources/conference_rooms
```

```python
import os
import requests
from requests.auth import HTTPBasicAuth

project_id = os.getenv('SIGNALWIRE_PROJECT_ID')
api_token = os.getenv('SIGNALWIRE_API_TOKEN')
space_url = os.getenv('SIGNALWIRE_SPACE_URL')

response = requests.post(
    f"{space_url}/api/fabric/resources/conference_rooms",
    auth=HTTPBasicAuth(project_id, api_token),
    headers={"Content-Type": "application/json"},
    json={"name": "team-standup", "enable_room_previews": False},
)

room_id = response.json()["id"]
```

`name` is unique in the project; a second create with the same name fails. Pass one: SWML `join_room` finds the room by `name`. Allowed characters: letters, numbers, `_`, `-`. `enable_room_previews` is optional and defaults to `false`. The response's top-level `id` is the Resource id.

In the Dashboard: **Resources** → **Add** → **Video Room**, enter a room name, choose **Build From Scratch**, then **Create**.

### List the address

```
GET https://{space}.signalwire.com/api/fabric/resources/{id}/addresses
```

```python
addresses = requests.get(
    f"{space_url}/api/fabric/resources/{room_id}/addresses",
    auth=HTTPBasicAuth(project_id, api_token),
).json()

address_id = addresses["data"][0]["id"]
room_address = addresses["data"][0]["channels"]["video"]
```

A new room has one address. `data[0].id` is the address id. Dial `data[0].channels.video`. Copy that value rather than building it from the room name.

### Issue a guest token

```
POST https://{space}.signalwire.com/api/fabric/guests/tokens
```

```python
response = requests.post(
    f"{space_url}/api/fabric/guests/tokens",
    auth=HTTPBasicAuth(project_id, api_token),
    headers={"Content-Type": "application/json"},
    json={"allowed_addresses": [address_id]},
)

guest_token = response.json()["token"]
```

Always pass `allowed_addresses` (up to 10 address ids). `expire_at` is optional; the token lasts two hours by default and places calls only.

### Join from the page

Serve the page over HTTPS or `localhost`. Browsers share the camera and microphone only on those origins. Sign in with the guest token and dial the copied address; see [Browser client](#browser-client-javascript).

Phone callers join with SWML `join_room`, passing the room's `name`, not its address. A name that matches no room creates a new empty room, and the caller waits alone in it. See [join_room](swml-methods.md#join_room).

## Browser Client (JavaScript)

### Installation

```bash
npm install @signalwire/js@latest rxjs
```

**RxJS is a peer dependency.** The SDK uses observables for all reactive state. Primer: `/docs/browser-sdk/v4/guides/rxjs-primer`.

### Two paths

**1. Full control** — your own UI, driven by `client.dial()` and observables.

```js
import { SignalWire, StaticCredentialProvider } from "@signalwire/js";

const client = new SignalWire(
  new StaticCredentialProvider({ token: guestToken })
);

// channels.video from the address list. Copy it; don't build it from the name.
await client.dial("/public/team-standup?channel=video", {
  audio: true,
  video: true,
  receiveVideo: true,
});
```

The `?channel=video` suffix turns on audio, video, and receiving video. Pass the three options anyway: without the suffix, receiving video is off by default. Serve the page over HTTPS or `localhost`. Browsers share the camera and microphone only on those origins.

**2. Web components** — one element, a styled working call UI:

```html
<sw-call-widget></sw-call-widget>
<sw-click-to-call></sw-click-to-call>
```

This is the right answer for marketing sites and click-to-call buttons. Do not hand-build a call UI for those. Guide: `/docs/browser-sdk/v4/guides/web-components`.

### Authentication

A room page signs in with the [guest token](#issue-a-guest-token) for the room address.

A **Subscriber Access Token (SAT)**, minted from the Dashboard's Subscribers section, signs a person in as a Subscriber instead.

For public widgets — chatbots, click-to-call — an **embed token** works with no backend at all. Guide: `/docs/browser-sdk/v4/guides/authentication`.

For a mobile or long-lived browser client, use device-bound tokens refreshed by proof of possession (DPoP):

```
POST /api/fabric/subscriber/devices/token
POST /api/fabric/subscriber/devices/refresh
```

### No-build option

Load as an ES module from a CDN that rewrites Node built-ins — `esm.sh`, `jspm.io`, `skypack`:

```html
<script type="module">
  import { SignalWire, StaticCredentialProvider } from "https://esm.sh/@signalwire/js@4";
</script>
```

**Pin a version rather than `@latest`** for script-tag setups, so a CDN update cannot change your page's behavior without a deploy.

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

1. **Token Security**: Never expose API tokens to browsers. A room page signs in with a guest token.
2. **Token Generation**: Generate tokens server-side on-demand
3. **Permissions**: Always pass `allowed_addresses` (up to 10). A guest token places calls only.
4. **Quality**: Match video quality to user bandwidth
5. **Layout**: Start with responsive layouts for flexibility
6. **Recording**: Inform participants when recording is active
7. **Error Handling**: Handle network disconnections gracefully

## WebRTC as Native Resource

**Key Concept:** SignalWire treats WebRTC as an addressable first-class resource, just like SIP or PSTN.

### Advantages

- Browser-to-phone calls (no plugins required)
- Browser-to-SIP calls
- Browser-to-AI agent
- Browser-to-browser
- Unified addressing scheme

### Call Widget Embedding

Simple HTML embed for instant video calling:

```html
<div id="sw-video-container"></div>
<script>
!function(){
  var e=document.createElement("script");
  e.async=!0,
  e.src="https://YOURSPACE.signalwire.com/relay/sdk.js",
  document.head.appendChild(e);
}();
</script>
```

### Widget Parameters

```javascript
{
  token: "room_token_here",
  username: "Agent Name",
  theme: "dark", // or "light"
  audio: true,
  video: true,
  memberList: true,
  chat: true,
  devicePicker: false, // Skip device selection screen
  prejoin: false // Skip waiting room
}
```

## Room Session Monitoring

### Tracking Room Activity

```javascript
const { Video } = require('@signalwire/realtime-api');

async function monitorRoom() {
  const client = new Video.Client({
    project: process.env.SIGNALWIRE_PROJECT_ID,
    token: process.env.SIGNALWIRE_API_TOKEN
  });

  const roomSession = await client.video.roomSessions.get({
    roomName: 'support-room'
  });

  // Monitor member events
  roomSession.on('member.joined', (member) => {
    console.log(`${member.name} joined`);

    // Update UI, send notifications
    notifyAdmins(`${member.name} joined the room`);
  });

  roomSession.on('member.talking', (member) => {
    const talkTime = Date.now() - member.talkStartTime;

    // Track speaking time for analytics
    updateMetrics(member.name, talkTime);

    // Highlight active speaker in UI
    highlightSpeaker(member.id);
  });

  roomSession.on('member.left', (member) => {
    console.log(`${member.name} left`);

    // Calculate session duration
    const duration = Date.now() - member.joinTime;
    logMemberSession(member.name, duration);
  });

  roomSession.on('recording.started', () => {
    console.log('Recording started');

    // Notify all members
    notifyAllMembers('This session is now being recorded');
  });

  roomSession.on('recording.ended', (recording) => {
    console.log('Recording ended');

    // Process recording
    processRecording(recording.url);
  });
}
```

### Analytics Dashboard

```javascript
class RoomAnalytics {
  constructor(roomName) {
    this.roomName = roomName;
    this.members = {};
    this.talkingTime = {};
  }

  trackMember(member) {
    this.members[member.id] = {
      name: member.name,
      joinTime: Date.now(),
      leaveTime: null,
      talkingTime: 0
    };
  }

  updateTalkingTime(memberId, duration) {
    if (this.members[memberId]) {
      this.members[memberId].talkingTime += duration;
    }
  }

  getMemberLeft(memberId) {
    if (this.members[memberId]) {
      this.members[memberId].leaveTime = Date.now();
    }
  }

  generateReport() {
    return {
      roomName: this.roomName,
      totalMembers: Object.keys(this.members).length,
      members: Object.values(this.members).map(m => ({
        name: m.name,
        duration: (m.leaveTime || Date.now()) - m.joinTime,
        talkingTime: m.talkingTime,
        talkingPercentage: (m.talkingTime / ((m.leaveTime || Date.now()) - m.joinTime)) * 100
      }))
    };
  }
}
```

## Programmable Video Conference Setup

### Quick Dashboard Setup

1. Navigate to **Video** section in Dashboard
2. Click **Create New**
3. Configure:
   - **Room name**: `team-standup`
   - **Size**: Participants limit (e.g., 50)
   - **Layout**: Grid, spotlight, custom
   - **Quality settings**: 720p, 1080p, 1440p
   - **Recording on start**: Enable/disable
   - **Enable chat**: Yes/no
   - **Room previews**: Show/hide video before joining

### Embed in Website

```html
<!-- Simple iframe embed -->
<iframe
  src="https://YOURSPACE.signalwire.com/pvr/ROOM_TOKEN"
  width="100%"
  height="600px"
  allow="camera;microphone"
  style="border: none;"
></iframe>
```

### Token Management

```python
from flask import Flask, request, jsonify
import os
import requests
from requests.auth import HTTPBasicAuth
import hashlib
import time

app = Flask(__name__)

# Token cache to reduce API calls
token_cache = {}

@app.route('/api/get-video-token', methods=['POST'])
def get_video_token():
    data = request.json
    room_name = data.get('room_name')
    user_name = data.get('user_name')
    is_moderator = data.get('is_moderator', False)

    # Check cache (tokens valid for ~1 hour)
    cache_key = f"{room_name}:{user_name}:{is_moderator}"
    cached = token_cache.get(cache_key)

    if cached and cached['expires'] > time.time():
        return jsonify({"token": cached['token']})

    # Generate new token
    token_response = requests.post(
        f"{os.getenv('SIGNALWIRE_SPACE_URL')}/api/video/room_tokens",
        auth=HTTPBasicAuth(
            os.getenv('SIGNALWIRE_PROJECT_ID'),
            os.getenv('SIGNALWIRE_API_TOKEN')
        ),
        json={
            "room_name": room_name,
            "user_name": user_name,
            "mod_permissions": is_moderator,
            "permissions": [] if is_moderator else [
                "room.self.audio_mute",
                "room.self.video_mute",
                "room.self.audio_unmute",
                "room.self.video_unmute"
            ]
        }
    )

    if token_response.status_code == 200:
        token = token_response.json()['token']

        # Cache token
        token_cache[cache_key] = {
            'token': token,
            'expires': time.time() + 3600  # 1 hour
        }

        return jsonify({"token": token})
    else:
        return jsonify({"error": "Failed to generate token"}), 500
```

## Click-to-Call Widget Patterns

### Browser-Based Calling

```html
<div id="call-widget"></div>
<script src="https://cdn.signalwire.com/call-widget.js"></script>
<script>
SignalWire.CallWidget({
  token: 'YOUR_CLICK_TO_CALL_TOKEN',
  element: '#call-widget',
  resource: '/public/your-agent-address',
  theme: 'dark',
  callerId: 'Customer Support'
});
</script>
```

### Configuration

Get token from Dashboard > Click to Call:

```javascript
// Initialize click-to-call
const callWidget = SignalWire.CallWidget({
  // Token from Dashboard
  token: 'CTT_xxxxxxxxxxxxxxxxxxxxxxx',

  // Widget container
  element: '#call-widget',

  // Connect to AI agent or SWML script
  resource: '/public/support-agent',

  // Customization
  theme: 'dark',
  position: 'bottom-right',
  buttonText: 'Call Support',
  callerId: 'Website Visitor',

  // Audio/video settings
  audio: true,
  video: false
});

// Event handling
callWidget.on('call.started', () => {
  console.log('Call started');
});

callWidget.on('call.ended', () => {
  console.log('Call ended');
});
```

### No Server Infrastructure Needed

The click-to-call widget connects directly to:
- AI agents for conversational support
- SWML scripts for IVR flows
- Subscribers for direct agent calls

```yaml
# SWML for click-to-call routing
version: 1.0.0
sections:
  main:
    - answer: {}
    - ai:
        prompt: |
          You are a customer support agent.
          Help the caller with their questions.
          Transfer to a human if needed.
        functions:
          - name: transfer_to_human
            web_hook: "https://yourserver.com/transfer"
```

## Production Video Tips

### Quality Settings

```python
# Create room with optimal quality
response = requests.post(
    f"{space_url}/api/video/rooms",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "name": "high-quality-meeting",
        "quality": "1080p",  # or "720p", "1440p"
        "max_participants": 25,  # Lower for better quality
        "enable_simulcast": True  # Adaptive quality
    }
)
```

### Bandwidth Management

```javascript
// Client-side quality adaptation
roomSession.on('network.quality', (quality) => {
  if (quality === 'poor') {
    // Reduce quality
    roomSession.setVideoQuality('low');
  } else if (quality === 'good') {
    roomSession.setVideoQuality('high');
  }
});
```

### Recording Management

```python
@app.route('/video/recording-ready', methods=['POST'])
def handle_recording():
    data = request.json

    recording_url = data.get('recording_url')
    room_id = data.get('room_id')

    # Upload to cloud storage
    upload_to_s3(recording_url, f"recordings/{room_id}.mp4")

    # Send to participants
    participants = get_room_participants(room_id)
    for participant in participants:
        send_email(
            to=participant.email,
            subject='Meeting Recording Available',
            body=f'Your recording is ready: {recording_url}'
        )

    return jsonify({"status": "ok"}), 200
```

## Next Steps

- [Webhooks & Events](webhooks-events.md) - Track video room events
- [Fabric & Relay](fabric-relay.md) - Advanced video integration
- [Authentication](authentication-setup.md) - Token management and security
