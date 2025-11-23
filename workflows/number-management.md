# Number Management

## Overview

Provision, configure, and manage phone numbers for voice calls, SMS/MMS, and fax using SignalWire's REST API or Dashboard.

## Searching for Available Numbers

### Search by Area Code

```
GET https://{space}.signalwire.com/api/relay/rest/phone_numbers/search?areacode={code}
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

# Search for numbers in 555 area code
response = requests.get(
    f"{space_url}/api/relay/rest/phone_numbers/search",
    auth=HTTPBasicAuth(project_id, api_token),
    params={
        "areacode": "555",
        "limit": 10
    }
)

if response.status_code == 200:
    numbers = response.json()
    for number in numbers:
        print(f"Available: {number['phone_number']}")
        print(f"  Capabilities: Voice={number.get('voice')}, SMS={number.get('sms')}")
else:
    print(f"Error: {response.status_code}")
```

### Search by City/State

```python
response = requests.get(
    f"{space_url}/api/relay/rest/phone_numbers/search",
    auth=HTTPBasicAuth(project_id, api_token),
    params={
        "city": "New York",
        "state": "NY",
        "limit": 10
    }
)
```

### Search Toll-Free Numbers

```python
response = requests.get(
    f"{space_url}/api/relay/rest/phone_numbers/search",
    auth=HTTPBasicAuth(project_id, api_token),
    params={
        "toll_free": True,
        "limit": 10
    }
)
```

### Search Parameters

- **areacode**: 3-digit area code
- **city**: City name
- **state**: 2-letter state code (US)
- **country**: 2-letter country code (default: US)
- **toll_free**: `true` for toll-free numbers
- **contains**: Pattern to match in number (e.g., "1234")
- **limit**: Max results (default: 10)

## Purchasing Numbers

### Via REST API

```
POST https://{space}.signalwire.com/api/relay/rest/phone_numbers
```

#### Python Example

```python
# First, search for available numbers
search_response = requests.get(
    f"{space_url}/api/relay/rest/phone_numbers/search",
    auth=HTTPBasicAuth(project_id, api_token),
    params={"areacode": "555", "limit": 1}
)

available_number = search_response.json()[0]['phone_number']

# Purchase the number
purchase_response = requests.post(
    f"{space_url}/api/relay/rest/phone_numbers",
    auth=HTTPBasicAuth(project_id, api_token),
    headers={"Content-Type": "application/json"},
    json={
        "phone_number": available_number,
        "friendly_name": "My Business Line"
    }
)

if purchase_response.status_code == 201:
    number = purchase_response.json()
    print(f"Purchased: {number['phone_number']}")
    print(f"Number SID: {number['sid']}")
else:
    print(f"Error: {purchase_response.status_code}")
    print(purchase_response.text)
```

#### Node.js Example

```javascript
const axios = require('axios');

const projectId = process.env.SIGNALWIRE_PROJECT_ID;
const apiToken = process.env.SIGNALWIRE_API_TOKEN;
const spaceUrl = process.env.SIGNALWIRE_SPACE_URL;

async function purchaseNumber() {
  // Search for numbers
  const searchResponse = await axios.get(
    `${spaceUrl}/api/relay/rest/phone_numbers/search`,
    {
      auth: { username: projectId, password: apiToken },
      params: { areacode: '555', limit: 1 }
    }
  );

  const availableNumber = searchResponse.data[0].phone_number;

  // Purchase
  const purchaseResponse = await axios.post(
    `${spaceUrl}/api/relay/rest/phone_numbers`,
    {
      phone_number: availableNumber,
      friendly_name: 'My Business Line'
    },
    {
      auth: { username: projectId, password: apiToken },
      headers: { 'Content-Type': 'application/json' }
    }
  );

  console.log(`Purchased: ${purchaseResponse.data.phone_number}`);
}

purchaseNumber();
```

### Via Dashboard

