# Client Tools

Extend your agent with custom capabilities. Tools let the agent take actions beyond just talking.

## Tool Types

| Type | Execution | Use Case |
|------|-----------|----------|
| **Webhook** | Server-side via HTTP | Database queries, API calls, secure operations |
| **Client** | Browser-side JavaScript | UI updates, local storage, navigation |
| **System** | Built-in ElevenLabs | End call, transfer, standard actions |

## Where Tools Live

Tools are defined inside `conversation_config.agent.prompt`. Webhook and client tools go in the `tools` array. System tools go in `built_in_tools`:

```python
conversation_config={
    "agent": {
        "prompt": {
            "prompt": "You are helpful.",
            "llm": "gemini-2.0-flash",
            "tools": [...],            # Webhook and client tools
            "built_in_tools": {...}     # System tools (end_call, transfer, etc.)
        }
    }
}
```

## Webhook Tools

Execute server-side logic when the agent needs external data or actions.

### Basic Webhook

```python
agent = client.conversational_ai.agents.create(
    name="Weather Assistant",
    conversation_config={
        "agent": {
            "prompt": {
                "prompt": "You are a helpful assistant that can check the weather.",
                "llm": "gemini-2.0-flash",
                "tools": [{
                    "type": "webhook",
                    "name": "get_weather",
                    "description": "Get current weather for a city. Use when user asks about weather.",
                    "api_schema": {
                        "url": "https://api.example.com/weather",
                        "method": "POST",
                        "request_headers": {
                            "Authorization": "Bearer {{API_KEY}}"
                        },
                        "request_body_schema": {
                            "type": "object",
                            "properties": {
                                "city": {
                                    "type": "string",
                                    "description": "City name, e.g., 'San Francisco'"
                                },
                                "units": {
                                    "type": "string",
                                    "enum": ["celsius", "fahrenheit"],
                                    "description": "Temperature units"
                                }
                            },
                            "required": ["city"]
                        }
                    }
                }]
            }
        },
        "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}
    }
)
```

### Webhook Request Format

When the agent calls a webhook tool, ElevenLabs sends:

```json
{
  "tool_call_id": "call_abc123",
  "tool_name": "get_weather",
  "parameters": {
    "city": "San Francisco",
    "units": "fahrenheit"
  },
  "conversation_id": "conv_xyz789"
}
```

### Webhook Response Format

Your server should respond with:

```json
{
  "result": "The weather in San Francisco is 68°F and sunny."
}
```

Or for structured data:

```json
{
  "result": {
    "temperature": 68,
    "condition": "sunny",
    "humidity": 45
  }
}
```

### Webhook with Authentication

```python
# Inside conversation_config.agent.prompt.tools:
{
    "type": "webhook",
    "name": "lookup_order",
    "description": "Look up order status by order ID",
    "response_timeout_secs": 10,
    "api_schema": {
        "url": "https://api.mystore.com/orders/lookup",
        "method": "POST",
        "request_headers": {
            "Authorization": "Bearer {{ORDER_API_KEY}}",
            "X-Store-ID": "store_123"
        },
        "request_body_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order ID (e.g., ORD-12345)"
                }
            },
            "required": ["order_id"]
        }
    }
}
```

### Webhook Tool Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `response_timeout_secs` | int | `20` | Timeout in seconds (5-120) |
| `disable_interruptions` | bool | `false` | Prevent user interruptions during tool execution |
| `execution_mode` | string | `"immediate"` | `immediate`, `post_tool_speech`, or `async` |
| `tool_call_sound` | string | - | Sound during execution: `typing`, `elevator1`-`elevator4` |
| `force_pre_tool_speech` | bool | `false` | Force agent to speak before executing tool |
| `tool_error_handling_mode` | string | `"auto"` | `auto`, `summarized`, `passthrough`, or `hide` |

**Note:** The default `api_schema.method` is `GET`. Always set `"method": "POST"` explicitly for webhook tools that send request bodies.

