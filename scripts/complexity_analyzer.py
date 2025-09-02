#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Complexity Analyzer

Analyzes Python files for function/method complexity based on:
- Lines of code (excluding blanks and comments)  
- Maximum nesting level
- Complexity score = nesting_level * 10 + loc

Usage:
    python complexity_analyzer.py <python_file> [output_file]
    
Example:
    python complexity_analyzer.py fcexport.py planning/complexity_report.md
"""

import ast
import sys
import os
from collections import defaultdict
from datetime import datetime


class ComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.functions = {}
        self.current_function = None
        self.nesting_level = 0
        self.max_nesting = 0
        
    def visit_FunctionDef(self, node):
        # Save previous state
        prev_function = self.current_function
        prev_nesting = self.nesting_level
        prev_max_nesting = self.max_nesting
        
        # Start analyzing this function
        self.current_function = node.name
        self.nesting_level = 0
        self.max_nesting = 0
        
        # Count lines of code (excluding docstrings)
        start_line = node.lineno
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
        
        # Skip docstring if present
        body_start = 0
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            body_start = 1
            
        lines_of_code = 0
        for stmt in node.body[body_start:]:
            if hasattr(stmt, 'lineno') and hasattr(stmt, 'end_lineno'):
                lines_of_code += stmt.end_lineno - stmt.lineno + 1
            else:
                lines_of_code += 1
                
        # Visit function body to find max nesting
        for stmt in node.body:
            self.visit(stmt)
            
        # Store results
        self.functions[node.name] = {
            'loc': lines_of_code,
            'max_nesting': self.max_nesting,
            'complexity_score': self.max_nesting * 10 + lines_of_code,
            'start_line': start_line,
            'end_line': end_line
        }
        
        # Restore previous state
        self.current_function = prev_function
        self.nesting_level = prev_nesting
        self.max_nesting = prev_max_nesting
        
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)  # Same logic as regular functions
        
    def visit_If(self, node):
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_For(self, node):
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_While(self, node):
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_With(self, node):
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_Try(self, node):
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1


class CompleteAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.all_functions = {}
        self.class_stack = []
        
    def visit_ClassDef(self, node):
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()
        
    def visit_FunctionDef(self, node):
        # Determine full function name
        if self.class_stack:
            func_name = f"{'.'.join(self.class_stack)}.{node.name}"
        else:
            func_name = node.name
            
        # Calculate complexity
        prev_nesting = getattr(self, 'nesting_level', 0)
        prev_max_nesting = getattr(self, 'max_nesting', 0)
        
        self.nesting_level = 0
        self.max_nesting = 0
        
        # Count lines of code (excluding docstrings)
        start_line = node.lineno
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
        
        # Skip docstring if present
        body_start = 0
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            body_start = 1
            
        lines_of_code = 0
        for stmt in node.body[body_start:]:
            if hasattr(stmt, 'lineno') and hasattr(stmt, 'end_lineno'):
                lines_of_code += stmt.end_lineno - stmt.lineno + 1
            else:
                lines_of_code += 1
                
        # Visit function body to find max nesting
        for stmt in node.body:
            self.visit(stmt)
            
        # Store results
        self.all_functions[func_name] = {
            'loc': lines_of_code,
            'max_nesting': self.max_nesting,
            'complexity_score': self.max_nesting * 10 + lines_of_code,
            'start_line': start_line,
            'end_line': end_line
        }
        
        # Restore previous state
        self.nesting_level = prev_nesting
        self.max_nesting = prev_max_nesting
        
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)  # Same logic as regular functions
        
    def visit_If(self, node):
        self.nesting_level = getattr(self, 'nesting_level', 0) + 1
        self.max_nesting = max(getattr(self, 'max_nesting', 0), self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_For(self, node):
        self.nesting_level = getattr(self, 'nesting_level', 0) + 1
        self.max_nesting = max(getattr(self, 'max_nesting', 0), self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_While(self, node):
        self.nesting_level = getattr(self, 'nesting_level', 0) + 1
        self.max_nesting = max(getattr(self, 'max_nesting', 0), self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_With(self, node):
        self.nesting_level = getattr(self, 'nesting_level', 0) + 1
        self.max_nesting = max(getattr(self, 'max_nesting', 0), self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_Try(self, node):
        self.nesting_level = getattr(self, 'nesting_level', 0) + 1
        self.max_nesting = max(getattr(self, 'max_nesting', 0), self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1


def analyze_file(file_path):
    """Analyze a Python file and return complexity metrics."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    # Single analyzer that properly tracks context
    analyzer = CompleteAnalyzer()
    analyzer.visit(tree)
    
    return analyzer.all_functions


