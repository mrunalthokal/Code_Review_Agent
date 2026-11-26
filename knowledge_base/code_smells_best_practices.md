# Code Smells and Design Best Practices

## Long Method
A method longer than about 30 to 50 lines does too much. Refactor with Extract Method so each function has a single responsibility.

## Large Class (God Class)
A class with too many responsibilities and fields. Split by responsibility following the Single Responsibility Principle.

## High Cyclomatic Complexity
Deeply nested if/else and loops make code hard to test. A complexity above 10 per function should be refactored using guard clauses, polymorphism or lookup tables.

## Duplicated Code
Copy-pasted logic multiplies bugs. Apply the DRY principle by extracting shared functions or classes.

## Magic Numbers and Poor Naming
Replace unexplained literals with named constants. Use meaningful names: Python snake_case (PEP 8), Java camelCase and PascalCase classes.

## Long Parameter List
More than 4 or 5 parameters suggests grouping into an object or dataclass.

## Missing Error Handling
Bare except: or empty catch blocks hide failures. Catch specific exceptions and log them.

## Design Principles
SOLID: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion. Prefer composition over inheritance and keep modules loosely coupled.
