/* MQ C code-flow runtime (experiment). Prepended to an instrumented copy of the learner's main.c and
   compiled by the SAME TinyCC 0.9.27 the grader uses. It never dereferences learner pointers: it only
   copies the bytes of variables it was told about (their own address and sizeof), and of malloc blocks
   it allocated itself. Records go to mq_trace.txt and are flushed at every step, so a crash keeps them. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MQ_MAX_FRAMES 128
#define MQ_MAX_VARS 1024
#define MQ_MAX_BLOCKS 256
#define MQ_MAX_BYTES 256
#define MQ_BUDGET 1000
static FILE *mq_out;
static int mq_steps;
static struct { int fid; char *fa; int line; } mq_frames[MQ_MAX_FRAMES];
static int mq_nframes;
static struct { char *fa; int id; char *addr; int size; } mq_vars[MQ_MAX_VARS];
static int mq_nvars;
static struct { char *addr; size_t size; int serial; } mq_blocks[MQ_MAX_BLOCKS];
static int mq_serial;   /* allocation order, so a block can be matched with the original run's */
static int mq_nblocks;
void __mq_layout(FILE *out);

static void mq_open(void) {
    if (mq_out) return;
    mq_out = fopen("mq_trace.txt", "w");
    __mq_layout(mq_out);
}
/* Frames deeper than `fa` (lower addresses: the stack grows down) have returned. */
static void mq_pop_below(char *fa, int inclusive) {
    while (mq_nframes > 0 && (mq_frames[mq_nframes - 1].fa < fa || (inclusive && mq_frames[mq_nframes - 1].fa == fa))) {
        char *gone = mq_frames[--mq_nframes].fa;
        while (mq_nvars > 0 && mq_vars[mq_nvars - 1].fa == gone) mq_nvars--;
    }
}
static void mq_hex(char *p, size_t n) {
    size_t i;
    if (n > MQ_MAX_BYTES) n = MQ_MAX_BYTES;
    for (i = 0; i < n; i++) fprintf(mq_out, "%02x", (unsigned char)p[i]);
}
static void mq_snapshot(const char *event, int line, long long ret) {
    int i;
    fflush(stdout);
    fprintf(mq_out, "S %s %d %ld %lld\n", event, line, ftell(stdout), ret);
    for (i = 0; i < mq_nframes; i++) fprintf(mq_out, "F %d %p %d\n", mq_frames[i].fid, mq_frames[i].fa, mq_frames[i].line);
    for (i = 0; i < mq_nvars; i++) {
        fprintf(mq_out, "V %p %d %p %d ", mq_vars[i].fa, mq_vars[i].id, mq_vars[i].addr, mq_vars[i].size);
        mq_hex(mq_vars[i].addr, mq_vars[i].size);
        fputc('\n', mq_out);
    }
    for (i = 0; i < mq_nblocks; i++) {
        fprintf(mq_out, "H %p %llu %d ", mq_blocks[i].addr, (unsigned long long)mq_blocks[i].size, mq_blocks[i].serial);
        mq_hex(mq_blocks[i].addr, mq_blocks[i].size);
        fputc('\n', mq_out);
    }
    fflush(mq_out);
    if (++mq_steps >= MQ_BUDGET) { fprintf(mq_out, "LIMIT\n"); fflush(mq_out); fflush(stdout); _exit(0); }
}
void __mq_enter(int fid, int line, char *fa) {
    mq_open();
    mq_pop_below(fa, 1);
    if (mq_nframes < MQ_MAX_FRAMES) { mq_frames[mq_nframes].fid = fid; mq_frames[mq_nframes].fa = fa; mq_frames[mq_nframes].line = line; mq_nframes++; }
}
/* After the parameters were registered: the `call` step. */
void __mq_called(int line) { mq_snapshot("call", line, 0); }
void __mq_var(int id, void *addr, int size, char *fa) {
    int i;
    mq_open();
    mq_pop_below(fa, 0);   /* a callee that returned since the last step must not keep its locals */
    for (i = 0; i < mq_nvars; i++) if (mq_vars[i].id == id && mq_vars[i].fa == fa) { mq_vars[i].addr = addr; return; }
    if (mq_nvars < MQ_MAX_VARS) { mq_vars[mq_nvars].fa = fa; mq_vars[mq_nvars].id = id; mq_vars[mq_nvars].addr = addr; mq_vars[mq_nvars].size = size; mq_nvars++; }
}
void __mq_line(int line, char *fa) {
    mq_open();
    mq_pop_below(fa, 0);
    if (mq_nframes > 0) mq_frames[mq_nframes - 1].line = line;
    mq_snapshot("step_line", line, 0);
}
long long __mq_ret(int line, char *fa, long long value) {
    mq_open();
    mq_pop_below(fa, 0);
    if (mq_nframes > 0) mq_frames[mq_nframes - 1].line = line;
    mq_snapshot("return", line, value);
    return value;
}
void *__mq_malloc(size_t n) {
    void *p = malloc(n);
    if (p && mq_nblocks < MQ_MAX_BLOCKS) { mq_blocks[mq_nblocks].addr = p; mq_blocks[mq_nblocks].size = n; mq_blocks[mq_nblocks].serial = ++mq_serial; mq_nblocks++; }
    return p;
}
static void mq_forget(void *p) {
    int i;
    for (i = 0; i < mq_nblocks; i++) if (mq_blocks[i].addr == p) { mq_blocks[i] = mq_blocks[--mq_nblocks]; break; }
}
static void mq_remember(void *p, size_t n) {
    if (p && mq_nblocks < MQ_MAX_BLOCKS) { mq_blocks[mq_nblocks].addr = p; mq_blocks[mq_nblocks].size = n; mq_blocks[mq_nblocks].serial = ++mq_serial; mq_nblocks++; }
}
void *__mq_calloc(size_t count, size_t size) { void *p = calloc(count, size); mq_remember(p, count * size); return p; }
void *__mq_realloc(void *old, size_t n) {
    void *p = realloc(old, n);
    if (p || n == 0) mq_forget(old);
    mq_remember(p, n);
    return p;
}
void __mq_free(void *p) {
    int i;
    for (i = 0; i < mq_nblocks; i++) if (mq_blocks[i].addr == p) { mq_blocks[i] = mq_blocks[--mq_nblocks]; break; }
    free(p);
}
#define malloc(n) __mq_malloc(n)
#define free(p) __mq_free(p)
#define calloc(c, n) __mq_calloc(c, n)
#define realloc(p, n) __mq_realloc(p, n)
