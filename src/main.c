#include "main.h"

#if CONFIG_ZTEST
void test_main(void)
#else
void main(void)
#endif
{
	test_userspace();
}
