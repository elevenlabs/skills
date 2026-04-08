# Widget Embedding

Add a voice AI agent to any website with the ElevenLabs conversation widget.

## Basic Embed

```html
<elevenlabs-convai agent-id="your-agent-id"></elevenlabs-convai>
<script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async type="text/javascript"></script>
```

This creates a floating button that users can click to start a voice conversation.

> **Note:** Widgets currently require public agents with authentication disabled. For authenticated flows, use the SDKs.

## Widget Attributes

### Required

| Attribute | Description |
|-----------|-------------|
| `agent-id` | Your ElevenLabs agent ID |
| `signed-url` | Alternative to `agent-id` when using signed URLs |

### Appearance

| Attribute | Description | Default |
|-----------|-------------|---------|
| `avatar-image-url` | URL for agent avatar image | ElevenLabs logo |
| `avatar-orb-color-1` | Primary orb gradient color | `#2792dc` |
| `avatar-orb-color-2` | Secondary orb gradient color | `#9ce6e6` |

### Text Labels

| Attribute | Description | Default |
|-----------|-------------|---------|
| `action-text` | Tooltip when hovering | "Talk to AI" |
| `start-call-text` | Button to start call | "Start call" |
| `end-call-text` | Button to end call | "End call" |
| `expand-text` | Expand chat button | "Open" |
| `collapse-text` | Collapse chat button | "Close" |
| `listening-text` | Listening state label | "Listening..." |
| `speaking-text` | Speaking state label | "Assistant speaking" |

### Behavior

| Attribute | Description | Default |
|-----------|-------------|---------|
| `variant` | Widget style: `compact` or `expanded` | `compact` |
| `server-location` | Server region (`us`, `eu-residency`, `in-residency`, `global`) | `us` |
| `dismissible` | Allow the user to minimize the widget | `false` |
| `disable-banner` | Hide "Powered by ElevenLabs" | `false` |

## Examples

### Custom Avatar

```html
<elevenlabs-convai
  agent-id="your-agent-id"
  avatar-image-url="https://example.com/your-avatar.png"
></elevenlabs-convai>
```

### Custom Colors

```html
<elevenlabs-convai
  agent-id="your-agent-id"
  avatar-orb-color-1="#ff6b6b"
  avatar-orb-color-2="#ffd93d"
></elevenlabs-convai>
```

### Custom Text

```html
<elevenlabs-convai
  agent-id="your-agent-id"
  action-text="Chat with our AI assistant"
  start-call-text="Begin conversation"
  end-call-text="Hang up"
></elevenlabs-convai>
```

### Expanded Variant

```html
<elevenlabs-convai
  agent-id="your-agent-id"
  variant="expanded"
></elevenlabs-convai>
```

### Full Customization

```html
<elevenlabs-convai
  agent-id="your-agent-id"
  avatar-image-url="https://example.com/support-agent.png"
  avatar-orb-color-1="#4f46e5"
  avatar-orb-color-2="#818cf8"
  action-text="Talk to Support"
  start-call-text="Start voice chat"
  end-call-text="End conversation"
  expand-text="Open assistant"
  collapse-text="Minimize"
></elevenlabs-convai>
```

## CSS Customization

The widget uses Shadow DOM but exposes CSS custom properties:

```css
elevenlabs-convai {
  --elevenlabs-convai-widget-width: 400px;
  --elevenlabs-convai-widget-height: 600px;
}
```

### Positioning

By default, the widget appears in the bottom-right corner. Override with CSS:

```css
elevenlabs-convai {
  position: fixed;
  bottom: 20px;
  right: 20px;
  /* Or position differently */
  left: 20px;
  right: auto;
}
```

### Z-Index

```css
elevenlabs-convai {
  z-index: 9999;
}
```

## JavaScript Control

Access the widget element to control it programmatically:

```html
<elevenlabs-convai id="my-widget" agent-id="your-agent-id"></elevenlabs-convai>

<script>
  const widget = document.getElementById("my-widget");

  // Start a conversation
  widget.startConversation();

  // End the conversation
  widget.endConversation();

  // Listen for events
  widget.addEventListener("conversationStarted", () => {
    console.log("Conversation started");
  });

  widget.addEventListener("conversationEnded", () => {
    console.log("Conversation ended");
  });
</script>
```

