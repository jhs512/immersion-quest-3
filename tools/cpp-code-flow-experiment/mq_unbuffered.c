/* Experiment helper linked beside the learner's main.c (the learner's file is not changed).
   Before main runs, stdout is made unbuffered so that each recorded step can show the output printed
   so far. Without it the CRT buffers a redirected stdout until exit and every step shows nothing. */
#include <stdio.h>
static int mq_unbuffer(void) { setvbuf(stdout, NULL, _IONBF, 0); return 0; }
#pragma section(".CRT$XCU", read)
__declspec(allocate(".CRT$XCU")) static int (*mq_unbuffer_entry)(void) = mq_unbuffer;
