cmake_minimum_required(VERSION 3.10)

project(@@PROJECT_NAME@@)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include_directories(include)

add_executable(@@PROJECT_NAME@@ src/main.cpp)

install(TARGETS @@PROJECT_NAME@@ DESTINATION bin)
