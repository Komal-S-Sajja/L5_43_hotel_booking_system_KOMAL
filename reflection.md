# Lab 5: Static Code Analysis — Reflection

**Student:** Komal S Sajja  
**Repository:** `L5_43_hotel_booking_system_KOMAL`  
**Course:** Software Engineering Lab, PES University  

---

### Question 1: What was learned about the role and purpose of static code analysis in software development?

Static code analysis is the practice of evaluating source code without executing it, examining code structure, syntax trees, patterns, and data flows to identify defects, security vulnerabilities, design flaws, and style violations early in the software development lifecycle (SDLC).

Through this lab, several key principles were reinforced:
- **Early Defect Detection ("Shift-Left"):** Static analysis catches defects before code ever reaches deployment, testing environments, or production. Subtle issues such as mutable default arguments (`booking_log=[]`) can silently corrupt state over time, but static analysis tools flag them immediately during compilation or linting.
- **Automated Standard Enforcement:** Maintaining consistent code style and idiomatic Python practices manually across large teams is error-prone. Automated linters provide immediate, objective feedback, preventing bikeshedding in code reviews and establishing clear quality baselines.
- **Security Awareness:** Developers often write code that works under ideal conditions but fails securely under adversarial conditions. Static analysis tools specifically scan for insecure functions (`eval()`, `os.system()`, weak hashes) that developer intuition might overlook as functional prototypes.
- **Maintainability and Technical Debt Reduction:** Flagging unused imports, dead variables, missing resource managers (`with` blocks), and undocumented interfaces prevents gradual codebase degradation and technical debt accumulation.

---

### Question 2: Which issues identified by the static analysis tools were the most significant, and how were they resolved?

The most critical issues identified were security vulnerabilities and subtle logic bugs that compromised application safety and data integrity:

1. **Arbitrary Code Execution via `eval()` (Bandit B307 / CWE-78):**
   - *Problem:* In `compute_seasonal_rate(room_num, rate_expr)`, `eval(rate_expr)` was used to evaluate dynamic pricing formulas. This gave untrusted inputs direct access to Python's execution environment. An attacker could pass payload expressions like `__import__('os').system('rm -rf /')` or read unauthorized files.
   - *Resolution:* Removed `eval()` entirely. Replaced it with Python's Abstract Syntax Tree (`ast`) module to inspect and parse mathematical expressions. The AST validator strictly restricts nodes to safe binary arithmetic operators (`ast.Mult`, `ast.Add`, `ast.Sub`) and authorized identifiers (`base_price`), rejecting any function calls, attribute access, or unauthorized statements. Direct numeric multipliers are also supported.

2. **Shell Command Injection via `os.system()` (Bandit B605 / CWE-78):**
   - *Problem:* `export_room_ledger()` constructed shell commands via string concatenation: `os.system("echo Hotel ledger exported to: " + filename)`. If a malicious filename was provided (e.g., `test.txt; rm -rf /`), it would execute arbitrary OS commands within the system shell. Spawning an entire subshell process for console logging was also an architectural flaw.
   - *Resolution:* Eliminated `os.system()` completely. The logging statement was replaced with Python's built-in `print(f"Hotel ledger exported to: {filename}")`, executing safely within the Python runtime without shell invocation.

3. **Weak Cryptographic Hash for Guest Identifiers (Bandit B324 / CWE-327):**
   - *Problem:* `generate_guest_hash()` used MD5 (`hashlib.md5`), which is cryptographically broken and prone to collision attacks. In guest identification systems, weak hashing can lead to identity spoofing or credential collision.
   - *Resolution:* Migrated the hashing function to SHA-256 (`hashlib.sha256`) with explicit UTF-8 string encoding, ensuring strong preimage and collision resistance.

4. **Dangerous Mutable Default Argument (Pylint W0102):**
   - *Problem:* `bookRoom(room_num, guest_name, booking_log=[])` used a mutable list as the default value. In Python, default parameter objects are evaluated only once at definition time. Consequently, successive function calls that did not provide a `booking_log` shared the identical list instance in memory, causing booking records from distinct guests to leak into subsequent bookings.
   - *Resolution:* Replaced the default parameter with `booking_log=None` and instantiated a fresh list inside the function body (`if booking_log is None: booking_log = []`).

