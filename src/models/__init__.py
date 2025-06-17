# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Models module for Olight.
Contains all data models and database schemas.
"""

from .database_datasource import (
    DatabaseDatasource,
    DatabaseType,
    ConnectionStatus,
)

from .api_tools import (
    AuthConfig,
    AuthType,
    Parameter,
    ParameterType,
    DataType,
    RateLimit,
    ResponseConfig,
    ResponseField,
    ResponseType,
    FieldRole,
    APIDefinition,
    HTTPMethod,
    APIDefinitionCreate,
    APIDefinitionUpdate,
    APICallLog,
)

# Temporarily commented out to fix import issues
# from .resource_discovery import (
#     ResourceRegistry,
#     ResourceRegistryCreate,
#     ResourceRegistryUpdate,
#     ResourceRegistryResponse,
#     ResourceType,
#     ResourceStatus,
#     VectorizationStatus,
#     ResourceVector,
#     ResourceVectorCreate,
#     VectorType,
#     ResourceMatchHistory,
#     ResourceMatchHistoryCreate,
#     UserFeedback,
#     ResourceUsageStats,
#     ResourceUsageStatsCreate,
#     SystemStatus,
#     SystemStatusCreate,
#     OperationType,
#     SystemStatusType,
#     ResourceMatch,
#     ResourceDiscoveryRequest,
#     ResourceDiscoveryResponse,
# )

__all__ = [
    # Database
    "DatabaseDatasource",
    "DatabaseType",
    "ConnectionStatus",

    # API Tools
    "AuthConfig",
    "AuthType",
    "Parameter",
    "ParameterType",
    "DataType",
    "RateLimit",
    "ResponseConfig",
    "ResponseField",
    "ResponseType",
    "FieldRole",
    "APIDefinition",
    "HTTPMethod",
    "APIDefinitionCreate",
    "APIDefinitionUpdate",
    "APICallLog",

    # Resource Discovery - temporarily commented out
    # "ResourceRegistry",
    # "ResourceRegistryCreate",
    # "ResourceRegistryUpdate",
    # "ResourceRegistryResponse",
    # "ResourceType",
    # "ResourceStatus",
    # "VectorizationStatus",
    # "ResourceVector",
    # "ResourceVectorCreate",
    # "VectorType",
    # "ResourceMatchHistory",
    # "ResourceMatchHistoryCreate",
    # "UserFeedback",
    # "ResourceUsageStats",
    # "ResourceUsageStatsCreate",
    # "SystemStatus",
    # "SystemStatusCreate",
    # "OperationType",
    # "SystemStatusType",
    # "ResourceMatch",
    # "ResourceDiscoveryRequest",
    # "ResourceDiscoveryResponse",
]
