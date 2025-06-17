# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import pytest
import requests
from unittest.mock import patch, MagicMock
from src.rag.graph_rag_agent import GraphRAGAgentProvider, parse_graph_uri


class TestGraphRAGAgentProvider:
    """Test GraphRAGAgentProvider"""

    def test_init_missing_url(self, monkeypatch):
        """Test initialization with missing API URL"""
        monkeypatch.delenv("GRAPH_RAG_AGENT_API_URL", raising=False)
        
        with pytest.raises(ValueError, match="GRAPH_RAG_AGENT_API_URL is not set"):
            GraphRAGAgentProvider()

    def test_init_success(self, monkeypatch):
        """Test successful initialization"""
        monkeypatch.setenv("GRAPH_RAG_AGENT_API_URL", "http://localhost:8001")
        monkeypatch.setenv("GRAPH_RAG_AGENT_API_KEY", "test-key")
        monkeypatch.setenv("GRAPH_RAG_AGENT_TIMEOUT", "30")
        monkeypatch.setenv("GRAPH_RAG_AGENT_SEARCH_TYPE", "local")
        
        provider = GraphRAGAgentProvider()
        
        assert provider.api_url == "http://localhost:8001"
        assert provider.api_key == "test-key"
        assert provider.timeout == 30
        assert provider.search_type == "local"

    @patch("src.rag.graph_rag_agent.requests.post")
    def test_query_relevant_documents_success(self, mock_post, monkeypatch):
        """Test successful document query"""
        monkeypatch.setenv("GRAPH_RAG_AGENT_API_URL", "http://localhost:8001")
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "answer": "This is a knowledge graph answer",
            "entities_mentioned": ["Entity1", "Entity2"],
            "sources": [{"type": "graph", "title": "Knowledge Graph"}],
            "execution_time": 1.5
        }
        mock_post.return_value = mock_response
        
        provider = GraphRAGAgentProvider()
        docs = provider.query_relevant_documents("What is Entity1?")
        
        assert len(docs) == 1
        assert docs[0].id == "graph_rag_result"
        assert docs[0].title.startswith("Knowledge Graph Query:")
        assert len(docs[0].chunks) == 1
        assert docs[0].chunks[0].content == "This is a knowledge graph answer"
        assert docs[0].chunks[0].similarity == 1.0
        assert docs[0].chunks[0].metadata["source"] == "graph-rag-agent"
        assert docs[0].chunks[0].metadata["entities_mentioned"] == ["Entity1", "Entity2"]

    @patch("src.rag.graph_rag_agent.requests.post")
    def test_query_relevant_documents_error(self, mock_post, monkeypatch):
        """Test document query with error response"""
        monkeypatch.setenv("GRAPH_RAG_AGENT_API_URL", "http://localhost:8001")
        
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        provider = GraphRAGAgentProvider()
        docs = provider.query_relevant_documents("What is Entity1?")
        
        assert len(docs) == 0

    @patch("src.rag.graph_rag_agent.requests.post")
    def test_query_relevant_documents_timeout(self, mock_post, monkeypatch):
        """Test document query with timeout"""
        monkeypatch.setenv("GRAPH_RAG_AGENT_API_URL", "http://localhost:8001")
        
        # Mock timeout exception
        mock_post.side_effect = requests.exceptions.Timeout()
        
        provider = GraphRAGAgentProvider()
        docs = provider.query_relevant_documents("What is Entity1?")
        
        assert len(docs) == 0

    @patch("src.rag.graph_rag_agent.requests.get")
    def test_list_resources_success(self, mock_get, monkeypatch):
        """Test successful resource listing"""
        monkeypatch.setenv("GRAPH_RAG_AGENT_API_URL", "http://localhost:8001")
        
        # Mock successful status response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "database_info": {
                "neo4j": "Connected",
                "postgresql": "Connected"
            }
        }
        mock_get.return_value = mock_response
        
        provider = GraphRAGAgentProvider()
        resources = provider.list_resources()
        
        assert len(resources) >= 1
        assert resources[0].uri == "graph://knowledge-base/default"
        assert resources[0].title == "Knowledge Graph"
        
        # Should have additional resources from database_info
        assert len(resources) > 1

    @patch("src.rag.graph_rag_agent.requests.get")
    def test_list_resources_error(self, mock_get, monkeypatch):
        """Test resource listing with error"""
        monkeypatch.setenv("GRAPH_RAG_AGENT_API_URL", "http://localhost:8001")
        
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        provider = GraphRAGAgentProvider()
        resources = provider.list_resources()
        
        # Should return default resource even on error
        assert len(resources) == 1
        assert resources[0].uri == "graph://knowledge-base/default"

    def test_parse_graph_uri_valid(self):
        """Test parsing valid graph URI"""
        kb_name, resource_id = parse_graph_uri("graph://knowledge-base/test#resource123")
        
        assert kb_name == "test"
        assert resource_id == "resource123"

    def test_parse_graph_uri_no_fragment(self):
        """Test parsing graph URI without fragment"""
        kb_name, resource_id = parse_graph_uri("graph://knowledge-base/test")
        
        assert kb_name == "test"
        assert resource_id == ""

    def test_parse_graph_uri_invalid_scheme(self):
        """Test parsing invalid URI scheme"""
        with pytest.raises(ValueError, match="Invalid graph URI"):
            parse_graph_uri("http://knowledge-base/test")

    def test_parse_graph_uri_default(self):
        """Test parsing URI with default knowledge base"""
        kb_name, resource_id = parse_graph_uri("graph://knowledge-base/")
        
        assert kb_name == "default"
        assert resource_id == ""
