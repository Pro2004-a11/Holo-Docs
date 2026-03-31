package com.holodocs.bridge;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

/**
 * DTOs matching the Bridge Protocol JSON schemas.
 * These mirror the Python Pydantic models and TypeScript types.
 */
public class BridgeSchemas {

    // ── Gesture Event (Vision → Orchestrator) ──

    public record GestureEvent(
        @JsonProperty("$schema") String schema,
        String version,
        @JsonProperty("session_id") String sessionId,
        long timestamp,
        @JsonProperty("frame_seq") int frameSeq,
        List<HandData> hands,
        @JsonProperty("head_pose") HeadPose headPose,
        @JsonProperty("light_vector") LightVector lightVector
    ) {}

    public record HandData(
        String handedness,
        HandLandmarks landmarks,
        Gesture gesture
    ) {}

    public record HandLandmarks(
        List<Double> wrist,
        @JsonProperty("thumb_tip") List<Double> thumbTip,
        @JsonProperty("index_tip") List<Double> indexTip,
        @JsonProperty("middle_tip") List<Double> middleTip,
        @JsonProperty("ring_tip") List<Double> ringTip,
        @JsonProperty("pinky_tip") List<Double> pinkyTip,
        @JsonProperty("palm_center") List<Double> palmCenter
    ) {}

    public record Gesture(
        String type,
        double confidence,
        @JsonProperty("pinch_distance") Double pinchDistance
    ) {}

    public record HeadPose(double pitch, double yaw, double roll) {}

    public record LightVector(
        List<Double> direction,
        double intensity,
        @JsonProperty("dominant_color") List<Integer> dominantColor
    ) {}

    // ── Scene State (Orchestrator → Browser) ──

    public record SceneState(
        @JsonProperty("$schema") String schema,
        String version,
        @JsonProperty("session_id") String sessionId,
        long timestamp,
        @JsonProperty("frame_seq") int frameSeq,
        @JsonProperty("scene_objects") List<SceneObject> sceneObjects,
        SceneLighting lighting,
        HudState hud
    ) {}

    public record SceneObject(
        String id,
        String type,
        List<Double> position,
        List<Double> rotation,
        List<Double> scale,
        String state,
        @JsonProperty("grabbed_by") String grabbedBy,
        SceneObjectMetadata metadata
    ) {}

    public record SceneObjectMetadata(
        String title,
        @JsonProperty("node_type") String nodeType,
        List<String> connections
    ) {}

    public record SceneLighting(
        List<Double> direction,
        double intensity,
        List<Integer> color
    ) {}

    public record HudState(
        @JsonProperty("cursor_position") List<Double> cursorPosition,
        @JsonProperty("active_gesture") String activeGesture,
        @JsonProperty("feedback_text") String feedbackText
    ) {}
}
