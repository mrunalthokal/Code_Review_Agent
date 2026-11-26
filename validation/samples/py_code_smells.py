import json                                       # EXPECT: Unused import
import os
import sys                                        # EXPECT: Unused import
from collections import *                         # EXPECT: Wildcard import

# TODO: split this module into smaller pieces     # EXPECT: Unresolved TODO/FIXME
LONG_TEXT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."   # EXPECT: Overly long lines
total = 0


def update_total(value):
    global total                                  # EXPECT: Use of global state
    total += value
    return total


def process_order(order, customer, discount, tax, shipping, coupon, notes, gift):   # EXPECT: Too Many Parameters | High Cyclomatic Complexity | Deep Nesting
    """Deliberately tangled order logic."""
    result = 0
    if order:
        for item in order:
            if item > 0:
                if customer:
                    if discount and tax or shipping and coupon:
                        result += item
            elif item < -1 and gift or notes:
                result -= 1
    return result


def append_item(item, bucket=[]):                 # EXPECT: Mutable default argument
    bucket.append(item)
    return bucket


def read_text(path):
    try:
        return open(path).read()
    except:                                       # EXPECT: Bare except
        return None


def to_number(text):
    try:
        return int(text)
    except ValueError:                            # EXPECT: Swallowed exception
        pass


def current_dir():
    return os.getcwd()


def long_report(value):                           # EXPECT: Long Method | Missing docstring
    step_01 = value + 1
    step_02 = value + 2
    step_03 = value + 3
    step_04 = value + 4
    step_05 = value + 5
    step_06 = value + 6
    step_07 = value + 7
    step_08 = value + 8
    step_09 = value + 9
    step_10 = value + 10
    step_11 = value + 11
    step_12 = value + 12
    step_13 = value + 13
    step_14 = value + 14
    step_15 = value + 15
    step_16 = value + 16
    step_17 = value + 17
    step_18 = value + 18
    step_19 = value + 19
    step_20 = value + 20
    step_21 = value + 21
    step_22 = value + 22
    step_23 = value + 23
    step_24 = value + 24
    step_25 = value + 25
    step_26 = value + 26
    step_27 = value + 27
    step_28 = value + 28
    step_29 = value + 29
    step_30 = value + 30
    step_31 = value + 31
    step_32 = value + 32
    step_33 = value + 33
    step_34 = value + 34
    step_35 = value + 35
    step_36 = value + 36
    step_37 = value + 37
    step_38 = value + 38
    step_39 = value + 39
    step_40 = value + 40
    step_41 = value + 41
    step_42 = value + 42
    step_43 = value + 43
    step_44 = value + 44
    step_45 = value + 45
    return step_45


class Everything:                                 # EXPECT: Large Class (God Class)
    def m01(self): return 1
    def m02(self): return 2
    def m03(self): return 3
    def m04(self): return 4
    def m05(self): return 5
    def m06(self): return 6
    def m07(self): return 7
    def m08(self): return 8
    def m09(self): return 9
    def m10(self): return 10
    def m11(self): return 11
    def m12(self): return 12
    def m13(self): return 13
    def m14(self): return 14
    def m15(self): return 15
    def m16(self): return 16
