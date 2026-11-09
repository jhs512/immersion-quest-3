import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

// Long-running HTTP server for the preflight guest. It uses the same ServerSocket idea as
// the network-http lesson, but it is a separate program: it loops forever and answers
// every request, while the lesson exercises open one socket inside a single test.
public class HelloServer {
    public static void main(String[] args) throws Exception {
        int port = Integer.parseInt(args[0]);
        // Floci puts the EC2 instance ID into the guest container environment.
        String instance = System.getenv().getOrDefault("AWS_EC2_INSTANCE_ID", "unknown");
        try (ServerSocket listener = new ServerSocket(port, 50, InetAddress.getByName("0.0.0.0"))) {
            System.out.println("listening on " + port + " as " + instance);
            while (true) {
                try (Socket client = listener.accept()) {
                    client.setSoTimeout(5000);
                    BufferedReader in = new BufferedReader(
                            new InputStreamReader(client.getInputStream(), StandardCharsets.US_ASCII));
                    String requestLine = in.readLine();
                    String header;
                    while ((header = in.readLine()) != null && !header.isEmpty()) {
                        // Skip headers until the blank line that ends the request head.
                    }
                    String body = "instance=" + instance + "\n"
                            + "served-on=" + client.getLocalAddress().getHostAddress() + "\n"
                            + "java.version=" + System.getProperty("java.version") + "\n"
                            + "request=" + requestLine + "\n";
                    byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
                    OutputStream out = client.getOutputStream();
                    out.write(("HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\n"
                            + "Content-Length: " + bytes.length + "\r\nConnection: close\r\n\r\n")
                            .getBytes(StandardCharsets.US_ASCII));
                    out.write(bytes);
                    out.flush();
                } catch (IOException e) {
                    System.err.println("request failed: " + e);
                }
            }
        }
    }
}
