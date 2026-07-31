import pytest
import numpy as np
from app.core.voice_detector import VoiceDetector
from app.core.cpp_wrapper import NativeDSPWrapper

def test_cpp_wrapper_fallback():
    wrapper = NativeDSPWrapper()
    fake_audio = np.random.uniform(-1.0, 1.0, 1000)
    score = wrapper.detect_deepfake_confidence(fake_audio, librosa_score=0.8)
    assert isinstance(score, float)
    assert 50.0 <= score <= 98.5

def test_voice_detector_analysis():
    detector = VoiceDetector()
    dummy_bytes = b"\x00\xFF\x80\x7F" * 200
    result = detector.analyze_audio_bytes(dummy_bytes)

    assert "is_ai_generated" in result
    assert "confidence_percent" in result
    assert result["accuracy_target"] == "94.2%"
    assert result["cpp_native_dsp_integrated"] is True
    assert result["dsp_module"] == "native_dsp.cpp"
