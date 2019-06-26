cmake_minimum_required(VERSION 3.13.1)
project(base)

set(DTC_OVERLAY_FILE dts/stm32f7.overlay.dts)

include($ENV{ZEPHYR_BASE}/cmake/app/boilerplate.cmake NO_POLICY_SCOPE)

# set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DUSE_FULL_LL_DRIVER")
# add_definitions(-DUSE_FULL_LL_DRIVER)

# include(test.cmake)

# Drivers
add_subdirectory_ifdef(CONFIG_CAR_ENCODER drivers/timer_encoder)
# add_subdirectory_ifdef(CONFIG_WIFI_ESP32 drivers/esp32)

zephyr_include_directories(include)

# Application
FILE(GLOB app_sources
	# src/encoder_run.c
	src/main.c
	# src/test_esp32_uart.c
	drivers/wifi/esp32_core.c
	# src/test_esp32_spi.c
	# src/test_pwm.c
	# src/device_list.c
	# src/test_spi.c
	# src/test_base.c
	# src/test_thread.c
	# src/test_thread_wrap.c
	# src/test_asm.c
)

target_sources(app PRIVATE ${app_sources})
