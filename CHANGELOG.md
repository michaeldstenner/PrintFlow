# Changelog

All notable changes to PrintFlow will be documented in this file.

## [1.2.0] - 2025-01-xx

### Major Features Added
- **Complete Cura 3MF Export Support**
  - Full container/component architecture implementation for Cura compatibility
  - Source-code-verified property support with cura: namespace formatting
  - Pure property pass-through approach without slicer translation
  - Comprehensive Cura documentation with verified property reference

- **Enhanced Testing Infrastructure**
  - Achieved perfect 33/33 test coverage including all Cura functionality
  - Added expect_error support to test framework for negative testing
  - Intelligent FreeCAD auto-detection in runmacro.sh script
  - Fixed slicer_format_override test to validate proper error handling

- **Document Property Validation System**
  - Centralized RECOGNIZED_DOCUMENT_PROPERTIES registry
  - Startup validation with info-level logging for recognized properties
  - Warning-level logging for unrecognized properties (catches typos)
  - Single source of truth prevents property maintenance drift

### Architecture Improvements
- **Consistent Geometry Transformations**
  - Unified transformation logic between PrusaSlicer and Cura exporters
  - Fixed geometry positioning issues using pre-transformed vertices
  - Preserved matrix transformation methods for future enhancement

- **Design Decision Documentation**
  - Established document vs object property access patterns in LOGIC.md
  - Clarified that objects[None] represents tree root, not document wrapper
  - Documents accessed directly via FreeCAD.ActiveDocument for efficiency

### Testing and Quality Assurance
- **Comprehensive Multi-Slicer Testing**
  - All 33 tests pass on both PrusaSlicer and Cura export paths  
  - Cura-specific tests: basic export, assembly properties, extruder assignment
  - Property inheritance validation across both slicer formats

- **Enhanced Development Tools**
  - runmacro.sh with intelligent FreeCAD version detection and auto-selection
  - Support for explicit version override with -f flag
  - Improved error messages and user guidance

### Documentation
- **Complete User Manual Updates**
  - Added Cura Export Notes section explaining auto-placement behavior
  - Documented extruder assignment limitations and workarounds  
  - Source-code-verified Cura Properties Reference with special vs standard properties
  - Clear explanations of slicer behavior differences

- **Technical Documentation**  
  - Multi-slicer property compatibility guidelines
  - Document vs object property access design decisions
  - Property validation system architecture

### Backward Compatibility
- All existing PrusaSlicer workflows unchanged
- No breaking changes to property inheritance or export behavior
- Default slicer target remains PrusaSlicer for existing users

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
