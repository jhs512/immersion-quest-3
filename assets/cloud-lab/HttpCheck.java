import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

// The grader's own HTTP probe, run inside the owned client guest. Exit 0 = HTTP 200,
// 2 = other status, 3 = could not connect or read.
public class HttpCheck {
    public static void main(String[] args) {
        String host = args[0];
        int port = Integer.parseInt(args[1]);
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress(host, port), 3000);
            socket.setSoTimeout(5000);
            OutputStream out = socket.getOutputStream();
            out.write(("GET / HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\n\r\n")
                    .getBytes(StandardCharsets.US_ASCII));
            out.flush();
            InputStream in = socket.getInputStream();
            ByteArrayOutputStream all = new ByteArrayOutputStream();
            in.transferTo(all);
            String response = all.toString(StandardCharsets.UTF_8);
            System.out.println("from=" + socket.getLocalAddress().getHostAddress());
            System.out.print(response);
            System.exit(response.startsWith("HTTP/1.1 200 ") ? 0 : 2);
        } catch (Exception e) {
            System.out.println("CONNECT_FAIL " + e);
            System.exit(3);
        }
    }
}
