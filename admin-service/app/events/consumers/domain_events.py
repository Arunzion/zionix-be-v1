import json
import logging
import asyncio
from typing import Dict, Any, Callable, Coroutine

from app.events.kafka_client import get_consumer

logger = logging.getLogger(__name__)

# Type for event handlers
EventHandler = Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]

# Registry of event handlers
event_handlers: Dict[str, EventHandler] = {}

def register_event_handler(event_type: str, handler: EventHandler) -> None:
    """
    Register a handler function for a specific event type
    
    Args:
        event_type: The type of event to handle
        handler: The async function that will handle the event
    """
    event_handlers[event_type] = handler
    logger.info(f"Registered handler for event type: {event_type}")

async def process_event(event_data: Dict[str, Any]) -> None:
    """
    Process an event by routing it to the appropriate handler
    
    Args:
        event_data: The event data as a dictionary
    """
    event_type = event_data.get("event_type")
    if not event_type:
        logger.warning(f"Received event without event_type: {event_data}")
        return
    
    handler = event_handlers.get(event_type)
    if not handler:
        logger.warning(f"No handler registered for event type: {event_type}")
        return
    
    try:
        await handler(event_data)
    except Exception as e:
        logger.error(f"Error processing {event_type} event: {str(e)}")

async def start_consumer() -> None:
    """
    Start the Kafka consumer to listen for domain events
    """
    consumer = await get_consumer("domain-events")
    
    try:
        logger.info("Domain events consumer started")
        while True:
            try:
                # Get batch of messages
                messages = await consumer.getmany(timeout_ms=1000)
                
                for partition, message_list in messages.items():
                    for message in message_list:
                        try:
                            # Parse message value as JSON
                            event_json = message.value.decode("utf-8")
                            event_data = json.loads(event_json)
                            
                            # Process the event
                            await process_event(event_data)
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse event as JSON: {message.value}")
                        except Exception as e:
                            logger.error(f"Error processing message: {str(e)}")
            
            except Exception as e:
                logger.error(f"Error consuming messages: {str(e)}")
                # Brief pause before retry
                await asyncio.sleep(1)
    
    finally:
        # Ensure consumer is closed on exit
        await consumer.stop()
        logger.info("Domain events consumer stopped")

# Example event handler registration
async def handle_domain_created(event_data: Dict[str, Any]) -> None:
    """
    Handle domain_created events
    
    Args:
        event_data: The event data
    """
    domain_id = event_data.get("domain_id")
    domain_name = event_data.get("domain_name")
    
    logger.info(f"Processing domain_created event for domain {domain_id}: {domain_name}")
    # Implement business logic for handling domain creation
    # For example, provisioning resources, sending notifications, etc.

# Register event handlers
register_event_handler("domain_created", handle_domain_created)