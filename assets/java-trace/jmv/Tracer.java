package jmv;

import java.io.OutputStream;
import java.io.PrintStream;
import java.lang.reflect.Array;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collection;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Runtime recorder called from instrumented user bytecode.
 *
 * Step model: one snapshot per {@code call}, {@code step_line}, {@code return},
 * {@code exception} and {@code uncaught_exception} event (same granularity as pythontutor).
 * Each snapshot is the full educational state: shadow call stack with named locals,
 * static fields of initialized user classes, and every heap object reachable from them.
 * Object IDs come from an identity registry, so the same object keeps its number across steps.
 *
 * Not a JVM memory dump: no addresses, headers, operand stacks, GC or library internals.
 */
public final class Tracer {
    /** Thrown into user code when the step budget is exhausted; hooks disable themselves first. */
    public static final class StepLimit extends Error {
        StepLimit() { super("step limit reached"); }
    }

    static final class Local {
        final String desc; final Object value;
        Local(String desc, Object value) { this.desc = desc; this.value = value; }
    }

    static final class Frame {
        final int id; final String owner; final String name; int line;
        final LinkedHashMap<String, Local> locals = new LinkedHashMap<>();
        Frame(int id, String owner, String name) { this.id = id; this.owner = owner; this.name = name; }
    }

    static final ArrayList<Frame> frames = new ArrayList<>();
    static final IdentityHashMap<Object, Integer> ids = new IdentityHashMap<>();
    static final LinkedHashSet<Class<?>> initialized = new LinkedHashSet<>();
    static final ArrayList<String> steps = new ArrayList<>();
    static final StringBuilder stdout = new StringBuilder();
    static Set<String> userClasses = Set.of();
    static boolean enabled, pendingCall, limitHit, heapTruncated;
    /** Option: show String and boxed primitives as heap objects (identity visible) instead of inline values. */
    static boolean boxAsObjects;
    static int nextFrameId, maxSteps = 1000, maxObjects = 300, maxStdout = 64 * 1024;
    static long ticks, maxTicks = 2_000_000; // loop back-edges + line hits; guards loops that never change line
    static long snapshotNs;
    static PrintStream originalOut, originalErr;

    private Tracer() {}

    public static void reset(Set<String> classes, int stepBudget) { reset(classes, stepBudget, false); }

    public static void reset(Set<String> classes, int stepBudget, boolean objects) {
        boxAsObjects = objects;
        frames.clear(); ids.clear(); initialized.clear(); steps.clear(); stdout.setLength(0);
        userClasses = classes; maxSteps = stepBudget; nextFrameId = 0; snapshotNs = 0; ticks = 0;
        enabled = true; pendingCall = false; limitHit = false; heapTruncated = false;
    }

    public static void captureOutput() {
        originalOut = System.out; originalErr = System.err;
        PrintStream capture = new PrintStream(new OutputStream() {
            @Override public void write(int b) { append(new byte[]{(byte) b}, 0, 1); }
            @Override public void write(byte[] b, int off, int len) { append(b, off, len); }
        }, true, StandardCharsets.UTF_8);
        System.setOut(capture); System.setErr(capture);
    }

    public static void restoreOutput() {
        if (originalOut != null) System.setOut(originalOut);
        if (originalErr != null) System.setErr(originalErr);
    }

    static synchronized void append(byte[] b, int off, int len) {
        if (stdout.length() >= maxStdout) return;
        stdout.append(new String(b, off, len, StandardCharsets.UTF_8));
    }

    // ---- hooks invoked from instrumented bytecode -------------------------------------------

    public static void enter(String owner, String name, Class<?> cls, Object self) {
        if (!enabled) return;
        initialized.add(cls);
        Frame frame = new Frame(++nextFrameId, owner, name);
        frames.add(frame);
        if (self != null) frame.locals.put("this", new Local("L" + owner + ";", self));
        pendingCall = true;
    }

    public static void local(String name, String desc, Object value) {
        if (!enabled || frames.isEmpty()) return;
        if (name.startsWith("slot") || name.indexOf('$') >= 0) return; // unnamed or synthetic
        frames.get(frames.size() - 1).locals.put(name, new Local(desc, value));
    }

    public static void scopeEnd(String name) {
        if (!enabled || frames.isEmpty()) return;
        frames.get(frames.size() - 1).locals.remove(name);
    }

