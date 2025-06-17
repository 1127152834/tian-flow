#!/usr/bin/env python3
"""
Celery worker startup script for DeerFlow Text2SQL.

This script starts the Celery worker for processing background tasks.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.tasks.text2sql_tasks import celery_app

if __name__ == '__main__':
    # Start Celery worker
    celery_app.start([
        'worker',
        '--loglevel=info',
        '--concurrency=2',
        '--queues=text2sql,database,cleanup',
        '--hostname=deer-flow-worker@%h'
    ])
