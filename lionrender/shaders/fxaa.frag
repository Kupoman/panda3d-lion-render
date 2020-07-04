#version 330
#extension GL_ARB_gpu_shader5 : require

#define FXAA_PC 1
#define FXAA_GLSL_130 1
#define FXAA_QUALITY_PRESET 12
#define FXAA_GREEN_AS_LUMA 1

#pragma include "fxaa.lib"

in vec2 texcoord;
out vec4 outFrag;

uniform sampler2D inputTexture;
uniform float subpix = 0.75;
uniform float edgeThreshold = 0.166;
uniform float edgeThresholdMin = 0.0;

void main() {
    vec2 rcpFrame = vec2(1.0) / textureSize(inputTexture, 0);

    outFrag = FxaaPixelShader(
        texcoord,
        vec4(0.0),
        inputTexture,
        inputTexture,
        inputTexture,
        rcpFrame,
        vec4(0.0),
        vec4(0.0),
        vec4(0.0),
        subpix,
        edgeThreshold,
        edgeThresholdMin,
        0.0,
        0.0,
        0.0,
        vec4(0.0)
    );
}