1. Go to **Phone Numbers** section
2. Click **Buy a Number**
3. Search by area code, city, or pattern
4. Select number
5. Click **Buy**

## Configuring Numbers

### Voice Configuration

Configure what happens when someone calls your number.

#### Via REST API

```python
response = requests.put(
    f"{space_url}/api/relay/rest/phone_numbers/{number_sid}",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "voice_url": "https://example.com/swml",
        "voice_method": "GET",
        "voice_fallback_url": "https://example.com/fallback",
        "status_callback": "https://example.com/call-status"
    }
)
```

#### Configuration Parameters

- **voice_url**: SWML endpoint for incoming calls
- **voice_method**: HTTP method (`GET` or `POST`)
- **voice_fallback_url**: Backup URL if primary fails
- **status_callback**: Webhook for call status updates

#### Via Dashboard

1. Go to **Phone Numbers**
2. Select your number
3. Under **Voice Settings**:
   - Set **When a call comes in**: URL or Relay context
   - Set **Method**: GET or POST
4. Save

### Messaging Configuration

Configure SMS/MMS handling.

#### Via REST API

```python
response = requests.put(
    f"{space_url}/api/relay/rest/phone_numbers/{number_sid}",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "sms_url": "https://example.com/incoming-sms",
        "sms_method": "POST",
        "sms_fallback_url": "https://example.com/sms-fallback"
    }
)
```

#### Configuration Parameters

- **sms_url**: Webhook for incoming messages
- **sms_method**: HTTP method (`GET` or `POST`)
- **sms_fallback_url**: Backup URL if primary fails

#### Via Dashboard

1. Go to **Phone Numbers**
2. Select your number
3. Under **Messaging Settings**:
   - Set **When a message comes in**: Webhook URL
4. Save

### Relay Context Configuration

Route calls/messages to Relay application contexts:

```python
response = requests.put(
    f"{space_url}/api/relay/rest/phone_numbers/{number_sid}",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "relay_context": "office",  # Your Relay app context
        "relay_application": "main_ivr"
    }
)
```

Your Relay application listening on context "office" will receive events.

## Listing Numbers

### Get All Numbers

```python
response = requests.get(
    f"{space_url}/api/relay/rest/phone_numbers",
    auth=HTTPBasicAuth(project_id, api_token)
)

numbers = response.json()
for number in numbers:
    print(f"Number: {number['phone_number']}")
    print(f"  Name: {number.get('friendly_name')}")
    print(f"  Voice URL: {number.get('voice_url')}")
    print(f"  SMS URL: {number.get('sms_url')}")
```

### Get Specific Number

```python
response = requests.get(
    f"{space_url}/api/relay/rest/phone_numbers/{number_sid}",
    auth=HTTPBasicAuth(project_id, api_token)
)

number = response.json()
print(f"Number: {number['phone_number']}")
print(f"Capabilities: {number['capabilities']}")
```

## Updating Number Configuration

### Full Update Example

```python
def configure_business_number(number_sid):
    """Configure a number for business use"""

    config = {
        "friendly_name": "Main Business Line",

        # Voice configuration
        "voice_url": "https://api.example.com/swml/main-menu",
        "voice_method": "GET",
        "voice_fallback_url": "https://api.example.com/swml/fallback",
        "status_callback": "https://api.example.com/webhooks/call-status",

        # Messaging configuration
        "sms_url": "https://api.example.com/webhooks/incoming-sms",
        "sms_method": "POST",
        "sms_fallback_url": "https://api.example.com/webhooks/sms-fallback",

        # Emergency settings (E911)
        "emergency_address_sid": "AD1234567890abcdef1234567890abcdef"
    }

    response = requests.put(
        f"{space_url}/api/relay/rest/phone_numbers/{number_sid}",
        auth=HTTPBasicAuth(project_id, api_token),
        json=config
    )

    if response.status_code == 200:
        print("Number configured successfully")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
```

