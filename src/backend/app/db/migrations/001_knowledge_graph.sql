CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_search;

CREATE TABLE IF NOT EXISTS ingestion_run (
  id uuid PRIMARY KEY,
  source_checksum text NOT NULL,
  source_filename text NOT NULL,
  parser_version text NOT NULL,
  approval_status text NOT NULL CHECK (approval_status IN ('draft', 'approved', 'rejected')),
  approved_by text,
  approved_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS standard (
  id uuid PRIMARY KEY,
  authority text NOT NULL,
  standard_number text NOT NULL,
  title text NOT NULL,
  edition text NOT NULL,
  language text NOT NULL,
  source_checksum text NOT NULL,
  approval_status text NOT NULL CHECK (approval_status IN ('draft', 'approved', 'rejected')),
  UNIQUE (authority, standard_number, edition, language, source_checksum)
);

CREATE TABLE IF NOT EXISTS clause (
  id uuid PRIMARY KEY,
  standard_id uuid NOT NULL REFERENCES standard(id),
  clause_id text NOT NULL,
  parent_clause_id text,
  breadcrumb text NOT NULL,
  verbatim_text text NOT NULL,
  embedding_text text NOT NULL,
  source_pdf_page_start integer NOT NULL,
  source_pdf_page_end integer NOT NULL,
  printed_page_start integer NOT NULL,
  printed_page_end integer NOT NULL,
  language text NOT NULL,
  approval_status text NOT NULL CHECK (approval_status IN ('draft', 'approved', 'rejected')),
  embedding vector(1536),
  UNIQUE (standard_id, clause_id)
);

CREATE INDEX IF NOT EXISTS clause_standard_approval_idx ON clause (standard_id, approval_status);
CREATE INDEX IF NOT EXISTS clause_approval_idx ON clause (approval_status);

-- The retrieval copy holds fields required for filtering, lexical BM25, and dense-vector top-k.
CREATE INDEX IF NOT EXISTS clause_search_idx ON clause
USING paradedb (
  id,
  clause_id,
  embedding_text,
  language,
  approval_status,
  embedding vector_cosine_ops
)
WITH (key_field = 'id');

CREATE TABLE IF NOT EXISTS graph_node (
  id uuid PRIMARY KEY,
  node_type text NOT NULL CHECK (node_type IN (
    'standard', 'section', 'clause', 'concept', 'contract_type', 'risk_pattern',
    'rule', 'control', 'finding', 'authority'
  )),
  canonical_key text NOT NULL UNIQUE,
  label text NOT NULL,
  description text,
  clause_id uuid REFERENCES clause(id),
  properties jsonb NOT NULL DEFAULT '{}'::jsonb,
  approval_status text NOT NULL CHECK (approval_status IN ('draft', 'approved', 'rejected')),
  ingestion_run_id uuid REFERENCES ingestion_run(id),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS graph_node_alias (
  id uuid PRIMARY KEY,
  graph_node_id uuid NOT NULL REFERENCES graph_node(id) ON DELETE CASCADE,
  alias text NOT NULL,
  language text NOT NULL DEFAULT 'en',
  UNIQUE (graph_node_id, alias, language)
);
CREATE INDEX IF NOT EXISTS graph_node_alias_lookup_idx ON graph_node_alias (alias, language);

CREATE TABLE IF NOT EXISTS graph_edge (
  id uuid PRIMARY KEY,
  source_node_id uuid NOT NULL REFERENCES graph_node(id) ON DELETE CASCADE,
  target_node_id uuid NOT NULL REFERENCES graph_node(id) ON DELETE CASCADE,
  predicate text NOT NULL CHECK (predicate IN (
    'CONTAINS', 'PARENT_OF', 'CITES', 'DEFINES', 'GOVERNS', 'REQUIRES',
    'PROHIBITS', 'PERMITS', 'CONFLICTS_WITH', 'EVIDENCED_BY', 'RELATED_TO'
  )),
  evidence_clause_id uuid REFERENCES clause(id),
  evidence_note text,
  source_pdf_page integer,
  extraction_method text NOT NULL CHECK (extraction_method IN ('parser', 'reviewer', 'inference')),
  confidence numeric(4,3) CHECK (confidence >= 0 AND confidence <= 1),
  approval_status text NOT NULL CHECK (approval_status IN ('draft', 'approved', 'rejected')),
  scholar_reviewer text,
  ingestion_run_id uuid REFERENCES ingestion_run(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (source_node_id <> target_node_id)
);
CREATE INDEX IF NOT EXISTS graph_edge_source_approved_idx ON graph_edge (source_node_id, approval_status, predicate);
CREATE INDEX IF NOT EXISTS graph_edge_target_approved_idx ON graph_edge (target_node_id, approval_status, predicate);
CREATE INDEX IF NOT EXISTS graph_edge_evidence_idx ON graph_edge (evidence_clause_id) WHERE approval_status = 'approved';

CREATE TABLE IF NOT EXISTS graph_projection_run (
  id uuid PRIMARY KEY,
  ingestion_run_id uuid NOT NULL REFERENCES ingestion_run(id),
  projection_version text NOT NULL,
  node_count integer NOT NULL,
  edge_count integer NOT NULL,
  approved_by text,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- graph_edge is the canonical, evidence-bearing graph. Inferred edges can exist only as draft,
-- and retrieval queries must filter on approval_status = 'approved'.
