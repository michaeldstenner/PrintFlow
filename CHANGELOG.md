# Changelog

All notable changes to PrintFlow will be documented in this file.

## [1.1.0] - 2025-09-03

### Added
- AI-enhanced release process with Claude Code integration
- Automated version and date management via bump-my-version
- New `just` targets for AI-assisted development workflow
- Enhanced grip integration for comfortable markdown viewing
- Smart test runner with improved monitoring and timeout handling

### Fixed
- Circular reference detection in Link processing for FreeCAD 1.1.Weekly compatibility
- Infinite recursion in `_create_linked_subtree` method
- Container export logic for multi-volume 3MF files
- Inappropriate TreeView recursion protection during Link processing

### Changed
- Enhanced test suite with better selection and monitoring
- Improved debug logging and error reporting
- Code quality tools with integrated whitespace management

### Compatibility
- Added FreeCAD 1.1.Weekly support while maintaining FreeCAD 1.0.* compatibility
- All 30 automated tests passing on both versions

## [1.0.0] - 2025-09-02

### Added
- Multi-object 3MF export with hierarchical structure support
- 4-level debug logging system (0=off, 1=error, 2=warn, 3=log, 4=debug)
- Comprehensive Link wrapper system for FreeCAD App::Link objects
- Assembly and Group organizational container handling
- Custom ExportPath, ExportName, ExportDelimiter property system
- Multi-slicer support with ExportSlicer property filtering
- 30-test YAML-based validation suite with automated FreeCAD testing
- Property inheritance with LinkTreePriority controls
- ExportContainer/ExportShape force mode overrides
- Advanced slicer property passthrough for PrusaSlicer metadata

### Fixed  
- first release

### Technical Details
- Tree View integration with selection override capability
- Branch duplication removal for Link descendant cleanup
- Container expansion with volume organization logic
- 3MF file structure validation and property extraction
- "Individual shape without container" export behavior pattern
- Three-tier export exclusion logic (Basic, Structural, User Choice)

## Development History

This macro evolved from extensive development and testing focused on:
- FreeCAD object tree manipulation and Link object handling
- 3MF file format structure and PrusaSlicer metadata integration
- Property inheritance systems for complex assembly workflows
- Automated testing framework for FreeCAD macro validation
