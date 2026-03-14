# E-Commerce Shopping Voice Assistant

## Problem/Feature Description

An online furniture store wants to add a voice assistant to their product pages. When a customer is browsing, they can click a button to start a voice conversation with the assistant. The assistant can answer questions about products, show product details in a modal on the page, add items to the cart, and navigate the customer to checkout when they are ready.

The store has a Node.js/Express backend that handles API authentication securely. The frontend is vanilla JavaScript running in the browser. The backend should provide a route that generates a secure connection token for the conversation. The frontend should start a voice session using that token and register browser-side tool handlers so the agent can trigger UI actions (showing products, updating the cart display, navigating pages).

On the server side, write the agent creation code that defines:
- The agent itself with a suitable voice and a prompt for a friendly shopping assistant
- Client tool definitions for: `show_product` (takes a productId), `add_to_cart` (takes productId and quantity), and `navigate_to` (takes a page name)
- An endpoint that creates a signed URL for the agent so the frontend can connect securely

On the client side, write the JavaScript that:
- Fetches the signed URL from the backend
- Starts a voice session with the agent
- Implements the browser-side handlers for all client tools
- Handles conversation events (messages, transcripts, errors)

## Output Specification

Produce two files:
- `server.js` - The Node.js/Express backend that creates the agent and serves the signed URL endpoint
- `client.js` - The browser JavaScript that connects to the agent and implements client-side tool handlers