    /** Called before every backward jump; stops programs that spin without producing steps. */
    public static void tick() {
        if (!enabled) return;
        if (++ticks > maxTicks) {
            steps.add(snapshot("instruction_limit_reached", null));
            enabled = false; limitHit = true;
            throw new StepLimit();
        }
    }

    public static void line(int line) {
        if (!enabled || frames.isEmpty()) return;
        tick();
        Frame top = frames.get(frames.size() - 1);
        if (pendingCall) { pendingCall = false; top.line = line; step("call", null); return; }
        if (top.line == line) return; // same line within the same frame: no new step (JDI line-step semantics)
        top.line = line;
        step("step_line", null);
    }

    public static void ret(Object value, String desc) {
        if (!enabled || frames.isEmpty()) return;
        Frame top = frames.get(frames.size() - 1);
        pendingCall = false;
        if (!desc.equals("V") && !top.name.equals("<init>")) top.locals.put("__return__", new Local(desc, value));
        step("return", null);
        frames.remove(frames.size() - 1);
    }

    public static void exceptionExit(Throwable t) {
        if (!enabled || frames.isEmpty()) return;
        pendingCall = false;
        String message = t.getClass().getSimpleName() + (t.getMessage() == null ? "" : ": " + t.getMessage());
        step(frames.size() == 1 ? "uncaught_exception" : "exception", message);
        frames.remove(frames.size() - 1);
    }

    // ---- snapshot ---------------------------------------------------------------------------

    static void step(String event, String exceptionMessage) {
        long start = System.nanoTime();
        try {
            if (steps.size() >= maxSteps) {
                steps.add(snapshot("instruction_limit_reached", null));
                enabled = false; limitHit = true;
                throw new StepLimit();
            }
            steps.add(snapshot(event, exceptionMessage));
        } finally {
            snapshotNs += System.nanoTime() - start;
        }
    }

    static String snapshot(String event, String exceptionMessage) {
        StringBuilder b = new StringBuilder(1024);
        Frame top = frames.isEmpty() ? null : frames.get(frames.size() - 1);
        ArrayDeque<Object> pending = new ArrayDeque<>();
        b.append("{\"event\":").append(json(event));
        b.append(",\"line\":").append(top == null ? 0 : top.line);
        b.append(",\"func_name\":").append(json(top == null ? "" : top.name));
        if (exceptionMessage != null) b.append(",\"exception_msg\":").append(json(exceptionMessage));
        b.append(",\"stdout\":").append(json(stdout.toString()));

        // static fields of user classes whose initialization has started
        StringBuilder globals = new StringBuilder(), order = new StringBuilder();
        for (Class<?> c : initialized) {
            for (Field f : c.getDeclaredFields()) {
                if (!Modifier.isStatic(f.getModifiers()) || f.isSynthetic()) continue;
                String key = simpleName(c) + "." + f.getName();
                Object value;
                try { f.setAccessible(true); value = f.get(null); } catch (Throwable e) { continue; }
                if (globals.length() > 0) { globals.append(','); order.append(','); }
                globals.append(json(key)).append(':').append(encode(value, descriptor(f.getType()), pending));
                order.append(json(key));
            }
        }
        b.append(",\"globals\":{").append(globals).append("},\"ordered_globals\":[").append(order).append(']');

        b.append(",\"stack_to_render\":[");
        for (int i = 0; i < frames.size(); i++) {
            Frame f = frames.get(i);
            if (i > 0) b.append(',');
            b.append("{\"func_name\":").append(json(f.name)).append(",\"class\":").append(json(displayClass(f.owner)));
            b.append(",\"frame_id\":").append(f.id).append(",\"line\":").append(f.line);
            b.append(",\"is_highlighted\":").append(i == frames.size() - 1);
            StringBuilder locals = new StringBuilder(), names = new StringBuilder();
            for (Map.Entry<String, Local> e : f.locals.entrySet()) {
                if (locals.length() > 0) { locals.append(','); names.append(','); }
                locals.append(json(e.getKey())).append(':').append(encode(e.getValue().value, e.getValue().desc, pending));
                names.append(json(e.getKey()));
            }
            b.append(",\"encoded_locals\":{").append(locals).append("},\"ordered_varnames\":[").append(names).append("]}");
        }
        b.append(']');

        b.append(",\"heap\":{");
        IdentityHashMap<Object, Boolean> visited = new IdentityHashMap<>();
        boolean first = true; int count = 0;
        internalQueue = new ArrayDeque<>();
        while (!pending.isEmpty()) {
            Object o = pending.poll();
            if (visited.put(o, Boolean.TRUE) != null) continue;
            if (++count > maxObjects) { heapTruncated = true; break; }
            if (!first) b.append(',');
            first = false;
            b.append('"').append(id(o)).append("\":");
            encodeObject(o, b, pending);
        }
        // Phase 2: objects reachable only through library internals (ArrayList backing array,
        // LinkedList nodes). Listed under "internal" so the renderer can hide them until asked.
        StringBuilder internalIds = new StringBuilder();
        while (!internalQueue.isEmpty()) {
            Object o = internalQueue.poll();
            if (visited.put(o, Boolean.TRUE) != null) continue;
            if (++count > maxObjects) { heapTruncated = true; break; }
            if (!first) b.append(',');
            first = false;
            b.append('"').append(id(o)).append("\":");
            encodeObject(o, b, internalQueue);
            if (internalIds.length() > 0) internalIds.append(',');
            internalIds.append(id(o));
        }
        b.append("},\"internal\":[").append(internalIds).append("]}");
        return b.toString();
    }

