
if(CONFIG_CAR_ENCODER)

	zephyr_sources(timer_encoder.c)
	zephyr_sources_ifdef(CONFIG_USERSPACE timer_encoder_handler.c)

endif()
