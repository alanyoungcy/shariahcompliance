-- Demo-only graph projection. It is intentionally independent of the AAOIFI PDF corpus
-- and must be replaced by an approved ingestion projection before a citation is presented as verified.
INSERT INTO ingestion_run (id, source_checksum, source_filename, parser_version, approval_status, approved_by, approved_at)
VALUES (
  '00000000-0000-0000-0000-000000000701',
  'demo-only-no-aaoifi-corpus',
  'demo-relationship-map.json',
  'demo-graph-v1',
  'approved',
  'demo-governance-marker',
  now()
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO graph_node (id, node_type, canonical_key, label, description, properties, approval_status, ingestion_run_id)
VALUES
  ('00000000-0000-0000-0000-000000000711', 'risk_pattern', 'variable-profit-benchmark', 'Variable profit benchmark', 'A sale price determined by a future floating benchmark.', '{"demo_only": true}'::jsonb, 'approved', '00000000-0000-0000-0000-000000000701'),
  ('00000000-0000-0000-0000-000000000712', 'rule', 'fixed-price', 'Fixed price and profit', 'The sale price and profit are fixed and known at signature.', '{"demo_only": true}'::jsonb, 'approved', '00000000-0000-0000-0000-000000000701'),
  ('00000000-0000-0000-0000-000000000713', 'clause', 'ss8-4-6', 'SS 8 · 4/6', 'Demo evidence reference. It does not claim an approved AAOIFI quotation.', '{"demo_only": true, "display_clause_id": "4/6", "printed_page": 211}'::jsonb, 'approved', '00000000-0000-0000-0000-000000000701'),
  ('00000000-0000-0000-0000-000000000714', 'standard', 'aaoifi-ss8', 'AAOIFI Shari’ah Standard 8', 'Murabahah (Revised Standard), English 2015 compilation.', '{"demo_only": true}'::jsonb, 'approved', '00000000-0000-0000-0000-000000000701'),
  ('00000000-0000-0000-0000-000000000715', 'control', 'fixed-sale-price-control', 'Confirm the executed sale price', 'Control proposed for human review before contract execution.', '{"demo_only": true}'::jsonb, 'approved', '00000000-0000-0000-0000-000000000701')
ON CONFLICT (canonical_key) DO NOTHING;

INSERT INTO graph_node_alias (id, graph_node_id, alias, language)
VALUES ('00000000-0000-0000-0000-000000000721', '00000000-0000-0000-0000-000000000711', 'variable-profit-benchmark', 'en')
ON CONFLICT (graph_node_id, alias, language) DO NOTHING;

INSERT INTO graph_edge (id, source_node_id, target_node_id, predicate, evidence_note, source_pdf_page, extraction_method, confidence, approval_status, scholar_reviewer, ingestion_run_id)
VALUES
  ('00000000-0000-0000-0000-000000000731', '00000000-0000-0000-0000-000000000711', '00000000-0000-0000-0000-000000000712', 'CONFLICTS_WITH', 'Demo-only relationship map. Review source and scholar approval before treating as authority.', 211, 'reviewer', 1.000, 'approved', 'demo-governance-marker', '00000000-0000-0000-0000-000000000701'),
  ('00000000-0000-0000-0000-000000000732', '00000000-0000-0000-0000-000000000712', '00000000-0000-0000-0000-000000000713', 'EVIDENCED_BY', 'Demo-only relationship map. Review source and scholar approval before treating as authority.', 211, 'reviewer', 1.000, 'approved', 'demo-governance-marker', '00000000-0000-0000-0000-000000000701'),
  ('00000000-0000-0000-0000-000000000733', '00000000-0000-0000-0000-000000000713', '00000000-0000-0000-0000-000000000714', 'CONTAINS', 'Demo-only relationship map. Review source and scholar approval before treating as authority.', 211, 'reviewer', 1.000, 'approved', 'demo-governance-marker', '00000000-0000-0000-0000-000000000701'),
  ('00000000-0000-0000-0000-000000000734', '00000000-0000-0000-0000-000000000712', '00000000-0000-0000-0000-000000000715', 'REQUIRES', 'Demo-only relationship map. Review source and scholar approval before treating as authority.', 211, 'reviewer', 1.000, 'approved', 'demo-governance-marker', '00000000-0000-0000-0000-000000000701')
ON CONFLICT (id) DO NOTHING;

INSERT INTO graph_projection_run (id, ingestion_run_id, projection_version, node_count, edge_count, approved_by)
VALUES ('00000000-0000-0000-0000-000000000741', '00000000-0000-0000-0000-000000000701', 'demo-graph-v1', 5, 4, 'demo-governance-marker')
ON CONFLICT (id) DO NOTHING;