    static ArrayDeque<Object> internalQueue = new ArrayDeque<>();

    /**
     * Reads java.util.ArrayList / LinkedList internals through sun.misc.Unsafe field offsets.
     * Plain reflection is blocked by module encapsulation (java.base does not open java.util),
     * and CheerpJ enforces that too; Unsafe offsets work in both. Everything degrades to "no
     * internals" if any step fails.
     */
    static final class Internals {
        static final boolean available;
        static final Object unsafe;
        static final java.lang.reflect.Method getObject, getInt;
        static final java.lang.reflect.Method getFloat;
        static final long listData, listSize, linkedFirst, linkedLast, linkedSize, nodeItem, nodeNext, nodePrev;
        static final long mapTable, mapSize, mapThreshold, mapLoadFactor, hashNodeHash, hashNodeKey, hashNodeValue, hashNodeNext, setMap;
        static final Object present; // HashSet.PRESENT: the dummy value every HashSet entry maps to
        static final Class<?> nodeClass, hashNodeClass;
        static {
            boolean ok = false; Object u = null; java.lang.reflect.Method go = null, gi = null, gf = null; Class<?> nc = null, hc = null;
            long ld = 0, ls = 0, lf = 0, ll = 0, lz = 0, ni = 0, nn = 0, np = 0;
            long mt = 0, ms = 0, mth = 0, mlf = 0, hh = 0, hk = 0, hv = 0, hn = 0, sm = 0; Object pr = null;
            try {
                Field theUnsafe = Class.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe");
                theUnsafe.setAccessible(true);
                u = theUnsafe.get(null);
                Class<?> uc = u.getClass();
                java.lang.reflect.Method offset = uc.getMethod("objectFieldOffset", Field.class);
                go = uc.getMethod("getObject", Object.class, long.class);
                gi = uc.getMethod("getInt", Object.class, long.class);
                gf = uc.getMethod("getFloat", Object.class, long.class);
                nc = Class.forName("java.util.LinkedList$Node");
                hc = Class.forName("java.util.HashMap$Node");
                ld = (Long) offset.invoke(u, java.util.ArrayList.class.getDeclaredField("elementData"));
                ls = (Long) offset.invoke(u, java.util.ArrayList.class.getDeclaredField("size"));
                lf = (Long) offset.invoke(u, java.util.LinkedList.class.getDeclaredField("first"));
                ll = (Long) offset.invoke(u, java.util.LinkedList.class.getDeclaredField("last"));
                lz = (Long) offset.invoke(u, java.util.LinkedList.class.getDeclaredField("size"));
                ni = (Long) offset.invoke(u, nc.getDeclaredField("item"));
                nn = (Long) offset.invoke(u, nc.getDeclaredField("next"));
                np = (Long) offset.invoke(u, nc.getDeclaredField("prev"));
                mt = (Long) offset.invoke(u, java.util.HashMap.class.getDeclaredField("table"));
                ms = (Long) offset.invoke(u, java.util.HashMap.class.getDeclaredField("size"));
                mth = (Long) offset.invoke(u, java.util.HashMap.class.getDeclaredField("threshold"));
                mlf = (Long) offset.invoke(u, java.util.HashMap.class.getDeclaredField("loadFactor"));
                hh = (Long) offset.invoke(u, hc.getDeclaredField("hash"));
                hk = (Long) offset.invoke(u, hc.getDeclaredField("key"));
                hv = (Long) offset.invoke(u, hc.getDeclaredField("value"));
                hn = (Long) offset.invoke(u, hc.getDeclaredField("next"));
                sm = (Long) offset.invoke(u, java.util.HashSet.class.getDeclaredField("map"));
                Field presentField = java.util.HashSet.class.getDeclaredField("PRESENT");
                Object base = uc.getMethod("staticFieldBase", Field.class).invoke(u, presentField);
                long presentOffset = (Long) uc.getMethod("staticFieldOffset", Field.class).invoke(u, presentField);
                pr = go.invoke(u, base, presentOffset);
                ok = true;
            } catch (Throwable e) { /* internals unavailable */ }
            available = ok; unsafe = u; getObject = go; getInt = gi; getFloat = gf; nodeClass = nc; hashNodeClass = hc;
            listData = ld; listSize = ls; linkedFirst = lf; linkedLast = ll; linkedSize = lz; nodeItem = ni; nodeNext = nn; nodePrev = np;
            mapTable = mt; mapSize = ms; mapThreshold = mth; mapLoadFactor = mlf; hashNodeHash = hh; hashNodeKey = hk; hashNodeValue = hv; hashNodeNext = hn;
            setMap = sm; present = pr;
        }
        static Object obj(Object o, long offset) throws Exception { return getObject.invoke(unsafe, o, offset); }
        static int integer(Object o, long offset) throws Exception { return (Integer) getInt.invoke(unsafe, o, offset); }
        static float real(Object o, long offset) throws Exception { return (Float) getFloat.invoke(unsafe, o, offset); }

