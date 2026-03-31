package com.holodocs.session;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Manages per-session state. Each session gets its own SceneGraph and state.
 * Thread-safe — sessions can be accessed from HTTP handler and WS pusher concurrently.
 */
@Service
public class SessionManager {

    private static final Logger log = LoggerFactory.getLogger(SessionManager.class);
    private final Map<String, SessionState> sessions = new ConcurrentHashMap<>();

    public SessionState getOrCreate(String sessionId) {
        return sessions.computeIfAbsent(sessionId, id -> {
            log.info("Creating new session: {}", id);
            return new SessionState(id);
        });
    }

    public SessionState get(String sessionId) {
        return sessions.get(sessionId);
    }

    public void remove(String sessionId) {
        sessions.remove(sessionId);
        log.info("Removed session: {}", sessionId);
    }

    public int activeCount() {
        return sessions.size();
    }
}
