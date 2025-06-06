import json
import logging
from typing import Optional

# Import Kafka producer
from app.events.kafka_client import get_producer

logger = logging.getLogger(__name__)

async def publish_application_created_event(application_id: int, application_name: str, domain_id: int) -> None:
    """
    Publishes an application created event to Kafka
    
    Args:
        application_id: The ID of the created application
        application_name: The name of the created application
        domain_id: The ID of the domain this application belongs to
    """
    try:
        # Create event payload
        event_data = {
            "event_type": "application_created",
            "application_id": application_id,
            "application_name": application_name,
            "domain_id": domain_id
        }
        
        # Serialize to JSON
        event_json = json.dumps(event_data)
        
        # Get Kafka producer
        producer = await get_producer()
        
        # Send message to Kafka topic
        await producer.send_and_wait(
            topic="application-events",
            value=event_json.encode("utf-8"),
            key=str(application_id).encode("utf-8")
        )
        
        logger.info(f"Published application_created event for application {application_id}")
    except Exception as e:
        logger.error(f"Failed to publish application_created event: {str(e)}")
        # In a production system, you might want to implement retry logic
        # or store failed events for later processing