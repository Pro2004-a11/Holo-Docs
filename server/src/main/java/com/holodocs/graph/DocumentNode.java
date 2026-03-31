package com.holodocs.graph;

import java.util.List;

/**
 * A node in the knowledge graph — represents a document or concept.
 * Stub for MVP — full graph backend (Neo4j) deferred to Phase 2.
 */
public record DocumentNode(
    String id,
    String title,
    String nodeType,  // "wiki", "doc", "task", "concept"
    List<String> connections
) {}
