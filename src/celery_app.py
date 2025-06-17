# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Celery application configuration for DeerFlow.

Provides distributed task queue for background processing including
Text2SQL training, embedding generation, and data cleanup tasks.
"""

import os
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Celery app
celery_app = Celery('deer_flow')

# Configuration
celery_app.conf.update(
    # Broker settings
    broker_url=os.getenv('REDIS_URL', 'redis://localhost:6380/0'),
    result_backend=os.getenv('REDIS_URL', 'redis://localhost:6380/0'),
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'text2sql.*': {'queue': 'text2sql'},
        'database.*': {'queue': 'database'},
        'cleanup.*': {'queue': 'cleanup'},
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Task execution settings
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes
    task_track_started=True,
    task_send_sent_event=True,
    worker_send_task_events=True,
    
    # Result settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Monitoring
    worker_hijack_root_logger=False,
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        'cleanup-old-data': {
            'task': 'text2sql.cleanup_old_data',
            'schedule': 86400.0,  # Run daily
            'kwargs': {'days_to_keep': 30}
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks([
    'src.tasks.text2sql_tasks',
])

# Task annotations for monitoring
celery_app.conf.task_annotations = {
    '*': {
        'rate_limit': '100/m',  # 100 tasks per minute
    },
    'text2sql.train_model': {
        'rate_limit': '5/m',    # 5 training tasks per minute
        'time_limit': 1800,     # 30 minutes
        'soft_time_limit': 1500, # 25 minutes
    },
    'text2sql.generate_embeddings': {
        'rate_limit': '10/m',   # 10 embedding tasks per minute
        'time_limit': 600,      # 10 minutes
    },
    'text2sql.cleanup_old_data': {
        'rate_limit': '1/h',    # 1 cleanup task per hour
        'time_limit': 3600,     # 1 hour
    },
}

if __name__ == '__main__':
    celery_app.start()
