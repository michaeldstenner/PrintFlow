# FreeCAD Macro Community Submission Guidelines

This document consolidates the requirements and best practices for submitting macros to the FreeCAD community, based on the official guidelines from:
- [FreeCAD-macros repository README](https://github.com/FreeCAD/FreeCAD-macros/blob/master/README.md)
- [FreeCAD Wiki Macro Documentation](https://wiki.freecad.org/Macro_documentation)

## Submission Process Overview

1. **Development & Testing** - Complete macro functionality and testing
2. **Forum Review** - Post in "FreeCAD Python Scripting and Macros subforum" for community feedback
3. **Repository Submission** - After approval, submit to FreeCAD-macros repository via pull request
4. **Wiki Documentation** - Create comprehensive wiki page

## Required Macro Metadata Header

Add this metadata block after the macro description in Python comments:

```python
"""
Macro description here...
"""

__Name__ = "MacroDisplayName"
__Comment__ = "Brief description of what the macro does"
__Author__ = "Author Name, Co-Author Name"  # Comma-separated
__Version__ = "1.0.0"  # Semantic versioning (major.minor.patch)
__Date__ = "2024-MM-DD"  # Last update date (YYYY-MM-DD)
__License__ = "MIT"  # SPDX license identifier (MIT, GPL-3.0, etc.)
__Wiki__ = "https://wiki.freecad.org/Macro_MacroName"  # Future wiki page URL
__Icon__ = "path/to/icon.svg"  # Path or URL to icon
__Status__ = "Stable"  # "Stable", "Alpha", or "Beta"
```

## File Naming Conventions

### Macro Filename
- Format: `CamelCase.FCMacro`
- Start with object type it works on (e.g., `Assembly`, `Part`, `Mesh`)
- Avoid prefixes like "Macro" or "FC"
- Be descriptive and clear
- Examples: `AssemblyExport.FCMacro`, `PartArrayPattern.FCMacro`

### Wiki Page Name
- Format: `Macro_MacroName` (matches the `__Name__` field)
- Example: `Macro_AssemblyExport`

## Required Documentation

### 1. In-Code Documentation
- Comprehensive description as Python comments at the top
- Explain what the macro does, inputs/outputs, and major options
- Include usage examples where helpful

### 2. Wiki Page Sections
Use the `[Template:Macro]` at the top, then include:

#### Essential Sections:
- **Description** - What the macro does, why it's useful
- **Usage** - Step-by-step instructions
- **Options** - Available settings and their effects
- **Limitations** - Known restrictions or requirements
- **Script** - The actual macro code using `[Template:MacroCode]`

#### Recommended Additions:
- **Examples** - Screenshots or diagrams showing usage
- **Related** - Links to similar macros or workbenches
- **Version History** - Changelog for major updates

### 3. Visual Elements
- **Icon** - SVG preferred, PNG acceptable
- **Screenshots** - Show macro in action
- **Animated GIF** - Max 500x500 pixels for complex operations

## Code Quality Standards

### Pre-commit Hooks
Set up automated code checks:
```bash
pre-commit run --all-files
```

### Code Style
- Follow Python best practices
- Use clear variable names
- Include error handling
- Add type hints where beneficial

### Comments
- Explain complex logic
- Document property systems
- Include usage examples in docstrings

## Submission Checklist

### High Priority (Required)
- [ ] Macro functionality complete and tested
- [ ] All required metadata fields added
- [ ] File renamed to CamelCase.FCMacro format
- [ ] Comprehensive in-code documentation
- [ ] Basic usage instructions

### Medium Priority (Recommended) 
- [ ] Wiki page created with Template:Macro
- [ ] Icon designed (SVG/PNG)
- [ ] Screenshots or examples added
- [ ] Changelog documented
- [ ] Pre-commit hooks configured

### Submission Process
- [ ] Posted in FreeCAD forum for review
- [ ] Addressed community feedback
- [ ] Forked FreeCAD-macros repository
- [ ] Created feature branch
- [ ] Submitted pull request
- [ ] Wiki page published

## Template Checklist for Specific Macro

When preparing a specific macro for submission, copy this checklist:

**Macro Name**: ________________
**Target Filename**: ________________.FCMacro

### Metadata Preparation
- [ ] `__Name__`: ________________
- [ ] `__Comment__`: ________________
- [ ] `__Author__`: ________________
- [ ] `__Version__`: ________________
- [ ] `__Date__`: ________________
- [ ] `__License__`: ________________
- [ ] `__Wiki__`: ________________
- [ ] `__Icon__`: ________________
- [ ] `__Status__`: ________________

### Documentation Tasks
- [ ] Description explains purpose and functionality
- [ ] Usage instructions with step-by-step guide
- [ ] Options and settings documented
- [ ] Limitations and requirements listed
- [ ] Examples or screenshots prepared
- [ ] Icon created (SVG preferred)

### Code Quality
- [ ] Code follows Python best practices
- [ ] Error handling implemented
- [ ] Comments explain complex logic
- [ ] Pre-commit checks passing

### Testing Verification
- [ ] Functionality tested thoroughly
- [ ] Works with target FreeCAD version
- [ ] Edge cases handled gracefully
- [ ] No breaking errors in normal usage

## Common Gotchas

1. **Naming**: Don't use "Macro" or "FC" prefixes in filename
2. **Wiki**: Create wiki page AFTER forum approval, not before
3. **Icon**: SVG format preferred over PNG for scalability
4. **Version**: Use semantic versioning (1.0.0, not 1.0 or v1)
5. **License**: Use SPDX identifiers, not full license text
6. **Code**: Preserve whitespace in wiki code blocks using Template:MacroCode

## Community Notes

- FreeCAD community is generally welcoming and helpful
- They value functionality and good documentation over perfect formatting
- Post in forum first - this is where you'll get the most useful feedback
- Be responsive to community suggestions during review process
- Consider maintaining your macro long-term for bug fixes and updates

## Resources

- [FreeCAD-macros GitHub Repository](https://github.com/FreeCAD/FreeCAD-macros)
- [FreeCAD Forum - Python Scripting and Macros](https://forum.freecad.org/viewforum.php?f=22)
- [FreeCAD Wiki Macro Documentation](https://wiki.freecad.org/Macro_documentation)
- [Template:Macro Documentation](https://wiki.freecad.org/Template:Macro)
- [SPDX License List](https://spdx.org/licenses/)