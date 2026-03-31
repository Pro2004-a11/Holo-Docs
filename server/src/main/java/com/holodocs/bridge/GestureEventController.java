package com.holodocs.bridge;

import com.holodocs.scene.GestureInterpreter;
import com.holodocs.session.SessionManager;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * Receives gesture events from the Vision service via HTTP POST.
 * Delegates to GestureInterpreter to mutate scene state.
 */
@RestController
@RequestMapping("/api")
public class GestureEventController {

    private static final Logger log = LoggerFactory.getLogger(GestureEventController.class);

    private final SessionManager sessionManager;
    private final GestureInterpreter gestureInterpreter;

    public GestureEventController(SessionManager sessionManager, GestureInterpreter gestureInterpreter) {
        this.sessionManager = sessionManager;
        this.gestureInterpreter = gestureInterpreter;
    }

    @PostMapping("/gesture-event")
    public ResponseEntity<Void> receiveGestureEvent(@RequestBody BridgeSchemas.GestureEvent event) {
        if (event.sessionId() == null) {
            return ResponseEntity.badRequest().build();
        }

        var session = sessionManager.getOrCreate(event.sessionId());

        // Apply gesture to scene state
        gestureInterpreter.apply(session, event);

        // Scene state push happens via the WebSocket handler on its own schedule
        return ResponseEntity.ok().build();
    }

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("{\"status\":\"ok\",\"sessions\":" + sessionManager.activeCount() + "}");
    }
}
