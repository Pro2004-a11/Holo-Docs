// Hologram shader for document cards — adds scan lines and edge glow.
// Used as a custom material in Three.js via ShaderMaterial.

// Vertex
varying vec2 vUv;
varying vec3 vNormal;

void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}

// Fragment — paste below into fragment shader string
// uniform float uTime;
// uniform vec3 uColor;
// varying vec2 vUv;
// varying vec3 vNormal;
//
// void main() {
//   // Scan lines
//   float scanLine = sin(vUv.y * 120.0 + uTime * 2.0) * 0.03;
//
//   // Edge glow (fresnel)
//   vec3 viewDir = normalize(cameraPosition - vNormal);
//   float fresnel = pow(1.0 - max(dot(vNormal, viewDir), 0.0), 3.0);
//
//   vec3 color = uColor + scanLine + fresnel * 0.3;
//   float alpha = 0.75 + fresnel * 0.2;
//
//   gl_FragColor = vec4(color, alpha);
// }
