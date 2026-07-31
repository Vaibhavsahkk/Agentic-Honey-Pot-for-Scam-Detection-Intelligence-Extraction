cmake_minimum_required(VERSION 3.10)
project(native_dsp VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(native_dsp SHARED app/core/native_dsp.cpp)

set_target_properties(native_dsp PROPERTIES
    PUBLIC_HEADER app/core/native_dsp.h
    POSITION_INDEPENDENT_CODE ON
)
