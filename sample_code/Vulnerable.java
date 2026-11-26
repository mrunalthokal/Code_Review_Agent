import java.sql.*;

public class Vulnerable {
    private static final String PASSWORD = "admin123";

    public ResultSet find(Connection c, String name) throws SQLException {
        Statement st = c.createStatement();
        return st.executeQuery("SELECT * FROM users WHERE name = '" + name + "'");
    }
}