        /** JSON object describing the real fields, with referenced internals queued for phase 2; null if unknown. */
        static String describe(Object o, ArrayDeque<Object> internal) {
            if (!available) return null;
            try {
                if (o.getClass() == java.util.ArrayList.class) {
                    return "{\"size\":" + integer(o, listSize) + ",\"elementData\":" + encode(obj(o, listData), "L", internal) + "}";
                }
                if (o.getClass() == java.util.LinkedList.class) {
                    return "{\"size\":" + integer(o, linkedSize) + ",\"first\":" + encode(obj(o, linkedFirst), "L", internal)
                        + ",\"last\":" + encode(obj(o, linkedLast), "L", internal) + "}";
                }
                if (o.getClass() == java.util.HashMap.class || o.getClass() == java.util.LinkedHashMap.class) {
                    return "{\"size\":" + integer(o, mapSize) + ",\"threshold\":" + integer(o, mapThreshold)
                        + ",\"loadFactor\":" + real(o, mapLoadFactor) + ",\"table\":" + encode(obj(o, mapTable), "L", internal) + "}";
                }
                if (o.getClass() == java.util.HashSet.class || o.getClass() == java.util.LinkedHashSet.class) {
                    Object map = obj(o, setMap);
                    return "{\"size\":" + (map == null ? 0 : integer(map, mapSize)) + ",\"map\":" + encode(map, "L", internal) + "}";
                }
            } catch (Throwable e) { /* fall through */ }
            return null;
        }

        static boolean isNode(Object o) { return available && (o.getClass() == nodeClass || hashNodeClass.isInstance(o)); }

        static boolean isHashNodeArray(Class<?> c) { return available && c.isArray() && c.getComponentType() == hashNodeClass; }

        static void encodeNode(Object o, StringBuilder b, ArrayDeque<Object> pending) throws Exception {
            if (hashNodeClass.isInstance(o)) {
                b.append("[\"INSTANCE\",\"HashMap.Node\"");
                b.append(",[\"hash\",").append(integer(o, hashNodeHash)).append(']');
                b.append(",[\"key\",").append(encode(obj(o, hashNodeKey), "L", pending)).append(']');
                Object value = obj(o, hashNodeValue);
                b.append(",[\"value\",").append(value != null && value == present ? "[\"PRESENT\"]" : encode(value, "L", pending)).append(']');
                b.append(",[\"next\",").append(encode(obj(o, hashNodeNext), "L", pending)).append(']');
                b.append(']');
                return;
            }
            b.append("[\"INSTANCE\",\"LinkedList.Node\"");
            b.append(",[\"item\",").append(encode(obj(o, nodeItem), "L", pending)).append(']');
            b.append(",[\"next\",").append(encode(obj(o, nodeNext), "L", pending)).append(']');
            b.append(",[\"prev\",").append(encode(obj(o, nodePrev), "L", pending)).append(']');
            b.append(']');
        }
    }

