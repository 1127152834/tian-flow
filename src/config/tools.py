# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import enum
from dotenv import load_dotenv

load_dotenv()


class RAGProvider(enum.Enum):
    RAGFLOW = "ragflow"
    GRAPH_RAG_AGENT = "graph_rag_agent"


SELECTED_RAG_PROVIDER = os.getenv("RAG_PROVIDER")
