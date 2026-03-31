package com.holodocs.graph;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Knowledge graph service — stub for MVP.
 * In Phase 2 this will back onto Neo4j for real graph traversal.
 */
@Service
public class KnowledgeGraphService {

    private static final Logger log = LoggerFactory.getLogger(KnowledgeGraphService.class);
    private final Map<String, DocumentNode> nodes = new ConcurrentHashMap<>();

    public KnowledgeGraphService() {
        // Seed with demo data
        nodes.put("doc-1", new DocumentNode("doc-1", "Architecture Review", "wiki", List.of("doc-2", "doc-3")));
        nodes.put("doc-2", new DocumentNode("doc-2", "API Spec", "doc", List.of("doc-1")));
        nodes.put("doc-3", new DocumentNode("doc-3", "Sprint Backlog", "task", List.of("doc-1")));
    }

    public Optional<DocumentNode> getNode(String id) {
        return Optional.ofNullable(nodes.get(id));
    }

    public List<DocumentNode> getConnections(String nodeId) {
        DocumentNode node = nodes.get(nodeId);
        if (node == null) return List.of();
        return node.connections().stream()
            .map(nodes::get)
            .filter(n -> n != null)
            .toList();
    }

    public List<DocumentNode> allNodes() {
        return List.copyOf(nodes.values());
    }
}
