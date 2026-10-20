import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Base64;

// Private launcher transport, never inserted into a learner's source or folder.
// Windows' java.exe converts argv through the system ANSI code page, even when
// file.encoding is UTF-8. Pass ASCII only, then restore the real String[] here.
// Source mode deliberately calls JDK 25's own in-memory source launcher. This
// internal entry point is version-bound and covered by both source/class tests.
public class MqUtf8Arguments {
    public static void main(String[] transport) throws Throwable {
        String entry = transport[0];
        String[] arguments = Arrays.stream(transport).skip(1)
            .map(value -> new String(Base64.getUrlDecoder().decode(value), StandardCharsets.UTF_8))
            .toArray(String[]::new);
        Method main;
        if (entry.equals("Main.java")) {
            String[] sourceArguments = new String[arguments.length + 1];
            sourceArguments[0] = entry;
            System.arraycopy(arguments, 0, sourceArguments, 1, arguments.length);
            arguments = sourceArguments;
            main = Class.forName("com.sun.tools.javac.launcher.SourceLauncher")
                .getMethod("main", String[].class);
        } else if (entry.equals("Main")) {
            main = ClassLoader.getSystemClassLoader().loadClass(entry)
                .getDeclaredMethod("main", String[].class);
            main.setAccessible(true);
        } else {
            throw new IllegalArgumentException("Unsupported lesson entry point");
        }
        try {
            main.invoke(null, (Object) arguments);
        } catch (InvocationTargetException error) {
            throw error.getCause();
        }
    }
}
