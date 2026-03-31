package com.holodocs.config;

import com.holodocs.bridge.SceneWebSocketHandler;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    private final SceneWebSocketHandler sceneHandler;

    public WebSocketConfig(SceneWebSocketHandler sceneHandler) {
        this.sceneHandler = sceneHandler;
    }

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(sceneHandler, "/ws/scene/{sessionId}")
                .setAllowedOrigins("*");
    }
}
