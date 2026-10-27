# Lab 5: Static Code Analysis — Reflection

**Student:** Komal S Sajja  
**Repository:** `L5_43_hotel_booking_system_KOMAL`  
**SRN:** PES1UG24CS231

---

### Question 1: What was learned about the role and purpose of static code analysis in software development?

From this lab, I learned that static code analysis helps us find problems in our code without actually running the program. It can identify coding mistakes, security risks and formatting issues early, which makes the code easier to maintain and less likely to cause problems later.

While working on the hotel booking system, I understood that code can run successfully and still contain serious issues. For example, using `eval()` can be dangerous because it can execute expressions that we did not intend to allow. Similarly, using a list as a default function argument can cause unexpected behaviour when the function is called multiple times.

I also learned that different tools help us look at code from different perspectives. Instead of checking everything manually, we can use automated tools to find common problems and then decide how to fix them. This saves time and helps us develop better coding habits.

### Question 2: Which issues identified by the static analysis tools were the most significant, and how were they resolved?

The most important issues I found were related to security and incorrect coding practices.

1. **Unsafe use of `eval()`:** The original program used `eval()` to calculate seasonal room prices. This was risky because an expression supplied as input could potentially execute unwanted Python code. I replaced it with a safer approach using Python's `ast` module, which allows only the arithmetic operations and expressions needed for calculating the price.

2. **Use of `os.system()`:** The original program used `os.system()` to display a message after exporting the room ledger. Constructing shell commands using strings can be dangerous if the input contains unexpected characters. I removed the shell command and used Python's `print()` function instead.

3. **Weak MD5 hashing:** The program originally used MD5 to generate a hash for a guest identifier. I changed it to SHA-256, which is a stronger hashing algorithm. This is a better choice when we need a hash that is resistant to collisions.

4. **Mutable default argument:** The booking function originally used `booking_log=[]` as its default argument. Since Python creates this list only once, multiple calls can share the same list unintentionally. I changed the default to `None` and initialise the list inside the function when needed.

5. **Hard-coded secret:** The original code contained a secret token directly in the source code and printed it. Keeping secrets in source code is unsafe, especially when the code is uploaded to GitHub. I changed the program to read the secret from an environment variable and display only whether it is configured, without revealing its value.

These changes helped me understand why it is important to look beyond whether a program produces the expected output. The way the code is written also affects its security, reliability and maintainability.

### Question 3: How do the three tools (Pylint, Bandit, and Flake8) complement one another?

I learned that Pylint, Bandit and Flake8 serve different purposes, so using all three gives us a more complete picture of the quality of our code.

- **Pylint** checks general code quality and programming practices. It helped identify issues such as the mutable default argument, unused variables, exception handling and missing documentation. It also gives a score that helps us measure improvements in code quality.
- **Bandit** focuses on security-related problems. In this lab, it helped identify risky practices such as using `eval()`, executing shell commands, using MD5 and keeping a secret directly in the source code.
- **Flake8** checks code style and formatting. It identifies problems such as unused imports, overly long lines, incorrect spacing and other violations of Python's style guidelines.

These tools complement one another because a program might have clean formatting but still contain a security vulnerability. Similarly, a program could have no obvious security warnings but still have logic problems or poor coding practices.

After making the changes, I reran the tools to check the results. Pylint reported a score of 10/10, Bandit reported no issues, and the Flake8 after-report was empty. This showed me how static analysis can be used not only to find problems but also to verify that the changes have improved the code.

### Question 4: What are the limitations of static code analysis, and why is manual and dynamic testing still essential?

Although static analysis is useful, I learned that it cannot guarantee that a program is completely correct or secure. These tools look for known patterns and potential problems, but they do not always understand what the program is supposed to do.

For example, a program might pass all three static analysis tools but still calculate an incorrect room price or allow a booking to be cancelled when it should not be. Such problems depend on the expected behaviour of the application and may not be detected by a linter.

Static analysis can also produce false positives, where a tool reports something that is not actually a problem, and false negatives, where a real problem is missed. It also cannot fully replace testing the program under different inputs and runtime conditions.

This is why dynamic testing and manual review are still important. Running the program helps us check its actual behaviour, while testing different inputs helps us identify unexpected results and edge cases. Manual review helps us decide whether the code makes sense and meets the requirements.

Overall, this lab taught me that static analysis is an important part of software development, but it should be combined with testing and human review. A good result from an analysis tool is useful evidence of code quality, not a guarantee that the program has no remaining problems.