### Server Implementation (Node.js)

```javascript
app.post("/webhook/get_weather", async (req, res) => {
  const { parameters, conversation_id } = req.body;
  const { city, units = "fahrenheit" } = parameters;

  // Fetch weather from your data source
  const weather = await weatherService.get(city, units);

  res.json({
    result: `It's ${weather.temp}°${units === "celsius" ? "C" : "F"} and ${weather.condition} in ${city}.`,
  });
});
```

### Server Implementation (Python)

```python
@app.post("/webhook/get_weather")
async def get_weather(request: Request):
    data = await request.json()
    city = data["parameters"]["city"]
    units = data["parameters"].get("units", "fahrenheit")

    # Fetch weather from your data source
    weather = weather_service.get(city, units)

    return {
        "result": f"It's {weather['temp']}°{'C' if units == 'celsius' else 'F'} and {weather['condition']} in {city}."
    }
```

## Client Tools

Execute JavaScript in the user's browser. Useful for UI updates, navigation, or accessing browser APIs.

### Defining Client Tools

Client tools are registered when starting a conversation:

```javascript
import { Conversation } from "@elevenlabs/client";

const conversation = await Conversation.startSession({
  agentId: "your-agent-id",
  clientTools: {
    show_product: async ({ productId }) => {
      // Update UI to show product
      const modal = document.getElementById("product-modal");
      modal.innerHTML = await fetchProductCard(productId);
      modal.showModal();
      return { success: true, message: "Showing product" };
    },

    navigate_to: async ({ page }) => {
      // Navigate to a page
      window.location.href = `/${page}`;
      return { success: true };
    },

    save_preference: async ({ key, value }) => {
      // Store in localStorage
      localStorage.setItem(key, value);
      return { saved: true };
    },
  },
});
```

### Registering Client Tools with Agent

Tell the agent about available client tools in `conversation_config.agent.prompt.tools`:

```python
agent = client.conversational_ai.agents.create(
    name="Shopping Assistant",
    conversation_config={
        "agent": {
            "prompt": {
                "prompt": """You are a shopping assistant.
When users want to see a product, use show_product.
When users want to go somewhere, use navigate_to.""",
                "llm": "gemini-2.0-flash",
                "tools": [
                    {
                        "type": "client",
                        "name": "show_product",
                        "description": "Display a product card to the user",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "productId": {
                                    "type": "string",
                                    "description": "Product ID to display"
                                }
                            },
                            "required": ["productId"]
                        }
                    },
                    {
                        "type": "client",
                        "name": "navigate_to",
                        "description": "Navigate user to a different page",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "page": {
                                    "type": "string",
                                    "enum": ["cart", "checkout", "account", "home"],
                                    "description": "Page to navigate to"
                                }
                            },
                            "required": ["page"]
                        }
                    }
                ]
            }
        },
        "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}
    }
)
```

### Client Tool Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `expects_response` | bool | `false` | Whether the tool returns data to the agent |

### Client Tool Return Values

Return data that the agent can use in conversation:

```javascript
clientTools: {
  check_cart: async () => {
    const cart = JSON.parse(localStorage.getItem("cart") || "[]");
    return {
      itemCount: cart.length,
      total: cart.reduce((sum, item) => sum + item.price, 0),
      items: cart.map((item) => item.name),
    };
  };
}
```

The agent receives this data and can say: "You have 3 items in your cart totaling $45.99."

## System Tools (built_in_tools)

Built-in tools provided by ElevenLabs. These are configured in `conversation_config.agent.prompt.built_in_tools` (not in the `tools` array):

```python
"built_in_tools": {
    "end_call": {},
    "transfer_to_number": {...},
    "transfer_to_agent": {...},
    "language_detection": {},
    "skip_turn": {},
    "voicemail_detection": {...},
    "play_keypad_touch_tone": {},
    "search_documentation": {...}
}
```

### end_call

Ends the current conversation:

```python
"built_in_tools": {
    "end_call": {}
}
```

The agent can say "Goodbye!" and then end the call programmatically.

### transfer_to_number

Transfer to a phone number (requires telephony integration):

```python
"built_in_tools": {
    "transfer_to_number": {
        "transfers": [{
            "transfer_destination": {"type": "phone", "phone_number": "+1234567890"},
            "condition": "User asks to speak with a human agent"
        }]
    }
}
```

### transfer_to_agent

Transfer to another ElevenLabs agent:

```python
"built_in_tools": {
    "transfer_to_agent": {
        "transfers": [{
            "agent_id": "other-agent-id",
            "condition": "User asks about sales"
        }]
    }
}
```

## Best Practices

### Tool Descriptions

Write clear descriptions so the LLM knows when to use tools:

```python
# Good - specific and actionable
"description": "Look up order status. Use when customer asks about their order, delivery, or shipping."

