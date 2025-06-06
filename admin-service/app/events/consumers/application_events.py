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
    Start the Kafka consumer to listen for application events
    """
    consumer = await get_consumer("application-events")
    
    try:
        logger.info("Application events consumer started")
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
        logger.info("Application events consumer stopped")

# Example event handler registration
async def handle_application_created(event_data: Dict[str, Any]) -> None:
    """
    Handle application_created events
    
    Args:
        event_data: The event data
    """
    application_id = event_data.get("application_id")
    application_name = event_data.get("application_name")
    domain_id = event_data.get("domain_id")
    
    logger.info(f"Processing application_created event for application {application_id}: {application_name} in domain {domain_id}")
    # Implement business logic for handling application creation
    # For example, provisioning resources, sending notifications, etc.

# Register event handlers
register_event_handler("application_created", handle_application_created)