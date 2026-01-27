# Client Tools

Extend your agent with custom capabilities. Tools let the agent take actions beyond just talking.

## Tool Types

| Type | Execution | Use Case |
|------|-----------|----------|
| **Webhook** | Server-side via HTTP | Database queries, API calls, secure operations |
| **Client** | Browser-side JavaScript | UI updates, local storage, navigation |
| **System** | Built-in ElevenLabs | End call, transfer, standard actions |

## Webhook Tools

Execute server-side logic when the agent needs external data or actions.

### Basic Webhook

```python
agent = client.conversational_ai.agents.create(
    name="Weather Assistant",
    tools=[{
        "type": "webhook",
        "name": "get_weather",
        "description": "Get current weather for a city. Use when user asks about weather.",
        "webhook": {
            "url": "https://api.example.com/weather",
            "method": "POST",
            "headers": {
                "Authorization": "Bearer {{API_KEY}}"
            }
        },
        "parameters": {
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
    }],
    prompt={
        "prompt": "You are a helpful assistant that can check the weather.",
        "llm": "gpt-4o-mini"
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
tools=[{
    "type": "webhook",
    "name": "lookup_order",
    "description": "Look up order status by order ID",
    "webhook": {
        "url": "https://api.mystore.com/orders/lookup",
        "method": "POST",
        "headers": {
            "Authorization": "Bearer {{ORDER_API_KEY}}",
            "X-Store-ID": "store_123"
        },
        "timeout_ms": 5000
    },
    "parameters": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "Order ID (e.g., ORD-12345)"
            }
        },
        "required": ["order_id"]
    }
}]
```

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

Tell the agent about available client tools in the agent config:

```python
agent = client.conversational_ai.agents.create(
    name="Shopping Assistant",
    tools=[
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
    ],
    prompt={
        "prompt": """You are a shopping assistant.
When users want to see a product, use show_product.
When users want to go somewhere, use navigate_to.""",
        "llm": "gpt-4o-mini"
    }
)
```

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

## System Tools

Built-in tools provided by ElevenLabs.

### end_call

Ends the current conversation:

```python
tools=[
    {"type": "system", "name": "end_call"}
]
```

The agent can say "Goodbye!" and then end the call programmatically.

### transfer_to_number

Transfer to a phone number (requires telephony integration):

```python
tools=[
    {
        "type": "system",
        "name": "transfer_to_number",
        "phone_number": "+1234567890",
        "description": "Transfer to human support"
    }
]
```

### transfer_to_agent

Transfer to another ElevenLabs agent:

```python
tools=[
    {
        "type": "system",
        "name": "transfer_to_agent",
        "agent_id": "other-agent-id",
        "description": "Transfer to sales specialist"
    }
]
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

Set reasonable timeouts for webhooks:

```python
"webhook": {
    "url": "https://api.example.com/slow-operation",
    "method": "POST",
    "timeout_ms": 10000  # 10 seconds
}
```

## Complete Example

```python
agent = client.conversational_ai.agents.create(
    name="E-commerce Assistant",
    tools=[
        # Webhook: Server-side order lookup
        {
            "type": "webhook",
            "name": "lookup_order",
            "description": "Look up order status by order ID or email",
            "webhook": {
                "url": "https://api.mystore.com/orders/lookup",
                "method": "POST",
                "headers": {"Authorization": "Bearer {{API_KEY}}"}
            },
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "email": {"type": "string"}
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
        },
        # System: Built-in call control
        {"type": "system", "name": "end_call"},
        {
            "type": "system",
            "name": "transfer_to_number",
            "phone_number": "+1234567890"
        }
    ],
    prompt={
        "prompt": """You are an e-commerce support assistant.

Available actions:
- lookup_order: Check order status
- show_product: Display products to customer
- end_call: End conversation politely
- transfer_to_number: Transfer to human support

Always verify order ID before lookup. Offer transfer for complex issues.""",
        "llm": "gpt-4o-mini"
    }
)
```