## Releasing Numbers

### Via REST API

```python
response = requests.delete(
    f"{space_url}/api/relay/rest/phone_numbers/{number_sid}",
    auth=HTTPBasicAuth(project_id, api_token)
)

if response.status_code == 204:
    print("Number released successfully")
else:
    print(f"Error: {response.status_code}")
```

**WARNING**: Released numbers cannot be recovered. They return to the available pool.

### Via Dashboard

1. Go to **Phone Numbers**
2. Select number
3. Click **Release Number**
4. Confirm

## Emergency Services (E911)

### Registering E911 Address

Required for voice-capable numbers in the US.

```python
# Create emergency address
address_response = requests.post(
    f"{space_url}/api/relay/rest/addresses",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "friendly_name": "Office Address",
        "customer_name": "Acme Corp",
        "street": "123 Main St",
        "city": "New York",
        "region": "NY",
        "postal_code": "10001",
        "iso_country": "US"
    }
)

address_sid = address_response.json()['sid']

# Associate with number
requests.put(
    f"{space_url}/api/relay/rest/phone_numbers/{number_sid}",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "emergency_address_sid": address_sid
    }
)
```

**IMPORTANT**: E911 registration may take 24-48 hours to activate.

## Caller ID

### Setting Caller ID Name (CNAM)

```python
response = requests.put(
    f"{space_url}/api/relay/rest/phone_numbers/{number_sid}",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "friendly_name": "Acme Corp Support"  # This becomes the CNAM
    }
)
```

**Note**: CNAM updates may take 24-72 hours to propagate across carriers.

## Number Porting

### Porting Numbers to SignalWire

1. **Dashboard**: Go to **Phone Numbers** → **Port Numbers**
2. Provide:
   - Numbers to port
   - Current carrier information
   - Account details
   - Letter of Authorization (LOA)
3. Submit port request
4. SignalWire coordinates with losing carrier
5. Port completes (usually 7-14 business days)

### Port Status

Check port status in Dashboard or via API:

```python
response = requests.get(
    f"{space_url}/api/relay/rest/port_requests/{port_request_id}",
    auth=HTTPBasicAuth(project_id, api_token)
)

port = response.json()
print(f"Status: {port['status']}")
print(f"Expected completion: {port['completion_date']}")
```

## Number Capabilities

### Checking Capabilities

```python
response = requests.get(
    f"{space_url}/api/relay/rest/phone_numbers/{number_sid}",
    auth=HTTPBasicAuth(project_id, api_token)
)

number = response.json()
capabilities = number['capabilities']

print(f"Voice: {capabilities.get('voice')}")
print(f"SMS: {capabilities.get('sms')}")
print(f"MMS: {capabilities.get('mms')}")
print(f"Fax: {capabilities.get('fax')}")
```

### Capability Types

- **voice**: Can make/receive calls
- **sms**: Can send/receive SMS
- **mms**: Can send/receive MMS (media messages)
- **fax**: Can send/receive fax

## Bulk Operations

### Purchase Multiple Numbers

```python
def purchase_numbers(area_code, count):
    """Purchase multiple numbers in the same area code"""

    # Search for available numbers
    search_response = requests.get(
        f"{space_url}/api/relay/rest/phone_numbers/search",
        auth=HTTPBasicAuth(project_id, api_token),
        params={"areacode": area_code, "limit": count}
    )

    available = search_response.json()

    purchased = []
    for number_data in available[:count]:
        purchase_response = requests.post(
            f"{space_url}/api/relay/rest/phone_numbers",
            auth=HTTPBasicAuth(project_id, api_token),
            json={
                "phone_number": number_data['phone_number'],
                "friendly_name": f"Line {len(purchased) + 1}"
            }
        )

        if purchase_response.status_code == 201:
            purchased.append(purchase_response.json())

    return purchased

# Purchase 5 numbers in 555 area code
numbers = purchase_numbers("555", 5)
print(f"Purchased {len(numbers)} numbers")
```

