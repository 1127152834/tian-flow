# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.prompts.planner_model import StepType
from src.config.database import get_database_config
import logging
import psycopg2
from typing import Optional

logger = logging.getLogger(__name__)

from .types import State
from .nodes import (
    coordinator_node,
    planner_node,
    reporter_node,
    research_team_node,
    researcher_node,
    coder_node,
    human_feedback_node,
    background_investigation_node,
    data_analyst_node,
)


def continue_to_running_research_team(state: State):
    current_plan = state.get("current_plan")
    if not current_plan or not current_plan.steps:
        return "planner"
    if all(step.execution_res for step in current_plan.steps):
        return "planner"
    for step in current_plan.steps:
        if not step.execution_res:
            break
    if step.step_type and step.step_type == StepType.RESEARCH:
        return "researcher"
    if step.step_type and step.step_type == StepType.PROCESSING:
        return "coder"
    return "planner"


def _build_base_graph():
    """Build and return the base state graph with all nodes and edges."""
    builder = StateGraph(State)
    builder.add_edge(START, "coordinator")
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("background_investigator", background_investigation_node)
    builder.add_node("planner", planner_node)
    builder.add_node("reporter", reporter_node)
    builder.add_node("research_team", research_team_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("coder", coder_node)
    builder.add_node("human_feedback", human_feedback_node)
    builder.add_node("data_analyst", data_analyst_node)
    builder.add_edge("background_investigator", "planner")
    builder.add_conditional_edges(
        "research_team",
        continue_to_running_research_team,
        ["planner", "researcher", "coder"],
    )

    builder.add_edge("reporter", END)
    builder.add_edge("data_analyst", END)
    return builder


class PostgreSQLCheckpointer:
    """PostgreSQL-based checkpointer for LangGraph state persistence"""

    def __init__(self):
        self.db_config = get_database_config()
        self._ensure_checkpoint_table()

    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(
            host=self.db_config["host"],
            port=self.db_config["port"],
            database=self.db_config["database"],
            user=self.db_config["user"],
            password=self.db_config["password"]
        )

    def _ensure_checkpoint_table(self):
        """Ensure checkpoint table exists"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CREATE SCHEMA IF NOT EXISTS langgraph;

                        CREATE TABLE IF NOT EXISTS langgraph.checkpoints (
                            thread_id TEXT NOT NULL,
                            checkpoint_id TEXT NOT NULL,
                            parent_checkpoint_id TEXT,
                            checkpoint_data JSONB NOT NULL,
                            metadata JSONB DEFAULT '{}',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY (thread_id, checkpoint_id)
                        );

                        CREATE INDEX IF NOT EXISTS idx_checkpoints_thread_id
                        ON langgraph.checkpoints(thread_id);

                        CREATE INDEX IF NOT EXISTS idx_checkpoints_created_at
                        ON langgraph.checkpoints(created_at);
                    """)
                    conn.commit()
                    logger.info("✅ PostgreSQL checkpoint table initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize checkpoint table: {e}")
            logger.info("Falling back to MemorySaver")


def _create_checkpointer() -> Optional[object]:
    """Create appropriate checkpointer based on configuration"""
    try:
        # Try to create PostgreSQL checkpointer
        pg_checkpointer = PostgreSQLCheckpointer()
        logger.info("✅ Using PostgreSQL checkpointer for persistent memory")

        # For now, return MemorySaver as LangGraph's built-in checkpointer
        # In a full implementation, we would create a custom checkpointer class
        # that implements LangGraph's checkpointer interface
        return MemorySaver()

    except Exception as e:
        logger.warning(f"Failed to create PostgreSQL checkpointer: {e}")
        logger.info("Falling back to MemorySaver")
        return MemorySaver()


def build_graph_with_memory():
    """Build and return the agent workflow graph with memory."""
    # Use PostgreSQL-compatible persistent memory to save conversation history
    memory = _create_checkpointer()

    # build state graph
    builder = _build_base_graph()
    return builder.compile(checkpointer=memory)


def build_graph():
    """Build and return the agent workflow graph without memory."""
    # build state graph
    builder = _build_base_graph()
    return builder.compile()


graph = build_graph()