    static int id(Object o) {
        Integer existing = ids.get(o);
        if (existing != null) return existing;
        int next = ids.size() + 1;
        ids.put(o, next);
        return next;
    }

    static String encode(Object v, String desc, ArrayDeque<Object> pending) {
        if (v == null) return "null";
        switch (desc) {
            case "I": case "S": case "B": return String.valueOf(((Number) v).intValue());
            case "J": return longValue(((Number) v).longValue());
            case "Z": return String.valueOf(v);
            case "C": return "[\"CHAR\"," + json(String.valueOf(v)) + "]";
            case "F": case "D": return floatValue(((Number) v).doubleValue());
            default: break;
        }
        if (!boxAsObjects) {
            String inline = inlineValue(v);
            if (inline != null) return inline;
        }
        pending.add(v);
        return "[\"REF\"," + id(v) + "]";
    }

    /** Inline JSON for String and boxed primitives, or null for other objects. */
    static String inlineValue(Object v) {
        if (v instanceof String) return json((String) v);
        if (v instanceof Integer || v instanceof Short || v instanceof Byte) return String.valueOf(((Number) v).intValue());
        if (v instanceof Long) return longValue((Long) v);
        if (v instanceof Boolean) return String.valueOf(v);
        if (v instanceof Character) return "[\"CHAR\"," + json(String.valueOf(v)) + "]";
        if (v instanceof Float || v instanceof Double) return floatValue(((Number) v).doubleValue());
        return null;
    }

    static String longValue(long v) {
        return Math.abs(v) <= (1L << 53) ? String.valueOf(v) : "[\"LONG\",\"" + v + "\"]";
    }

    static String floatValue(double d) {
        if (Double.isNaN(d)) return "[\"SPECIAL_FLOAT\",\"NaN\"]";
        if (Double.isInfinite(d)) return "[\"SPECIAL_FLOAT\",\"" + (d > 0 ? "Infinity" : "-Infinity") + "\"]";
        return String.valueOf(d);
    }

