import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import javax.crypto.Cipher;

public class UserRepository {
    private final Connection conn;

    public UserRepository(Connection conn) {
        this.conn = conn;
    }

    public ResultSet findUser(String name) throws SQLException {
        PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE name = ?");
        ps.setString(1, name);
        return ps.executeQuery();
    }

    public byte[] randomBytes(int n) {
        byte[] out = new byte[n];
        new SecureRandom().nextBytes(out);
        return out;
    }

    public Cipher newCipher() throws Exception {
        return Cipher.getInstance("AES/GCM/NoPadding");
    }

    public String classify(int score) {
        if (score < 0) {
            return "invalid";
        }
        if (score < 50) {
            return "low";
        }
        return "high";
    }
}
