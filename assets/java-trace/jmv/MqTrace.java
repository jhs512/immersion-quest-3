package jmv;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.FileObject;
import javax.tools.ForwardingJavaFileManager;
import javax.tools.JavaCompiler;
import javax.tools.JavaFileObject;
import javax.tools.SimpleJavaFileObject;
import javax.tools.StandardJavaFileManager;
import javax.tools.ToolProvider;

/**
 * MQ adapter around the java-memory-visualizer core (Instrumenter + Tracer, reused unchanged).
 * The core's own front end compiles with ECJ for Java 17 inside CheerpJ. MQ lessons are graded by the
 * real JDK 25 source launcher, so this adapter compiles the same Main.java with that JDK's own javac
 * (--release 25, debug info for local names), and starts main with the JDK 25 launch rules
 * (static or instance, with or without String[]), so the trace is of the code the grader runs.
 *
 * Usage: java -cp asm.jar;asm-tree.jar;classes jmv.MqTrace Main.java stdin.txt out.json stepBudget
 * Started by src/java_trace.rs. Nothing here grades: the lesson grader stays the only judge.
 */
public final class MqTrace {
    static final class Source extends SimpleJavaFileObject {
        final String text;
        Source(String name, String text) { super(URI.create("string:///" + name), Kind.SOURCE); this.text = text; }
        @Override public CharSequence getCharContent(boolean ignore) { return text; }
    }
    static final class Output extends SimpleJavaFileObject {
        final ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        Output(String name) { super(URI.create("bytes:///" + name.replace('.', '/') + ".class"), Kind.CLASS); }
        @Override public OutputStream openOutputStream() { return bytes; }
    }
    static final class MemoryLoader extends ClassLoader {
        final Map<String, byte[]> classes;
        MemoryLoader(Map<String, byte[]> classes) { super(MqTrace.class.getClassLoader()); this.classes = classes; }
        @Override protected Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException {
            if (!classes.containsKey(name)) return super.loadClass(name, resolve);
            synchronized (getClassLoadingLock(name)) {
                Class<?> c = findLoadedClass(name);
                if (c == null) { byte[] b = classes.get(name); c = defineClass(name, b, 0, b.length); }
                if (resolve) resolveClass(c);
                return c;
            }
        }
    }

    public static void main(String[] args) throws Exception {
        String source = Files.readString(Path.of(args[0]), StandardCharsets.UTF_8);
        String stdin = args.length > 1 && !args[1].equals("-") ? Files.readString(Path.of(args[1]), StandardCharsets.UTF_8) : "";
        int budget = args.length > 3 ? Integer.parseInt(args[3]) : 1000;
        String json = run(source, stdin, budget);
        Files.writeString(Path.of(args[2]), json, StandardCharsets.UTF_8);
    }

