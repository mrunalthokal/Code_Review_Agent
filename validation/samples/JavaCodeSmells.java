import java.util.ArrayList;                                  // EXPECT: Unused import
import java.util.List;
import java.util.Map;                                        // EXPECT: Unused import

public class OrderProcessor {

    public List<Integer> none() {
        return null;
    }

    public int ProcessOrder(int a) {                         // EXPECT: Naming convention
        return a;
    }

    public int tooManyParams(int a, int b, int c, int d, int e, int f, int g) {   // EXPECT: Too Many Parameters
        return a + b + c + d + e + f + g;
    }

    public int complexLogic(int x) {                         // EXPECT: High Cyclomatic Complexity
        int r = 0;
        if (x > 1) { r += 1; }
        if (x > 2) { r += 1; }
        if (x > 3) { r += 1; }
        if (x > 4) { r += 1; }
        if (x > 5) { r += 1; }
        if (x > 6) { r += 1; }
        if (x > 7) { r += 1; }
        if (x > 8) { r += 1; }
        if (x > 9) { r += 1; }
        if (x > 10) { r += 1; }
        if (x > 11) { r += 1; }
        return r;
    }

    public int deepNesting(int x) {                          // EXPECT: Deep Nesting
        int r = 0;
        if (x > 0) {
            if (x > 1) {
                if (x > 2) {
                    if (x > 3) {
                        if (x > 4) {
                            r = x;
                        }
                    }
                }
            }
        }
        return r;
    }

    public void longMethod() {                               // EXPECT: Long Method
        int s01 = 1;
        int s02 = 2;
        int s03 = 3;
        int s04 = 4;
        int s05 = 5;
        int s06 = 6;
        int s07 = 7;
        int s08 = 8;
        int s09 = 9;
        int s10 = 10;
        int s11 = 11;
        int s12 = 12;
        int s13 = 13;
        int s14 = 14;
        int s15 = 15;
        int s16 = 16;
        int s17 = 17;
        int s18 = 18;
        int s19 = 19;
        int s20 = 20;
        int s21 = 21;
        int s22 = 22;
        int s23 = 23;
        int s24 = 24;
        int s25 = 25;
        int s26 = 26;
        int s27 = 27;
        int s28 = 28;
        int s29 = 29;
        int s30 = 30;
        int s31 = 31;
        int s32 = 32;
        int s33 = 33;
        int s34 = 34;
        int s35 = 35;
        int s36 = 36;
        int s37 = 37;
        int s38 = 38;
        int s39 = 39;
        int s40 = 40;
        int s41 = 41;
        int s42 = 42;
        int s43 = 43;
        int s44 = 44;
        int s45 = 45;
    }

    public void swallow() {
        try {
            Integer.parseInt("x");
        } catch (NumberFormatException e) {                   // EXPECT: Empty catch block
        }
    }

    public void broad() {
        try {
            Integer.parseInt("y");
        } catch (Exception e) {                               // EXPECT: Overly broad catch
            System.out.println("failed");
        }
    }
}

class Everything {                                           // EXPECT: Large Class (God Class)
    public int m01() { return 1; }
    public int m02() { return 2; }
    public int m03() { return 3; }
    public int m04() { return 4; }
    public int m05() { return 5; }
    public int m06() { return 6; }
    public int m07() { return 7; }
    public int m08() { return 8; }
    public int m09() { return 9; }
    public int m10() { return 10; }
    public int m11() { return 11; }
    public int m12() { return 12; }
    public int m13() { return 13; }
    public int m14() { return 14; }
    public int m15() { return 15; }
    public int m16() { return 16; }
}

class bad_name {                                             // EXPECT: Naming convention
    public int value() { return 1; }
}
