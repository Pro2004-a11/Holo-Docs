package com.holodocs.bridge;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.holodocs.session.SessionManager;
import com.holodocs.session.SessionState;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * WebSocket handler that pushes scene state to browser clients at 30Hz.
 * One WS connection per browser session.
 */
@Component
public class SceneWebSocketHandler extends TextWebSocketHandler {

    private static final Logger log = LoggerFactory.getLogger(SceneWebSocketHandler.class);
    private static final long PUSH_INTERVAL_MS = 33; // ~30Hz

    private final SessionManager sessionManager;
    private final ObjectMapper objectMapper;
    private final Map<String, WebSocketSession> activeSessions = new ConcurrentHashMap<>();
    private final ScheduledExecutorService pushScheduler;

    public SceneWebSocketHandler(SessionManager sessionManager, ObjectMapper objectMapper) {
        this.sessionManager = sessionManager;
        this.objectMapper = objectMapper;

        // Virtual thread executor for state pushing
        this.pushScheduler = Executors.newScheduledThreadPool(1, Thread.ofVirtual().factory());
        this.pushScheduler.scheduleAtFixedRate(this::pushAllStates, 100, PUSH_INTERVAL_MS, TimeUnit.MILLISECONDS);
    }

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        String sessionId = extractSessionId(session);
        if (sessionId != null) {
            activeSessions.put(sessionId, session);
            sessionManager.getOrCreate(sessionId);
            log.info("Browser connected: session={}", sessionId);
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        String sessionId = extractSessionId(session);
        if (sessionId != null) {
            activeSessions.remove(sessionId);
            log.info("Browser disconnected: session={}", sessionId);
        }
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) {
        // Client can send commands (future: menu actions, etc.)
        log.debug("Received from client: {}", message.getPayload());
    }

    private void pushAllStates() {
        for (var entry : activeSessions.entrySet()) {
            String sessionId = entry.getKey();
            WebSocketSession ws = entry.getValue();

            if (!ws.isOpen()) {
                activeSessions.remove(sessionId);
                continue;
            }

            SessionState state = sessionManager.get(sessionId);
            if (state == null) continue;

            try {
                BridgeSchemas.SceneState sceneState = state.toSceneState();
                String json = objectMapper.writeValueAsString(sceneState);
                ws.sendMessage(new TextMessage(json));
            } catch (IOException e) {
                log.warn("Failed to push state to session {}: {}", sessionId, e.getMessage());
            }
        }
    }

    private String extractSessionId(WebSocketSession session) {
        // URI pattern: /ws/scene/{sessionId}
        String path = session.getUri() != null ? session.getUri().getPath() : "";
        String[] parts = path.split("/");
        return parts.length > 0 ? parts[parts.length - 1] : null;
    }
}
