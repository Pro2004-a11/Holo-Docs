package com.holodocs.session;

import com.holodocs.bridge.BridgeSchemas;
import com.holodocs.scene.SceneGraph;

import java.util.List;

/**
 * Per-session state container. Holds the scene graph, current lighting,
 * HUD state, and latest frame sequence number.
 */
public class SessionState {

    private final String sessionId;
    private final SceneGraph sceneGraph;

    // Latest CV-derived state
    private volatile List<Double> cursorPosition = List.of(0.5, 0.5);
    private volatile String activeGesture = "IDLE";
    private volatile BridgeSchemas.LightVector lightVector;
    private volatile int lastFrameSeq = 0;

    public SessionState(String sessionId) {
        this.sessionId = sessionId;
        this.sceneGraph = new SceneGraph();
        this.lightVector = new BridgeSchemas.LightVector(
            List.of(0.0, -1.0, 0.5), 0.8, List.of(255, 255, 255)
        );
    }

    public String getSessionId() { return sessionId; }
    public SceneGraph getSceneGraph() { return sceneGraph; }

    public void updateCursor(List<Double> position) {
        this.cursorPosition = position;
    }

    public void updateGesture(String gesture) {
        this.activeGesture = gesture;
    }

    public void updateLighting(BridgeSchemas.LightVector lv) {
        if (lv != null) this.lightVector = lv;
    }

    public void updateFrameSeq(int seq) {
        this.lastFrameSeq = seq;
    }

    /**
     * Snapshot current state into a SceneState message for the browser.
     */
    public BridgeSchemas.SceneState toSceneState() {
        return new BridgeSchemas.SceneState(
            "bridge/scene-state",
            "1.0",
            sessionId,
            System.currentTimeMillis(),
            lastFrameSeq,
            sceneGraph.toSceneObjects(),
            new BridgeSchemas.SceneLighting(
                lightVector.direction(),
                lightVector.intensity(),
                lightVector.dominantColor()
            ),
            new BridgeSchemas.HudState(cursorPosition, activeGesture, null)
        );
    }
}
