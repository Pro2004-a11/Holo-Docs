import { useMemo } from 'react';
import type { SceneState, GestureType } from '../types/bridge';

/**
 * Derives convenience values from the raw scene state.
 */
export function useGestureState(sceneState: SceneState | null) {
  return useMemo(() => {
    if (!sceneState) {
      return {
        cursorX: 0.5,
        cursorY: 0.5,
        activeGesture: 'IDLE' as GestureType,
        isTracking: false,
        hasGrabbedObject: false,
      };
    }

    const hud = sceneState.hud;
    const hasGrabbed = sceneState.scene_objects.some((o) => o.state === 'GRABBED');

    return {
      cursorX: hud.cursor_position[0],
      cursorY: hud.cursor_position[1],
      activeGesture: hud.active_gesture,
      isTracking: hud.active_gesture !== 'IDLE',
      hasGrabbedObject: hasGrabbed,
    };
  }, [sceneState]);
}
