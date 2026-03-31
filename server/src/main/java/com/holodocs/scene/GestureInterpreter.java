package com.holodocs.scene;

import com.holodocs.bridge.BridgeSchemas;
import com.holodocs.session.SessionState;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * Translates gesture events into scene mutations.
 * Core logic: pinch near object → grab, move hand → move object, release → drop.
 */
@Component
public class GestureInterpreter {

    private static final Logger log = LoggerFactory.getLogger(GestureInterpreter.class);

    // How close the hand must be to grab (in normalized coords mapped to scene space)
    private static final double GRAB_RADIUS = 0.5;

    // Scale factor: normalized hand coords (0-1) → scene space
    private static final double SCENE_SCALE_X = 4.0;  // scene is roughly -2 to 2
    private static final double SCENE_SCALE_Y = 3.0;
    private static final double SCENE_Z = -2.0;       // fixed depth for MVP

    public void apply(SessionState session, BridgeSchemas.GestureEvent event) {
        session.updateFrameSeq(event.frameSeq());
        session.updateLighting(event.lightVector());

        if (event.hands() == null || event.hands().isEmpty()) {
            return;
        }

        for (BridgeSchemas.HandData hand : event.hands()) {
            String handedness = hand.handedness();
            BridgeSchemas.Gesture gesture = hand.gesture();
            List<Double> indexTip = hand.landmarks().indexTip();

            // Map normalized coords to scene space
            double sceneX = (indexTip.get(0) - 0.5) * SCENE_SCALE_X;
            double sceneY = (0.5 - indexTip.get(1)) * SCENE_SCALE_Y; // flip Y
            double sceneZ = SCENE_Z;

            // Update cursor position for HUD
            session.updateCursor(List.of(indexTip.get(0), indexTip.get(1)));
            session.updateGesture(gesture.type());

            SceneGraph graph = session.getSceneGraph();

            switch (gesture.type()) {
                case "PINCH" -> handlePinch(graph, handedness, sceneX, sceneY, sceneZ);
                case "PINCH_RELEASE" -> handleRelease(graph, handedness);
                case "POINT" -> handlePoint(graph, sceneX, sceneY, sceneZ);
                default -> {
                    // IDLE, SWIPE, OPEN_PALM — clear hover state
                    SceneGraph.SceneNode hovered = graph.findClosest(sceneX, sceneY, sceneZ, GRAB_RADIUS);
                    if (hovered != null) hovered.unhover();
                }
            }
        }
    }

    private void handlePinch(SceneGraph graph, String handedness,
                             double x, double y, double z) {
        // Already grabbing something? Move it.
        SceneGraph.SceneNode grabbed = graph.findGrabbedBy(handedness);
        if (grabbed != null) {
            grabbed.moveTo(x, y, z);
            return;
        }

        // Try to grab nearest object
        SceneGraph.SceneNode nearest = graph.findClosest(x, y, z, GRAB_RADIUS);
        if (nearest != null) {
            nearest.grab(handedness);
            nearest.moveTo(x, y, z);
            log.debug("Grabbed {} with {}", nearest, handedness);
        }
    }

    private void handleRelease(SceneGraph graph, String handedness) {
        SceneGraph.SceneNode grabbed = graph.findGrabbedBy(handedness);
        if (grabbed != null) {
            grabbed.release();
            log.debug("Released {}", grabbed);
        }
    }

    private void handlePoint(SceneGraph graph, double x, double y, double z) {
        SceneGraph.SceneNode nearest = graph.findClosest(x, y, z, GRAB_RADIUS);
        if (nearest != null) {
            nearest.hover();
        }
    }
}
