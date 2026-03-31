package com.holodocs.scene;

import com.holodocs.bridge.BridgeSchemas;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Manages the 3D scene objects — positions, rotations, grab state.
 * Thread-safe: gesture interpreter writes, WS handler reads.
 */
public class SceneGraph {

    private final Map<String, SceneNode> nodes = new ConcurrentHashMap<>();

    public SceneGraph() {
        // Start with a single document node for the MVP vertical slice
        nodes.put("doc-node-1", new SceneNode(
            "doc-node-1",
            "DOCUMENT",
            new double[]{0.0, 1.2, -2.0},
            new double[]{0, 0, 0},
            new double[]{1.0, 1.0, 1.0},
            "Demo Document",
            "wiki"
        ));
    }

    public SceneNode getNode(String id) {
        return nodes.get(id);
    }

    public SceneNode findGrabbedBy(String handedness) {
        for (SceneNode node : nodes.values()) {
            if (handedness.equals(node.grabbedBy)) return node;
        }
        return null;
    }

    public SceneNode findClosest(double x, double y, double z, double maxDist) {
        SceneNode closest = null;
        double best = maxDist;
        for (SceneNode node : nodes.values()) {
            double d = node.distanceTo(x, y, z);
            if (d < best) {
                best = d;
                closest = node;
            }
        }
        return closest;
    }

    public List<BridgeSchemas.SceneObject> toSceneObjects() {
        List<BridgeSchemas.SceneObject> result = new ArrayList<>();
        for (SceneNode node : nodes.values()) {
            result.add(node.toSceneObject());
        }
        return result;
    }

    /**
     * Mutable scene node — position and state can change per frame.
     */
    public static class SceneNode {
        private final String id;
        private final String type;
        private volatile double[] position;
        private volatile double[] rotation;
        private volatile double[] scale;
        private volatile String state = "IDLE"; // IDLE, HOVERED, GRABBED
        private volatile String grabbedBy = null;
        private final String title;
        private final String nodeType;

        public SceneNode(String id, String type, double[] pos, double[] rot, double[] scl,
                         String title, String nodeType) {
            this.id = id;
            this.type = type;
            this.position = pos;
            this.rotation = rot;
            this.scale = scl;
            this.title = title;
            this.nodeType = nodeType;
        }

        public void grab(String handedness) {
            this.state = "GRABBED";
            this.grabbedBy = handedness;
        }

        public void release() {
            this.state = "IDLE";
            this.grabbedBy = null;
        }

        public void hover() {
            if (!"GRABBED".equals(state)) this.state = "HOVERED";
        }

        public void unhover() {
            if ("HOVERED".equals(state)) this.state = "IDLE";
        }

        public void moveTo(double x, double y, double z) {
            this.position = new double[]{x, y, z};
        }

        public double distanceTo(double x, double y, double z) {
            double dx = position[0] - x;
            double dy = position[1] - y;
            double dz = position[2] - z;
            return Math.sqrt(dx * dx + dy * dy + dz * dz);
        }

        public BridgeSchemas.SceneObject toSceneObject() {
            return new BridgeSchemas.SceneObject(
                id, type,
                List.of(position[0], position[1], position[2]),
                List.of(rotation[0], rotation[1], rotation[2]),
                List.of(scale[0], scale[1], scale[2]),
                state, grabbedBy,
                new BridgeSchemas.SceneObjectMetadata(title, nodeType, List.of())
            );
        }
    }
}
