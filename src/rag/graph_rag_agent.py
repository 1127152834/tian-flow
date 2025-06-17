# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import requests
import logging
from typing import List, Dict, Any
from urllib.parse import urlparse

from src.rag.retriever import Chunk, Document, Resource, Retriever

logger = logging.getLogger(__name__)


class GraphRAGAgentProvider(Retriever):
    """
    GraphRAGAgentProvider is a provider that uses Graph-RAG-Agent to retrieve knowledge graph information.
    Similar to RAGFlowProvider but for knowledge graph queries.
    """

    api_url: str
    api_key: str = None
    timeout: int = 60
    search_type: str = "coordinator"  # Default search type

    def __init__(self):
        api_url = os.getenv("GRAPH_RAG_AGENT_API_URL")
        if not api_url:
            raise ValueError("GRAPH_RAG_AGENT_API_URL is not set")
        self.api_url = api_url.rstrip('/')

        # API key is optional for graph-rag-agent
        self.api_key = os.getenv("GRAPH_RAG_AGENT_API_KEY")
        
        timeout = os.getenv("GRAPH_RAG_AGENT_TIMEOUT")
        if timeout:
            self.timeout = int(timeout)
            
        search_type = os.getenv("GRAPH_RAG_AGENT_SEARCH_TYPE")
        if search_type:
            self.search_type = search_type

        logger.info(f"GraphRAGAgentProvider initialized with URL: {self.api_url}")

    def query_relevant_documents(
        self, query: str, resources: List[Resource] = []
    ) -> List[Document]:
        """
        Query relevant documents from Graph-RAG-Agent.
        
        Args:
            query: The query string
            resources: List of resources (not used for graph queries, but kept for interface compatibility)
            
        Returns:
            List[Document]: List of documents with knowledge graph results
        """
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "query": query,
            "search_type": self.search_type,
            "debug": False,
            "use_thinking": True,
            "max_results": 50
        }

        try:
            response = requests.post(
                f"{self.api_url}/api/v1/chat/query", 
                headers=headers, 
                json=payload,
                timeout=self.timeout
            )

            if response.status_code != 200:
                logger.error(f"Failed to query Graph-RAG-Agent: {response.status_code} - {response.text}")
                # Return empty result on error
                return []

            result = response.json()
            
            # Convert Graph-RAG-Agent response to Document format
            answer = result.get("answer", "")
            entities = result.get("entities_mentioned", [])
            sources = result.get("sources", [])
            execution_time = result.get("execution_time", 0)
            
            # Create a single document with the knowledge graph result
            doc = Document(
                id="graph_rag_result",
                title=f"Knowledge Graph Query: {query[:50]}...",
                chunks=[
                    Chunk(
                        content=answer,
                        similarity=1.0,  # Knowledge graph results are considered highly relevant
                        metadata={
                            "source": "graph-rag-agent",
                            "search_type": self.search_type,
                            "entities_mentioned": entities,
                            "sources": sources,
                            "execution_time": execution_time,
                            "query": query
                        }
                    )
                ]
            )
            
            return [doc]

        except requests.exceptions.Timeout:
            logger.error("Graph-RAG-Agent query timeout")
            return []
        except Exception as e:
            logger.error(f"Graph-RAG-Agent query error: {e}")
            return []

    def list_resources(self, query: str | None = None) -> List[Resource]:
        """
        List available resources from Graph-RAG-Agent.
        For knowledge graphs, this could return available knowledge bases or datasets.
        
        Args:
            query: Optional query to filter resources
            
        Returns:
            List[Resource]: List of available resources
        """
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            # Try to get service status which might include available knowledge bases
            response = requests.get(
                f"{self.api_url}/api/v1/status", 
                headers=headers,
                timeout=10
            )

            if response.status_code != 200:
                logger.warning(f"Failed to get Graph-RAG-Agent status: {response.status_code}")
                # Return a default resource representing the knowledge graph
                return [
                    Resource(
                        uri="graph://knowledge-base/default",
                        title="Knowledge Graph",
                        description="Graph-RAG-Agent Knowledge Graph Database"
                    )
                ]

            result = response.json()
            
            # Extract knowledge base information if available
            resources = []
            
            # Add default knowledge graph resource
            resources.append(
                Resource(
                    uri="graph://knowledge-base/default",
                    title="Knowledge Graph",
                    description="Graph-RAG-Agent Knowledge Graph Database"
                )
            )
            
            # If there are specific databases or knowledge bases mentioned in status, add them
            if "database_info" in result:
                db_info = result["database_info"]
                if isinstance(db_info, dict):
                    for db_name, db_details in db_info.items():
                        resources.append(
                            Resource(
                                uri=f"graph://knowledge-base/{db_name}",
                                title=f"Knowledge Base: {db_name}",
                                description=str(db_details)
                            )
                        )

            return resources

        except Exception as e:
            logger.error(f"Failed to list Graph-RAG-Agent resources: {e}")
            # Return a default resource on error
            return [
                Resource(
                    uri="graph://knowledge-base/default",
                    title="Knowledge Graph",
                    description="Graph-RAG-Agent Knowledge Graph Database"
                )
            ]


def parse_graph_uri(uri: str) -> tuple[str, str]:
    """
    Parse a graph URI to extract knowledge base and resource information.
    
    Args:
        uri: URI in format "graph://knowledge-base/name#resource"
        
    Returns:
        tuple: (knowledge_base_name, resource_id)
    """
    parsed = urlparse(uri)
    if parsed.scheme != "graph":
        raise ValueError(f"Invalid graph URI: {uri}")
    
    # Extract knowledge base name from path
    path_parts = parsed.path.strip('/').split('/')
    kb_name = path_parts[-1] if path_parts else "default"
    
    # Extract resource ID from fragment
    resource_id = parsed.fragment if parsed.fragment else ""
    
    return kb_name, resource_id
