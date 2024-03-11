import static spark.Spark.*;
import java.io.*;

public class KITCat {
    // go to http://localhost:4567/hello
    public static void main(String[] args) {
        staticFileLocation("/static");
        get("/hello", (req, res) -> "Hello World");

        get("/VoiceRecorder", (req, res) -> {
            // Read the contents of the HTML file
            InputStream inputStream = KITCat.class.getClassLoader().getResourceAsStream("VoiceRecorder.html");
            if (inputStream != null) {
                // Return the contents of the HTML file
                res.type("text/html"); // Set content type to HTML
                return org.apache.commons.io.IOUtils.toString(inputStream, java.nio.charset.StandardCharsets.UTF_8);
            } else {
                // If the HTML file doesn't exist, return 404 Not Found
                res.status(404);
                return "HTML file not found";
            }
        });
    }
}
