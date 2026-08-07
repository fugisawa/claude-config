---
description: Explain how a specific code file or function works
argument-hint: <file path or function name>
allowed-tools: Read, Grep, Task
model: opus
---

# Explain Code

Provide a detailed explanation of the following code:

$ARGUMENTS

Instructions:
1. If it's a file path, read the entire file
2. If it's a function/class name, search for its definition
3. Analyze the code structure and logic
4. Explain:
   - Purpose and functionality
   - Key algorithms or patterns used
   - Dependencies and interactions
   - Potential improvements or issues
5. Provide examples of usage if applicable