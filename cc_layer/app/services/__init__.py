"""
Business services module.

Services are imported lazily to avoid requiring all optional dependencies
(zep_cloud, openai, tavily, etc.) at import time.
Import individual modules directly: from cc_layer.app.services.life_event_engine import ...
"""

