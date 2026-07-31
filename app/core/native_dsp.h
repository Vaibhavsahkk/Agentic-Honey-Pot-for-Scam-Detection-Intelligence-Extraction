#ifndef NATIVE_DSP_H
#define NATIVE_DSP_H

#ifdef _WIN32
#define EXPORT_API __declspec(dllexport)
#else
#define EXPORT_API __attribute__((visibility("default")))
#endif

extern "C" {
    // Calculates Zero Crossing Rate and Spectral Energy ratio for AI deepfake voice audio signal
    EXPORT_API double calculate_spectral_energy(const double* audio_buffer, int buffer_size);
    EXPORT_API double calculate_zero_crossing_rate(const double* audio_buffer, int buffer_size);
    EXPORT_API double detect_deepfake_confidence(const double* audio_buffer, int buffer_size, double librosa_feature_val);
}

#endif // NATIVE_DSP_H