### Custom Trigger Button

Hide the default widget and use your own button:

```html
<style>
  elevenlabs-convai {
    display: none;
  }
</style>

<button onclick="document.getElementById('widget').startConversation()">
  Talk to AI
</button>

<elevenlabs-convai id="widget" agent-id="your-agent-id"></elevenlabs-convai>
```

## Authentication

For agents with authentication enabled, pass a signed URL:

```html
<elevenlabs-convai id="widget" agent-id="your-agent-id"></elevenlabs-convai>

<script>
  async function startAuthenticatedConversation() {
    // Get signed URL from your backend
    const response = await fetch("/api/get-signed-url");
    const { signedUrl } = await response.json();

    const widget = document.getElementById("widget");
    widget.setAttribute("signed-url", signedUrl);
    widget.startConversation();
  }
</script>
```

Your backend:

```python
@app.get("/api/get-signed-url")
def get_signed_url():
    signed_url = client.conversational_ai.conversations.get_signed_url(
        agent_id="your-agent-id"
    )
    return {"signedUrl": signed_url.signed_url}
```

## Mobile Considerations

### Responsive Positioning

```css
/* Desktop: bottom-right */
elevenlabs-convai {
  position: fixed;
  bottom: 20px;
  right: 20px;
}

/* Mobile: full-width bottom */
@media (max-width: 768px) {
  elevenlabs-convai {
    bottom: 0;
    right: 0;
    left: 0;
    --elevenlabs-convai-widget-width: 100%;
  }
}
```

### Touch-Friendly

The widget is touch-optimized by default. For better mobile UX:

```css
@media (max-width: 768px) {
  elevenlabs-convai {
    /* Larger touch target */
    transform: scale(1.1);
    transform-origin: bottom right;
  }
}
```

## Multiple Widgets

You can have multiple widgets for different agents:

```html
<elevenlabs-convai
  agent-id="support-agent-id"
  action-text="Support"
  style="right: 20px"
></elevenlabs-convai>

<elevenlabs-convai
  agent-id="sales-agent-id"
  action-text="Sales"
  style="right: 100px"
></elevenlabs-convai>
```

## Framework Integration

### React

```jsx
function App() {
  useEffect(() => {
    // Load widget script
    const script = document.createElement("script");
    script.src = "https://unpkg.com/@elevenlabs/convai-widget-embed";
    script.async = true;
    document.body.appendChild(script);

    return () => document.body.removeChild(script);
  }, []);

  return (
    <div>
      <elevenlabs-convai agent-id="your-agent-id"></elevenlabs-convai>
    </div>
  );
}
```

### Vue

```vue
<template>
  <div>
    <elevenlabs-convai agent-id="your-agent-id"></elevenlabs-convai>
  </div>
</template>

<script setup>
import { onMounted } from "vue";

onMounted(() => {
  const script = document.createElement("script");
  script.src = "https://unpkg.com/@elevenlabs/convai-widget-embed";
  script.async = true;
  document.body.appendChild(script);
});
</script>
```

### Next.js

```jsx
import Script from "next/script";

export default function Page() {
  return (
    <>
      <Script
        src="https://unpkg.com/@elevenlabs/convai-widget-embed"
        strategy="lazyOnload"
      />
      <elevenlabs-convai agent-id="your-agent-id"></elevenlabs-convai>
    </>
  );
}
```

## Troubleshooting

### Widget Not Appearing

1. Check that the agent ID is correct
2. Verify the script is loaded (check Network tab)
3. Check for JavaScript errors in console
4. Ensure no CSS is hiding the widget

### Audio Issues

1. Ensure HTTPS (microphone requires secure context)
2. Check browser permissions for microphone
3. Test in a supported browser (Chrome, Firefox, Safari, Edge)

### CORS Errors

If using authentication, ensure your domain is in the agent's allowlist:

```python
platform_settings={
    "auth": {
        "enable_auth": True,
        "allowlist": ["https://yourdomain.com"]
    }
}
```
