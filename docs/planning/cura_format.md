# Cura 3MF Format Analysis

## Overview

Analysis of two Cura-generated 3MF files to understand the format structure and develop a strategy for PrintFlow's Cura export implementation.

**Files Analyzed:**
- `UMMXL_PassportMounts-e12/` - Single merged object with rich settings
- `UCP_belt_buckle-e1/` - Multi-object with container structure

## Single Object File Analysis (UMMXL_PassportMounts-e12)

### Structure
```xml
<model xmlns:cura="http://software.ultimaker.com/xml/cura/3mf/2015/10">
  <resources>
    <object id="1" name="PassportMounts-e12.3mf" type="model">
      <metadatagroup>
        <!-- Rich per-object settings -->
      </metadatagroup>
      <mesh>
        <!-- Single merged mesh -->
      </mesh>
    </object>
  </resources>
  <build>
    <item objectid="1" transform="..." />
  </build>
</model>
```

### Observed Cura Settings (cura: namespace)
- `cura:drop_to_buildplate` - Boolean (True/False)
- `cura:extruder_nr` - Integer extruder assignment (0, 1, 2...)
- `cura:infill_pattern` - String (zigzag, grid, lines, triangles, etc.)
- `cura:infill_sparse_density` - Integer percentage (20 = 20%)
- `cura:print_order` - Integer printing sequence
- `cura:speed_print` - Float mm/s speed (120.0)
- `cura:wall_line_count` - Integer perimeter count (2)

### Key Insights
- **Rich settings support**: Extensive per-object configuration
- **Namespace isolation**: All Cura settings use `cura:` prefix
- **Mixed data types**: Boolean, Integer, Float, String values
- **Single mesh approach**: All geometry merged into one object

## Multi-Object File Analysis (UCP_belt_buckle-e1)

### Structure
```xml
<model xmlns:cura="http://software.ultimaker.com/xml/cura/3mf/2015/10">
  <resources>
    <!-- Individual shape objects -->
    <object id="1" name="belt_buckle-e1.3mf(3)" type="model">
      <metadatagroup>
        <metadata name="cura:drop_to_buildplate">True</metadata>
        <metadata name="cura:print_order">1</metadata>
      </metadatagroup>
      <mesh><!-- Mesh data --></mesh>
    </object>
    <object id="2" name="belt_buckle-e1.3mf(4)" type="model">
      <!-- Similar structure -->
    </object>
    
    <!-- Container object using components -->
    <object id="6" name="MergedMesh" type="model">
      <metadatagroup>
        <metadata name="cura:drop_to_buildplate">True</metadata>
        <metadata name="cura:print_order">1</metadata>
      </metadatagroup>
      <components>
        <component objectid="1" transform="1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0" />
        <component objectid="2" transform="1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0" />
      </components>
    </object>
  </resources>
  <build>
    <!-- Mix of direct objects and containers -->
    <item objectid="3" transform="..." />  <!-- Direct object -->
    <item objectid="4" transform="..." />  <!-- Direct object -->  
    <item objectid="5" transform="..." />  <!-- Direct object -->
    <item objectid="6" transform="..." />  <!-- Container object -->
  </build>
</model>
```

### Additional Cura Settings Observed
- `cura:support_mesh` - Boolean (True for support material objects)
- Per-object `cura:print_order` - Different values (1,2,3,4) for printing sequence

### Container/Component Model
- **Container objects**: Use `<components>` instead of `<mesh>`
- **Component references**: `<component objectid="N" transform="..." />`
- **Transform inheritance**: Components can have individual positioning
- **Mixed build strategy**: Build section references both containers and individual objects

## Working Hypothesis: Combined Approach

Based on analysis of both files, we propose that Cura supports both approaches simultaneously:

### 1. Rich Settings Support (from File 1)
- Extensive per-object settings via `cura:` metadata namespace  
- Settings apply to both individual objects and containers
- PrintFlow can pass-through settings without understanding semantics