5. **Hard-coded Secret Token in Source Code (Bandit B105):**
   - *Problem:* `main()` hard-coded `hotel_secret_key = "HOTEL_ADMIN_RESERVATION_TOKEN_2026"` and printed it to stdout. Hardcoding credentials in source code exposes tokens in version control repositories, and printing them leaks credentials into system logs.
   - *Resolution:* Removed the hard-coded string literal. The program now retrieves the secret key from the environment (`os.environ.get("HOTEL_SECRET_KEY")`) and reports its configuration status without printing sensitive token values.

---

### Question 3: How do the three tools (Pylint, Bandit, and Flake8) complement one another?

Each tool operates from a distinct perspective, and using them together provides multi-layered coverage that no single tool can achieve independently:

| Tool | Primary Focus | Strengths in This Lab |
|---|---|---|
| **Pylint** | Code Quality, Logic, and Design Standards | Caught semantic logic bugs (mutable default argument `W0102`), unhandled or broad exceptions (`W0702`), unclosed file handles (`R1732`), missing encodings (`W1514`), unnecessary branch structures (`R1705`), and missing docstrings (`C0116`). Provides a quantitative score (initially 5.32/10, improved to >9.5/10). |
| **Bandit** | Security Vulnerabilities & Insecure Patterns | Analyzed the AST specifically for Common Weakness Enumerations (CWEs): flagged arbitrary code execution via `eval` (B307), shell injection via `os.system` (B605), cryptographically weak MD5 hashing (B324), hard-coded passwords (B105), and insecure random number generation (B311). |
| **Flake8** | PEP 8 Style, Syntax, and Fast Linting | Enforced strict style rules: line length limits (`E501`), unused imports (`F401`), unused local variables (`F841`), singleton comparisons (`E711`), and missing end-of-file newlines (`W292`). Runs quickly and ensures code readability and formatting uniformity. |

**Synergy:**
- Flake8 enforces consistency and readability at the syntax/formatting level.
- Pylint dives deeper into semantic structure, object models, and programming best practices.
- Bandit examines the code through an adversarial security lens, identifying attack vectors and insecure API calls that general linters might overlook.

Together, they form a comprehensive static validation pipeline.

---

### Question 4: What are the limitations of static code analysis, and why is manual and dynamic testing still essential?

While static code analysis is powerful, it has fundamental theoretical and practical limitations:

1. **Inability to Detect Business Logic Flaws:**
   Static analysis tools inspect syntax and known patterns; they have no semantic understanding of business rules. For instance, if `cancel_booking()` set `is_booked = True` instead of `False`, static analysis tools would report zero errors because the assignment is syntactically valid and type-consistent. Only unit tests and functional verification can catch business logic inversions.

2. **False Positives and False Negatives:**
   - *False Positives:* Linters frequently flag benign constructs (such as flagging pseudo-random numbers in non-cryptographic games, or flagging `eval` in controlled mathematical DSLs).
   - *False Negatives:* Complex data flows across multiple functions or dynamic inputs can evade AST pattern matching. If unsafe strings flow into external libraries via dynamic dispatch, static tools often fail to trace the vulnerability.

3. **Runtime Environment Independence:**
   Static analysis does not test behavior under concurrent load, network latency, database timeouts, operating system differences, or memory exhaustion. A script can score 10.00/10 on Pylint but still crash at runtime due to missing OS permissions or unhandled network drops.

4. **Value of Dynamic and Manual Testing:**
   - **Dynamic Testing (Unit & Integration Tests):** Executes code with diverse inputs, asserting actual outputs against expected behaviors across boundary conditions.
   - **Manual Code Review:** Evaluates code clarity, maintainability, architectural fit, and whether the code actually solves the user's requirements cleanly.

**Conclusion:** Static analysis serves as an indispensable first line of automated defense, but it must be coupled with rigorous dynamic testing and human review to ensure truly reliable, secure software.