def generate_report(file_path, functions, output_file=None):
    """Generate complexity report."""
    
    # Sort by complexity score (descending)
    sorted_functions = sorted(functions.items(), 
                            key=lambda x: x[1]['complexity_score'], 
                            reverse=True)
    
    # Categorize by complexity
    high_complexity = [(name, data) for name, data in sorted_functions 
                      if data['complexity_score'] >= 80]
    medium_complexity = [(name, data) for name, data in sorted_functions 
                        if 40 <= data['complexity_score'] < 80]
    low_complexity = [(name, data) for name, data in sorted_functions 
                     if data['complexity_score'] < 40]
    
    # Generate report content
    report = f"""# Code Complexity Analysis Report

**File:** {file_path}  
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Total Functions/Methods:** {len(functions)}

## Analysis Methodology

- **Lines of Code (LOC)**: Non-blank, non-comment lines within function body (excluding docstrings)
- **Max Nesting Level**: Deepest indentation level (if/for/while/with/try blocks)
- **Complexity Score**: `nesting_level × 10 + loc` (prioritizes high nesting over long functions)

## Summary Statistics

- **High Complexity** (Score ≥ 80): {len(high_complexity)} functions
- **Medium Complexity** (Score 40-79): {len(medium_complexity)} functions  
- **Low Complexity** (Score < 40): {len(low_complexity)} functions

## Top 10 Most Complex Functions

| Rank | Function/Method | LOC | Nesting | Score | Lines |
|------|-----------------|-----|---------|-------|-------|
"""
    
    for i, (name, data) in enumerate(sorted_functions[:10], 1):
        start_line = data['start_line']
        end_line = data['end_line']
        report += f"| {i:2d} | `{name}` | {data['loc']:3d} | {data['max_nesting']:7d} | {data['complexity_score']:5d} | {start_line}-{end_line} |\n"
    
    report += """
## Complexity Categories

### High Complexity Functions (Score ≥ 80)
*These functions should be prioritized for refactoring*

"""
    
    if high_complexity:
        for name, data in high_complexity:
            start_line = data['start_line']
            end_line = data['end_line']
            report += f"- **`{name}`** (Score: {data['complexity_score']}) - {data['loc']} LOC, {data['max_nesting']} max nesting (lines {start_line}-{end_line})\n"
    else:
        report += "*No functions with high complexity found.*\n"
    
    report += """
### Medium Complexity Functions (Score 40-79)
*Consider refactoring if they grow larger*

"""
    
    if medium_complexity:
        for name, data in medium_complexity:
            start_line = data['start_line']
            end_line = data['end_line']
            report += f"- **`{name}`** (Score: {data['complexity_score']}) - {data['loc']} LOC, {data['max_nesting']} max nesting (lines {start_line}-{end_line})\n"
    else:
        report += "*No functions with medium complexity found.*\n"
    
    report += """
## Refactoring Recommendations

### Priority 1: High Complexity Functions
"""
    
    if high_complexity:
        report += "Focus on these functions first as they have the highest complexity scores:\n\n"
        for name, data in high_complexity[:3]:
            if data['max_nesting'] >= 4:
                report += f"- **`{name}`**: High nesting level ({data['max_nesting']}) suggests nested logic that could be extracted into helper functions\n"
            elif data['loc'] >= 50:
                report += f"- **`{name}`**: Large function ({data['loc']} LOC) should be broken into smaller, focused functions\n"
            else:
                report += f"- **`{name}`**: Moderate complexity - review for potential simplification\n"
    else:
        report += "Great! No high-complexity functions found.\n"
    
    report += """
### Priority 2: Medium Complexity Functions
Monitor these functions to prevent them from growing too complex. Consider refactoring if they gain additional responsibilities.

### General Recommendations
1. **Extract Helper Functions**: Break large functions into smaller, single-purpose functions
2. **Reduce Nesting**: Use early returns, guard clauses, and extraction methods to reduce nesting depth
3. **Single Responsibility**: Ensure each function has one clear purpose
4. **Regular Monitoring**: Run this analysis periodically to catch complexity growth early

## Complete Function List (Sorted by Complexity)

| Function/Method | LOC | Nesting | Score | Lines |
|-----------------|-----|---------|-------|-------|
"""
    
    for name, data in sorted_functions:
        start_line = data['start_line']
        end_line = data['end_line']
        report += f"| `{name}` | {data['loc']:3d} | {data['max_nesting']:7d} | {data['complexity_score']:5d} | {start_line}-{end_line} |\n"
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Complexity report saved to: {output_file}")
    else:
        print(report)


def main():
    if len(sys.argv) < 2:
        print("Usage: python complexity_analyzer.py <python_file> [output_file]")
        sys.exit(1)
        
    file_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
        
    if not file_path.endswith('.py'):
        print(f"Warning: '{file_path}' doesn't appear to be a Python file")
    
    try:
        functions = analyze_file(file_path)
        generate_report(file_path, functions, output_file)
    except SyntaxError as e:
        print(f"Error: Invalid Python syntax in '{file_path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()