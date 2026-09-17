-- A contract-specific graph is a transient reviewer artifact, separate from the approved AAOIFI corpus graph.
-- It is retained locally so a browser may issue bounded Cypher-compatible graph queries after analysis.
CREATE TABLE IF NOT EXISTS contract_analysis_graph (
  analysis_id uuid PRIMARY KEY,
  graph jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
