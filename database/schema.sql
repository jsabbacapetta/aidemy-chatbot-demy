-- Aidemy Chatbot (Demy) Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active', -- active, completed, abandoned
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb, -- can store citations, confidence, etc.
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Leads table
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    company VARCHAR(255),
    role VARCHAR(255),
    company_size VARCHAR(50), -- <50, 50-250, >250
    challenge TEXT,
    timeline VARCHAR(100),

    -- BANEC Scoring (1-5 each, total 5-25)
    banec_budget INTEGER CHECK (banec_budget BETWEEN 1 AND 5),
    banec_authority INTEGER CHECK (banec_authority BETWEEN 1 AND 5),
    banec_necessity INTEGER CHECK (banec_necessity BETWEEN 1 AND 5),
    banec_emergency INTEGER CHECK (banec_emergency BETWEEN 1 AND 5),
    banec_compatibility INTEGER CHECK (banec_compatibility BETWEEN 1 AND 5),
    banec_total INTEGER GENERATED ALWAYS AS (
        COALESCE(banec_budget, 0) +
        COALESCE(banec_authority, 0) +
        COALESCE(banec_necessity, 0) +
        COALESCE(banec_emergency, 0) +
        COALESCE(banec_compatibility, 0)
    ) STORED,
    banec_category VARCHAR(20) GENERATED ALWAYS AS (
        CASE
            WHEN (COALESCE(banec_budget, 0) + COALESCE(banec_authority, 0) +
                  COALESCE(banec_necessity, 0) + COALESCE(banec_emergency, 0) +
                  COALESCE(banec_compatibility, 0)) >= 18 THEN 'hot'
            WHEN (COALESCE(banec_budget, 0) + COALESCE(banec_authority, 0) +
                  COALESCE(banec_necessity, 0) + COALESCE(banec_emergency, 0) +
                  COALESCE(banec_compatibility, 0)) >= 12 THEN 'warm'
            ELSE 'cold'
        END
    ) STORED,

    -- Actions
    call_booked BOOLEAN DEFAULT FALSE,
    call_booked_at TIMESTAMP,
    docs_sent BOOLEAN DEFAULT FALSE,
    docs_sent_at TIMESTAMP,
    escalated BOOLEAN DEFAULT FALSE,
    escalated_at TIMESTAMP,

    -- Status
    status VARCHAR(50) DEFAULT 'new', -- new, contacted, converted, lost

    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Metrics table for analytics
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type VARCHAR(100) NOT NULL, -- conversation_started, message_sent, lead_qualified, call_booked, etc.
    metric_value NUMERIC,
    metadata JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge base documents tracking
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_url TEXT,
    source_type VARCHAR(50), -- google_drive, substack, manual
    document_name VARCHAR(500) NOT NULL,
    document_hash VARCHAR(64), -- SHA-256 hash for change detection
    chunk_count INTEGER DEFAULT 0,
    last_processed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_started_at ON conversations(started_at);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_banec_total ON leads(banec_total);
CREATE INDEX idx_leads_banec_category ON leads(banec_category);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_created_at ON leads(created_at);
CREATE INDEX idx_metrics_metric_type ON metrics(metric_type);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp);
CREATE INDEX idx_knowledge_documents_document_hash ON knowledge_documents(document_hash);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_documents_updated_at BEFORE UPDATE ON knowledge_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial metrics for tracking
INSERT INTO metrics (metric_type, metric_value, metadata)
VALUES ('system_initialized', 1, '{"version": "1.0", "date": "2025-01-30"}'::jsonb);