    static void encodeObject(Object o, StringBuilder b, ArrayDeque<Object> pending) {
        Class<?> c = o.getClass();
        if (o instanceof String) { b.append("[\"STRING\",").append(json((String) o)).append(']'); return; }
        String boxed = inlineValue(o);
        if (boxed != null) { b.append("[\"BOXED\",").append(json(simpleName(c))).append(',').append(boxed).append(']'); return; }
        if (c.isArray()) {
            String elementDesc = descriptor(c.getComponentType());
            b.append("[\"ARRAY\",").append(json(Internals.isHashNodeArray(c) ? "HashMap.Node[]" : typeName(c)));
            int n = Array.getLength(o);
            for (int i = 0; i < n; i++) b.append(',').append(encode(Array.get(o, i), elementDesc, pending));
            b.append(']');
            return;
        }
        if (userClasses.contains(c.getName())) {
            b.append("[\"INSTANCE\",").append(json(simpleName(c)));
            if (o instanceof Enum) b.append(",[\"name\",").append(json(((Enum<?>) o).name())).append(']');
            ArrayList<Class<?>> chain = new ArrayList<>();
            for (Class<?> k = c; k != null && userClasses.contains(k.getName()); k = k.getSuperclass()) chain.add(0, k);
            Set<String> seen = new LinkedHashSet<>();
            for (Class<?> k : chain) for (Field f : k.getDeclaredFields()) {
                if (Modifier.isStatic(f.getModifiers()) || f.isSynthetic()) continue;
                String label = seen.add(f.getName()) ? f.getName() : simpleName(k) + "." + f.getName();
                Object value;
                try { f.setAccessible(true); value = f.get(o); } catch (Throwable e) { continue; }
                b.append(",[").append(json(label)).append(',').append(encode(value, descriptor(f.getType()), pending)).append(']');
            }
            if (o instanceof Throwable) b.append(",[\"message\",").append(json(((Throwable) o).getMessage())).append(']');
            b.append(']');
            return;
        }
        String name = c.getName();
        if (name.startsWith("java.util.") && o instanceof Map) {
            b.append("[\"MAP\",").append(json(simpleName(c))).append(",[");
            boolean firstEntry = true;
            try {
                for (Map.Entry<?, ?> e : ((Map<?, ?>) o).entrySet()) {
                    if (!firstEntry) b.append(','); firstEntry = false;
                    Object value = e.getValue();
                    b.append('[').append(encode(e.getKey(), "L", pending)).append(',')
                     .append(Internals.available && value != null && value == Internals.present ? "[\"PRESENT\"]" : encode(value, "L", pending)).append(']');
                }
            } catch (Throwable e) { /* keep what was read */ }
            b.append(']');
            String internals = Internals.describe(o, internalQueue);
            if (internals != null) b.append(',').append(internals);
            b.append(']');
            return;
        }
        if (name.startsWith("java.util.") && o instanceof Collection) {
            b.append("[\"COLLECTION\",").append(json(simpleName(c))).append(",[");
            boolean firstElement = true;
            try {
                for (Object e : (Collection<?>) o) { if (!firstElement) b.append(','); firstElement = false; b.append(encode(e, "L", pending)); }
            } catch (Throwable e) { /* partial */ }
            b.append(']');
            String internals = Internals.describe(o, internalQueue);
            if (internals != null) b.append(',').append(internals);
            b.append(']');
            return;
        }
        if (Internals.isNode(o)) {
            try { Internals.encodeNode(o, b, pending); return; } catch (Throwable e) { /* fall through to OPAQUE */ }
        }
        if (o instanceof Throwable) {
            b.append("[\"INSTANCE\",").append(json(simpleName(c))).append(",[\"message\",").append(json(((Throwable) o).getMessage())).append("]]");
            return;
        }
        if (name.contains("$$Lambda") || c.isSynthetic()) {
            Class<?>[] interfaces = c.getInterfaces();
            b.append("[\"OPAQUE\",").append(json("lambda" + (interfaces.length > 0 ? " " + simpleName(interfaces[0]) : ""))).append(']');
            return;
        }
        b.append("[\"OPAQUE\",").append(json(typeName(c))).append(']');
    }

    static String descriptor(Class<?> c) {
        if (c.isArray()) return c.getName().replace('.', '/');
        if (!c.isPrimitive()) return "L" + c.getName().replace('.', '/') + ";";
        if (c == int.class) return "I"; if (c == boolean.class) return "Z"; if (c == byte.class) return "B";
        if (c == char.class) return "C"; if (c == short.class) return "S"; if (c == long.class) return "J";
        if (c == float.class) return "F"; if (c == double.class) return "D"; return "V";
    }

    static String typeName(Class<?> c) {
        if (c.isArray()) return typeName(c.getComponentType()) + "[]";
        return simpleName(c);
    }

    static String simpleName(Class<?> c) {
        String s = c.getSimpleName();
        if (s.isEmpty()) { String n = c.getName(); s = n.substring(Math.max(n.lastIndexOf('.'), n.lastIndexOf('$')) + 1); }
        return s;
    }

    static String displayClass(String internal) {
        String s = internal.substring(internal.lastIndexOf('/') + 1);
        return s.substring(s.lastIndexOf('$') + 1);
    }

    public static String json(String s) {
        if (s == null) return "null";
        StringBuilder b = new StringBuilder(s.length() + 2).append('"');
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"': b.append("\\\""); break;
                case '\\': b.append("\\\\"); break;
                case '\n': b.append("\\n"); break;
                case '\r': b.append("\\r"); break;
                case '\t': b.append("\\t"); break;
                default: if (c < 32) b.append(String.format("\\u%04x", (int) c)); else b.append(c);
            }
        }
        return b.append('"').toString();
    }

    public static List<String> steps() { return steps; }
    public static boolean limitHit() { return limitHit; }
    public static boolean heapTruncated() { return heapTruncated; }
    public static long snapshotNs() { return snapshotNs; }
    public static int retainedObjects() { return ids.size(); }
    public static String stdoutText() { return stdout.toString(); }
}
