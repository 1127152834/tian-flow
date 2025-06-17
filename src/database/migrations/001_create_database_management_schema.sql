-- Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
-- SPDX-License-Identifier: MIT

-- Migration: Create database management schema and tables
-- This migration creates the necessary tables for database datasource management

-- Create database_management schema
CREATE SCHEMA IF NOT EXISTS database_management;

-- Create database_datasources table (safe creation - no data loss)
CREATE TABLE IF NOT EXISTS database_management.database_datasources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    description TEXT,
    database_type VARCHAR(50) NOT NULL CHECK (database_type IN ('MYSQL', 'POSTGRESQL')),
    host VARCHAR(256) NOT NULL,
    port INTEGER NOT NULL CHECK (port > 0 AND port <= 65535),
    database_name VARCHAR(256) NOT NULL,
    username VARCHAR(256) NOT NULL,
    password VARCHAR(512) NOT NULL,
    readonly_mode BOOLEAN NOT NULL DEFAULT TRUE,
    allowed_operations TEXT[] NOT NULL DEFAULT ARRAY['SELECT'],
    connection_status VARCHAR(50) NOT NULL DEFAULT 'DISCONNECTED'
        CHECK (connection_status IN ('CONNECTED', 'DISCONNECTED', 'ERROR', 'TESTING')),
    connection_error TEXT,
    last_tested_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Add unique constraint on name for non-deleted records
    CONSTRAINT unique_active_datasource_name UNIQUE (name) DEFERRABLE INITIALLY DEFERRED
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_database_datasources_name 
    ON database_management.database_datasources(name) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_database_datasources_type 
    ON database_management.database_datasources(database_type) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_database_datasources_status 
    ON database_management.database_datasources(connection_status) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_database_datasources_created 
    ON database_management.database_datasources(created_at) WHERE deleted_at IS NULL;

-- Create connection_tests table for tracking connection test history
CREATE TABLE IF NOT EXISTS database_management.connection_tests (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL REFERENCES database_management.database_datasources(id) ON DELETE CASCADE,
    test_result BOOLEAN NOT NULL,
    error_message TEXT,
    response_time_ms INTEGER,
    tested_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    test_details JSONB
);

-- Create index for connection tests
CREATE INDEX IF NOT EXISTS idx_connection_tests_datasource 
    ON database_management.connection_tests(datasource_id);

CREATE INDEX IF NOT EXISTS idx_connection_tests_tested_at 
    ON database_management.connection_tests(tested_at);

-- Create datasource_logs table for audit logging
CREATE TABLE IF NOT EXISTS database_management.datasource_logs (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER REFERENCES database_management.database_datasources(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    details JSONB,
    user_info VARCHAR(256),
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create index for datasource logs
CREATE INDEX IF NOT EXISTS idx_datasource_logs_datasource 
    ON database_management.datasource_logs(datasource_id);

CREATE INDEX IF NOT EXISTS idx_datasource_logs_action 
    ON database_management.datasource_logs(action);

CREATE INDEX IF NOT EXISTS idx_datasource_logs_created 
    ON database_management.datasource_logs(created_at);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION database_management.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at (if not exists)
DROP TRIGGER IF EXISTS update_database_datasources_updated_at ON database_management.database_datasources;
CREATE TRIGGER update_database_datasources_updated_at
    BEFORE UPDATE ON database_management.database_datasources
    FOR EACH ROW EXECUTE FUNCTION database_management.update_updated_at_column();

-- Insert some sample data for testing (optional)
-- INSERT INTO database_management.database_datasources 
-- (name, description, database_type, host, port, database_name, username, password, readonly_mode)
-- VALUES 
-- ('Local PostgreSQL', 'Local development database', 'POSTGRESQL', 'localhost', 5432, 'aolei', 'aolei', 'aolei123456', true);

COMMENT ON SCHEMA database_management IS 'Schema for database datasource management';
COMMENT ON TABLE database_management.database_datasources IS 'Database datasource configurations';
COMMENT ON TABLE database_management.connection_tests IS 'Database connection test history';
COMMENT ON TABLE database_management.datasource_logs IS 'Audit logs for datasource operations';