### Configure Multiple Numbers

```python
def configure_all_numbers(config):
    """Apply same configuration to all numbers"""

    # Get all numbers
    response = requests.get(
        f"{space_url}/api/relay/rest/phone_numbers",
        auth=HTTPBasicAuth(project_id, api_token)
    )

    numbers = response.json()

    for number in numbers:
        requests.put(
            f"{space_url}/api/relay/rest/phone_numbers/{number['sid']}",
            auth=HTTPBasicAuth(project_id, api_token),
            json=config
        )

    print(f"Configured {len(numbers)} numbers")

# Configure all numbers with same settings
configure_all_numbers({
    "voice_url": "https://example.com/swml",
    "sms_url": "https://example.com/incoming-sms"
})
```

## Number Groups & Pooling

### Creating Number Pools

Group numbers for round-robin or load balancing:

```python
number_pool = {
    'sales': ['+15551111111', '+15551111112', '+15551111113'],
    'support': ['+15552222221', '+15552222222'],
    'billing': ['+15553333331']
}

def get_next_available_number(department):
    """Get next available number from pool (simple round-robin)"""
    pool = number_pool.get(department, [])
    # Implement your logic (database, Redis, etc.)
    return pool[0] if pool else None
```

## Compliance & Best Practices

### A2P 10DLC Registration (US SMS)

For business messaging on local numbers:

1. **Register your brand** in Dashboard
2. **Create campaigns** describing use cases
3. **Associate numbers** with campaigns
4. **Wait for approval** (can take 1-2 weeks)

### International Numbers

Different countries have different requirements:

- **UK**: May require business address
- **Canada**: Similar to US
- **Other regions**: Check specific requirements in Dashboard

### Number Verification

Some carriers require ownership verification:

```python
# Initiate verification
response = requests.post(
    f"{space_url}/api/relay/rest/phone_numbers/{number_sid}/verify",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "verification_type": "sms",  # or "voice"
        "phone_number": "+15559876543"  # Number to receive code
    }
)

# Submit verification code
verify_response = requests.put(
    f"{space_url}/api/relay/rest/phone_numbers/{number_sid}/verify",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "verification_code": "123456"
    }
)
```

## Monitoring & Analytics

### Number Usage Tracking

```python
def get_number_usage(number_sid):
    """Get usage statistics for a number"""

    # Get calls for this number
    calls_response = requests.get(
        f"{space_url}/api/calling/calls",
        auth=HTTPBasicAuth(project_id, api_token),
        params={
            "to": number_sid,  # or "from" for outbound
            "start_date": "2025-01-01",
            "end_date": "2025-01-31"
        }
    )

    # Get messages for this number
    messages_response = requests.get(
        f"{space_url}/api/messaging/messages",
        auth=HTTPBasicAuth(project_id, api_token),
        params={
            "to": number_sid,
            "start_date": "2025-01-01",
            "end_date": "2025-01-31"
        }
    )

    return {
        "calls": len(calls_response.json()),
        "messages": len(messages_response.json())
    }
```

## Troubleshooting

### Common Issues

**Number not receiving calls**:
- Check voice_url is accessible via HTTPS
- Verify voice_url returns valid SWML
- Check Dashboard logs for errors

**SMS not working**:
- Verify number has SMS capability
- Check sms_url is configured
- Ensure A2P 10DLC registration (US)
- Check for carrier blocks

**E911 not registered**:
- Verify address is validated
- Wait 24-48 hours for activation
- Check address format matches requirements

## Next Steps

- [Inbound Call Handling](inbound-call-handling.md) - Configure voice_url with SWML
- [Messaging](messaging.md) - Configure sms_url webhooks
- [Webhooks & Events](webhooks-events.md) - Handle status callbacks
- [Outbound Calling](outbound-calling.md) - Use numbers for outbound calls
