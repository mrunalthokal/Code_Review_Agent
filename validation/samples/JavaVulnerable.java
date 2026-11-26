import java.io.FileInputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.net.URL;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Random;
import javax.crypto.Cipher;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.xml.parsers.DocumentBuilderFactory;

public class VulnerableServlet {
    private static final String DB_PASSWORD = "Sup3rS3cret!";           // EXPECT: Hardcoded Secret
    private static final String AWS_ACCESS = "AKIAIOSFODNN7EXAMPLE";    // EXPECT: Exposed Cloud Key / Private Key

    public ResultSet findUser(Connection conn, HttpServletRequest req) throws Exception {
        String name = req.getParameter("name");
        Statement st = conn.createStatement();
        return st.executeQuery("SELECT * FROM users WHERE name = '" + name + "'");   // EXPECT: SQL Injection
    }

    public ResultSet report(Connection conn, String id) throws Exception {
        String sql = "SELECT * FROM reports "                       // EXPECT: SQL Injection
                + "WHERE owner = " + id;
        return conn.createStatement().executeQuery(sql);
    }

    public void greet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.getWriter().println("<h1>Hello " + req.getParameter("name") + "</h1>");   // EXPECT: Cross-Site Scripting (XSS)
    }

    public void run(HttpServletRequest req) throws IOException {
        Runtime.getRuntime().exec("ping " + req.getParameter("host"));   // EXPECT: OS Command Injection
    }

    public Object load(String path) throws Exception {
        ObjectInputStream in = new ObjectInputStream(new FileInputStream(path));   // EXPECT: Insecure Deserialization
        return in.readObject();
    }

    public FileInputStream open(HttpServletRequest req) throws IOException {
        return new FileInputStream(req.getParameter("file"));       // EXPECT: Path Traversal
    }

    public DocumentBuilderFactory xmlFactory() {
        return DocumentBuilderFactory.newInstance();                // EXPECT: XML External Entity (XXE)
    }

    public void safeRun(HttpServletRequest req) {
        try {
            run(req);
        } catch (IOException e) {
            e.printStackTrace();                                    // EXPECT: Information Exposure via Stack Trace
        }
    }

    public boolean login(String password) {
        return password.equals("letmein");                          // EXPECT: Insecure Authentication
    }

    public String role(HttpServletRequest req) {
        return req.getParameter("role");                            // EXPECT: Missing / Client-Controlled Access Check
    }

    @CrossOrigin(origins = "*")                                     // EXPECT: Permissive CORS
    public String open() {
        return "ok";
    }

    public URL fetch(HttpServletRequest req) throws Exception {
        return new URL(req.getParameter("url"));                    // EXPECT: Server-Side Request Forgery
    }

    public void configure(HttpSecurity http) throws Exception {
        http.csrf().disable();                                      // EXPECT: CSRF Protection Disabled
    }
}

class WeakCrypto {
    public String digest(String text) throws Exception {
        MessageDigest md = MessageDigest.getInstance("MD5");        // EXPECT: Weak Hash Algorithm
        return new String(md.digest(text.getBytes()));
    }

    public Cipher cipher() throws Exception {
        return Cipher.getInstance("DES/ECB/PKCS5Padding");          // EXPECT: Weak Cipher / ECB Mode
    }

    public int token() {
        return new Random().nextInt();                              // EXPECT: Insecure Randomness
    }
}