    static String run(String source, String stdin, int stepBudget) {
        StringBuilder out = new StringBuilder(4096);
        out.append("{\"code\":").append(Tracer.json(source)).append(",\"stdin\":").append(Tracer.json(stdin));
        out.append(",\"compiler\":").append(Tracer.json("javac " + Runtime.version() + " --release 25"));
        JavaCompiler javac = ToolProvider.getSystemJavaCompiler();
        if (javac == null) return out.append(",\"status\":\"internal_error\",\"message\":\"JDK compiler not found\",\"problems\":[],\"trace\":[]}").toString();
        DiagnosticCollector<JavaFileObject> diagnostics = new DiagnosticCollector<>();
        Map<String, Output> outputs = new LinkedHashMap<>();
        StandardJavaFileManager standard = javac.getStandardFileManager(diagnostics, Locale.KOREAN, StandardCharsets.UTF_8);
        ForwardingJavaFileManager<StandardJavaFileManager> manager = new ForwardingJavaFileManager<>(standard) {
            @Override public JavaFileObject getJavaFileForOutput(Location location, String name, JavaFileObject.Kind kind, FileObject sibling) {
                Output o = new Output(name); outputs.put(name, o); return o;
            }
        };
        List<String> options = List.of("--release", "25", "-g", "-proc:none", "-implicit:none", "-encoding", "UTF-8", "-Xlint:none");
        boolean ok = javac.getTask(null, manager, diagnostics, options, null, List.of(new Source("Main.java", source))).call();
        out.append(",\"problems\":[");
        boolean first = true;
        for (Diagnostic<? extends JavaFileObject> d : diagnostics.getDiagnostics()) {
            if (!first) out.append(','); first = false;
            out.append("{\"line\":").append(d.getLineNumber()).append(",\"error\":").append(d.getKind() == Diagnostic.Kind.ERROR)
               .append(",\"message\":").append(Tracer.json(d.getMessage(Locale.KOREAN))).append('}');
        }
        out.append(']');
        if (!ok) return out.append(",\"status\":\"compile_error\",\"trace\":[]}").toString();
        Map<String, byte[]> compiled = new LinkedHashMap<>();
        for (Map.Entry<String, Output> e : outputs.entrySet()) compiled.put(e.getKey(), e.getValue().bytes.toByteArray());

        Map<String, byte[]> transformed = new LinkedHashMap<>();
        try {
            Instrumenter instrumenter = new Instrumenter(compiled);
            for (Map.Entry<String, byte[]> e : compiled.entrySet()) transformed.put(e.getKey(), instrumenter.transform(e.getValue()));
        } catch (Throwable e) {
            return out.append(",\"status\":\"internal_error\",\"message\":").append(Tracer.json("instrumentation failure: " + e)).append(",\"trace\":[]}").toString();
        }
        MemoryLoader loader = new MemoryLoader(transformed);
        Method main; Class<?> mainClass;
        try {
            // The source launcher runs the first top-level class of Main.java.
            String launched = compiled.containsKey("Main") ? "Main" : compiled.keySet().stream().filter(n -> n.indexOf('$') < 0).findFirst().orElse(null);
            if (launched == null) return out.append(",\"status\":\"no_main\",\"message\":\"no class\",\"trace\":[]}").toString();
            mainClass = loader.loadClass(launched);
            main = findMain(mainClass);
        } catch (Throwable e) {
            return out.append(",\"status\":\"internal_error\",\"message\":").append(Tracer.json("class loading failure: " + e)).append(",\"trace\":[]}").toString();
        }
        if (main == null) return out.append(",\"status\":\"no_main\",\"message\":\"main method not found\",\"trace\":[]}").toString();

        // An instance main (compact source file) needs the launcher's own `new Main()`. It is created
        // before recording starts, so the learner's first step is the first line of main.
        Object target = null;
        if (!Modifier.isStatic(main.getModifiers())) {
            try {
                Constructor<?> ctor = mainClass.getDeclaredConstructor();
                ctor.setAccessible(true);
                target = ctor.newInstance();
            } catch (Throwable e) {
                return out.append(",\"status\":\"no_main\",\"message\":").append(Tracer.json("main needs a no-argument constructor: " + e)).append(",\"trace\":[]}").toString();
            }
        }
        Tracer.reset(compiled.keySet(), stepBudget, false);
        InputStream originalIn = System.in;
        System.setIn(new ByteArrayInputStream(stdin.getBytes(StandardCharsets.UTF_8)));
        Tracer.captureOutput();
        String status = "ok", message = null;
        try {
            main.setAccessible(true);
            if (main.getParameterCount() == 1) main.invoke(target, (Object) new String[0]); else main.invoke(target);
        } catch (InvocationTargetException e) {
            Throwable cause = e.getCause();
            if (cause instanceof Tracer.StepLimit) status = "step_limit";
            else { status = "uncaught_exception"; message = cause.toString(); }
        } catch (Throwable e) {
            status = "internal_error"; message = e.toString();
        } finally {
            Tracer.enabled = false;
            Tracer.restoreOutput();
            System.setIn(originalIn);
        }
        if (Tracer.limitHit()) status = "step_limit";
        out.append(",\"status\":").append(Tracer.json(status));
        if (message != null) out.append(",\"message\":").append(Tracer.json(message));
        out.append(",\"mainClass\":").append(Tracer.json(mainClass.getName()));
        out.append(",\"stepBudget\":").append(stepBudget).append(",\"heapTruncated\":").append(Tracer.heapTruncated());
        out.append(",\"stdout\":").append(Tracer.json(Tracer.stdoutText()));
        out.append(",\"trace\":[");
        boolean firstStep = true;
        for (String step : Tracer.steps()) { if (!firstStep) out.append(','); firstStep = false; out.append(step); }
        return out.append("]}").toString();
    }

    /** JDK 25 (JEP 512) launch protocol: main(String[]) before main(); static or instance; not private. */
    static Method findMain(Class<?> c) {
        for (Class<?>[] params : new Class<?>[][]{{String[].class}, {}}) {
            for (Class<?> k = c; k != null && k != Object.class; k = k.getSuperclass()) {
                try {
                    Method m = k.getDeclaredMethod("main", params);
                    if (!Modifier.isPrivate(m.getModifiers()) && m.getReturnType() == void.class) return m;
                } catch (NoSuchMethodException ignored) { }
            }
        }
        return null;
    }
}
