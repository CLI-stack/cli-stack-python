"""
Script: Webhook Handler (Flask)
What it does: Receives incoming webhook notifications from external services.
Webhooks are how services notify you of events (e.g., payment received, new commit).
Example: GitHub sends a webhook to your server when someone pushes code.

Install: pip install flask
Run: python 56_webhook_handler.py
Test: curl -X POST http://localhost:5000/webhook -H "Content-Type: application/json" -d '{"event":"push","repo":"my-project"}'
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# Store received webhooks in memory (use a database in production)
received_events = []

@app.route("/webhook", methods=["POST"])
def receive_webhook():
    """Endpoint that receives webhook notifications."""

    # Get the raw payload (JSON body)
    payload = request.get_json()

    if not payload:
        return jsonify({"error": "No JSON payload received"}), 400

    # Record the event with a timestamp
    event = {
        "received_at": datetime.now().isoformat(),
        "source_ip": request.remote_addr,  # who sent it
        "payload": payload
    }
    received_events.append(event)

    # Process the event based on its type
    event_type = payload.get("event", "unknown")
    print(f"\n[Webhook] Received '{event_type}' event at {event['received_at']}")
    print(f"  Payload: {json.dumps(payload, indent=2)}")

    # Handle different event types
    if event_type == "push":
        repo = payload.get("repo", "unknown")
        print(f"  → Code pushed to: {repo}")
    elif event_type == "payment":
        amount = payload.get("amount", 0)
        print(f"  → Payment received: ${amount}")
    else:
        print(f"  → Unknown event type: {event_type}")

    # Always respond quickly with 200 OK (webhook senders retry on failure)
    return jsonify({"status": "received", "event": event_type}), 200

@app.route("/webhook/events", methods=["GET"])
def list_events():
    """View all received webhook events."""
    return jsonify({
        "total_events": len(received_events),
        "events": received_events
    })

if __name__ == "__main__":
    print("Webhook handler running at http://localhost:5000/webhook")
    print("POST events to /webhook, view them at /webhook/events")
    app.run(debug=True, port=5000)
