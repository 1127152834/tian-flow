# Graph-RAG-Agent Integration

DeerFlow now supports Graph-RAG-Agent as a RAG provider, enabling knowledge graph-based question answering alongside traditional document retrieval.

## Overview

Graph-RAG-Agent integration allows DeerFlow to leverage knowledge graphs for enhanced question answering. Instead of retrieving documents from a traditional RAG system, it queries a knowledge graph to provide more structured and relationship-aware responses.

## Configuration

### Environment Variables

Add the following environment variables to your `.env` file:

```bash
# Use Graph-RAG-Agent as RAG provider
RAG_PROVIDER=graph_rag_agent

# Graph-RAG-Agent API configuration
GRAPH_RAG_AGENT_API_URL="http://localhost:8001"
GRAPH_RAG_AGENT_API_KEY=""  # Optional, if authentication is required
GRAPH_RAG_AGENT_TIMEOUT=60
GRAPH_RAG_AGENT_SEARCH_TYPE=coordinator  # coordinator, local, global, exploration
```

### Search Types

Graph-RAG-Agent supports different search strategies:

- **coordinator**: Intelligent routing between different search strategies (recommended)
- **local**: Local vector search for specific entities and relations
- **global**: Global community search for comprehensive answers
- **exploration**: Deep research with multi-hop graph traversal

## Usage

### In Chat Interface

Once configured, Graph-RAG-Agent works seamlessly with DeerFlow's existing chat interface. When you mention resources using the `@` symbol, the system will query the knowledge graph instead of traditional documents.

### API Usage

The integration uses the same RAG API endpoints:

```bash
# Get RAG configuration
GET /api/rag/config

# List available resources (knowledge bases)
GET /api/rag/resources?query=optional_filter

# Query is handled automatically in chat
POST /api/chat
```

### Example Queries

Knowledge graph queries work best with relationship-focused questions:

- "What is the relationship between Entity A and Entity B?"
- "How are these systems connected?"
- "What are the dependencies of this component?"
- "Explain the data flow between these services"

## Architecture

### Integration Pattern

Graph-RAG-Agent follows the same provider pattern as RAGFlow:

```
DeerFlow Chat → RAG Builder → GraphRAGAgentProvider → Graph-RAG-Agent API
```

### Response Format

Graph-RAG-Agent responses are converted to DeerFlow's document format:

```python
Document(
    id="graph_rag_result",
    title="Knowledge Graph Query: {query}",
    chunks=[
        Chunk(
            content=answer,
            similarity=1.0,
            metadata={
                "source": "graph-rag-agent",
                "search_type": search_type,
                "entities_mentioned": entities,
                "sources": sources,
                "execution_time": execution_time
            }
        )
    ]
)
```

## Setup Graph-RAG-Agent Service

### Prerequisites

1. Install and configure Graph-RAG-Agent service
2. Ensure it's running on the configured URL (default: http://localhost:8001)
3. Set up your knowledge graph data in Graph-RAG-Agent

### Health Check

DeerFlow automatically checks the health of the Graph-RAG-Agent service. You can verify the connection by:

1. Checking the RAG configuration endpoint: `GET /api/rag/config`
2. Listing resources: `GET /api/rag/resources`
3. Monitoring logs for connection status

## Troubleshooting

### Common Issues

1. **Service Not Available**
   - Check if Graph-RAG-Agent is running on the configured URL
   - Verify network connectivity
   - Check API key if authentication is required

2. **Empty Results**
   - Ensure your knowledge graph has relevant data
   - Try different search types
   - Check Graph-RAG-Agent logs for errors

3. **Timeout Issues**
   - Increase `GRAPH_RAG_AGENT_TIMEOUT` value
   - Optimize your knowledge graph queries
   - Consider using simpler search types

### Debugging

Enable debug mode in Graph-RAG-Agent queries by modifying the provider:

```python
payload = {
    "query": query,
    "search_type": self.search_type,
    "debug": True,  # Enable debug mode
    "use_thinking": True,
    "max_results": 50
}
```

## Comparison with RAGFlow

| Feature | RAGFlow | Graph-RAG-Agent |
|---------|---------|-----------------|
| Data Type | Documents | Knowledge Graph |
| Search Method | Vector Similarity | Graph Traversal + Vector |
| Relationships | Limited | Rich Relationships |
| Reasoning | Basic | Advanced (Multi-hop) |
| Use Cases | Document QA | Relationship Analysis |

## Best Practices

1. **Query Design**: Frame questions to leverage graph relationships
2. **Search Type Selection**: Use `coordinator` for automatic strategy selection
3. **Resource Management**: Organize knowledge bases logically
4. **Performance**: Monitor execution times and adjust timeout accordingly
5. **Fallback**: Consider having both RAGFlow and Graph-RAG-Agent available

## Future Enhancements

- Support for multiple knowledge graph providers
- Hybrid RAG + Knowledge Graph queries
- Real-time knowledge graph updates
- Advanced visualization of graph results
- Integration with DeerFlow's research workflows