### 2. Container/Component Structure (from File 2)
- Multiple objects defined as separate `<object>` elements with `<mesh>`
- Container objects use `<components>` to reference other objects
- Build section can reference both containers and individual objects
- Transform matrices allow positioning within containers

### 3. Combined Strategy for PrintFlow
```xml
<!-- PrintFlow export approach -->
<resources>
  <!-- Each PrintFlow "shape" becomes a Cura object -->
  <object id="1" name="Part1" type="model">
    <metadatagroup>
      <!-- Pass-through PrintFlow properties with cura: prefix -->
      <metadata name="cura:extruder_nr">0</metadata>
      <metadata name="cura:infill_sparse_density">20</metadata>
      <metadata name="cura:wall_line_count">3</metadata>
    </metadatagroup>
    <mesh><!-- Part geometry --></mesh>
  </object>
  
  <!-- PrintFlow "container" becomes Cura container object -->
  <object id="3" name="Assembly" type="model">
    <metadatagroup>
      <!-- Container-level settings -->
      <metadata name="cura:print_order">1</metadata>
    </metadatagroup>
    <components>
      <component objectid="1" transform="..." />
      <component objectid="2" transform="..." />
    </components>
  </object>
</resources>
<build>
  <!-- Export containers, not individual parts -->
  <item objectid="3" transform="..." />
</build>
```

## Comparison: Cura vs PrusaSlicer

| Aspect | PrusaSlicer | Cura |
|--------|-------------|------|
| **Multi-part support** | Objects with multiple `<volume>` elements | Containers with `<component>` references |
| **Settings location** | `slic3r:` metadata + external config | `cura:` metadata in XML |
| **Namespace** | `xmlns:slic3rpe="http://schemas.slic3r.org/3mf/2017/06"` | `xmlns:cura="http://software.ultimaker.com/xml/cura/3mf/2015/10"` |
| **External files** | `Metadata/Slic3r_PE_model.config` | `Cura/` directory with extensive configs |
| **Geometry organization** | Volumes within objects | Objects referenced by components |

## Implementation Roadmap

### 1. CuraExporter Class Design
```python
class CuraExporter(ThreeMFExporter):
    # Cura-specific templates
    _RAW_MODEL = """
        <?xml version="1.0"?>
        <model unit="millimeter" 
               xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
               xmlns:cura="http://software.ultimaker.com/xml/cura/3mf/2015/10" 
               xml:lang="en-US">
          <resources>
            {objects}
          </resources>
          <build>
            {build}
          </build>
        </model>"""
    
    def _generate_object_structure(self):
        """Generate Cura container/component structure."""
        # Convert PrintFlow containers -> Cura container objects
        # Convert PrintFlow shapes -> Cura mesh objects
        pass
```

### 2. Template Structure
- Standard 3MF files: `[Content_Types].xml`, `_rels/.rels`
- Main model: `3D/3dmodel.model` with Cura namespace
- External configs: `Cura/` directory structure (investigate further)

### 3. Property Handling Strategy
- **Pass-through approach**: PrintFlow properties with `cura:` prefix added
- **Dual naming**: Support both `perimeters` and `wall_line_count` in same object
- **Format conversion**: Handle Boolean/Integer/Float/String value formatting

### 4. Testing Approach
- Create test objects with both PrusaSlicer and Cura properties
- Verify Cura imports and ignores unknown `slic3r:` properties
- Verify PrusaSlicer imports and ignores unknown `cura:` properties
- Test container/component structure export

## Open Questions

1. **External config files**: How much of the `Cura/` directory is required vs optional?
2. **Property conflicts**: Any cases where same property name means different things?
3. **Transform handling**: How do component transforms interact with build transforms?
4. **Version compatibility**: Do these patterns work across Cura versions?

## Next Steps

1. Implement basic `CuraExporter` class with container/component structure
2. Test property pass-through with simple objects
3. Research `Cura/` directory structure requirements
4. Create comprehensive test suite validating both slicer compatibility