# Bad - vague
"description": "Order tool"
```

### Parameter Descriptions

Help the LLM extract correct values:

```python
"parameters": {
    "type": "object",
    "properties": {
        "order_id": {
            "type": "string",
            "description": "Order ID in format ORD-XXXXX (e.g., ORD-12345)"
        },
        "email": {
            "type": "string",
            "description": "Customer email address for verification"
        }
    }
}
```

### Error Handling

Return helpful error messages:

```javascript
// Server webhook
app.post("/webhook/lookup_order", async (req, res) => {
  const { order_id } = req.body.parameters;

  const order = await db.orders.find(order_id);

  if (!order) {
    return res.json({
      result: {
        error: true,
        message: `Order ${order_id} not found. Please verify the order ID.`,
      },
    });
  }

  res.json({ result: order });
});
```

### Timeouts

Set reasonable timeouts for webhooks using `response_timeout_secs` (5-120 seconds, default 20):

```python
{
    "type": "webhook",
    "name": "slow_operation",
    "description": "Run a slow operation",
    "response_timeout_secs": 30,
    "api_schema": {
        "url": "https://api.example.com/slow-operation",
        "method": "POST"
    }
}
```

## Complete Example

```python
agent = client.conversational_ai.agents.create(
    name="E-commerce Assistant",
    conversation_config={
        "agent": {
            "first_message": "Hi! How can I help you today?",
            "language": "en",
            "prompt": {
                "prompt": """You are an e-commerce support assistant.

Available actions:
- lookup_order: Check order status
- show_product: Display products to customer
- end_call: End conversation politely
- transfer_to_number: Transfer to human support

Always verify order ID before lookup. Offer transfer for complex issues.""",
                "llm": "gemini-2.0-flash",
                "tools": [
                    # Webhook: Server-side order lookup
                    {
                        "type": "webhook",
                        "name": "lookup_order",
                        "description": "Look up order status by order ID or email",
                        "api_schema": {
                            "url": "https://api.mystore.com/orders/lookup",
                            "method": "POST",
                            "request_headers": {"Authorization": "Bearer {{API_KEY}}"},
                            "request_body_schema": {
                                "type": "object",
                                "properties": {
                                    "order_id": {"type": "string"},
                                    "email": {"type": "string"}
                                }
                            }
                        }
                    },
                    # Client: Browser-side product display
                    {
                        "type": "client",
                        "name": "show_product",
                        "description": "Display product details to the customer",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string"}
                            },
                            "required": ["product_id"]
                        }
                    }
                ],
                "built_in_tools": {
                    "end_call": {},
                    "transfer_to_number": {
                        "transfers": [{
                            "transfer_destination": {"type": "phone", "phone_number": "+1234567890"},
                            "condition": "User asks for human support"
                        }]
                    }
                }
            }
        },
        "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb", "model_id": "eleven_flash_v2_5"}
    }
)
```
