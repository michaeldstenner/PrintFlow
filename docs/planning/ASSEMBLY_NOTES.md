# FreeCAD 1.0+ Assembly Support for FCExport

## Assembly Object Types

FreeCAD 1.0 introduces the Assembly workbench with these key object types:

- **`Assembly::AssemblyObject`** - Main Assembly container with spatial placement relationships
- **`Assembly::JointGroup`** - Contains joints/constraints (automatically pruned from export)

## Current FCExport Assembly Support

### Assembly Detection
- Objects with TypeId starting with `'Assembly::'` are automatically detected
- Assembly objects get default properties: `ExportContainer=False, ExportShape=False`

### Assembly Placement Control
- **`IgnoreAssemblyPlacement` property** (defaults to True)
  - When True: Objects maintain relative positions, Assembly absolute position ignored
  - When False: Include Assembly placement matrices for absolute positioning
  - Can be set at document level or per-Assembly object

### Assembly Infrastructure Pruning
- `Assembly::JointGroup` objects automatically removed from export (line 1184 in PrintFlow.FCMacro)
- Origin objects, axes, planes also pruned

### Link Object Support
- Link objects within Assemblies create virtual children (e.g., "WheelFL.Tire", "WheelFL.Rim")
- LinkTreePriority controls property inheritance precedence

## Creating Assembly Objects Programmatically

### Basic Assembly
```python
import FreeCAD as App

doc = App.ActiveDocument or App.newDocument("AssemblyTest")

# Create main Assembly container
assembly = doc.addObject("Assembly::AssemblyObject", "TestAssembly")
assembly.Label = "TestAssembly"

# Create parts
box1 = doc.addObject("Part::Box", "Part1")
box1.Label = "Part1"

# Add parts to assembly
assembly.addObject(box1)
doc.recompute()
```

### Assembly with Links (Virtual Wrapper Pattern)
```python
# Create master part
master_wheel = doc.addObject("App::Part", "MasterWheel") 
master_wheel.Label = "MasterWheel"

tire = doc.addObject("Part::Cylinder", "Tire")
tire.Label = "Tire"
master_wheel.addObject(tire)

rim = doc.addObject("Part::Cylinder", "Rim")
rim.Label = "Rim" 
master_wheel.addObject(rim)

# Create Assembly
car_assembly = doc.addObject("Assembly::AssemblyObject", "Car")
car_assembly.Label = "Car"

# Create Links at different positions
positions = [("WheelFL", (50, 50, 0)), ("WheelFR", (50, -50, 0))]
for name, pos in positions:
    link = doc.addObject("App::Link", name)
    link.Label = name
    link.LinkedObject = master_wheel
    link.Placement = App.Placement(App.Vector(*pos), App.Rotation())
    car_assembly.addObject(link)

doc.recompute()
```

### Assembly with Export Properties
```python
# Create exportable Assembly
buildplate = doc.addObject("Assembly::AssemblyObject", "BuildPlateExport")
buildplate.Label = "BuildPlateExport"  # Matches AutoExportPattern

# Add Export properties
buildplate.addProperty("App::PropertyBool", "Export", "Export")
buildplate.Export = True

buildplate.addProperty("App::PropertyBool", "IgnoreAssemblyPlacement", "Export")
buildplate.IgnoreAssemblyPlacement = True

# Add objects
for i, pos in enumerate([(0, 0, 0), (25, 0, 0), (0, 25, 0)]):
    part = doc.addObject("Part::Box", f"TestPart{i+1}")
    part.Placement = App.Placement(App.Vector(*pos), App.Rotation())
    buildplate.addObject(part)

doc.recompute()
```

## Assembly Object Hierarchy
```
Assembly::AssemblyObject (Main container)
├── Assembly::JointGroup (Constraints - auto-pruned)
├── Part objects
├── Link objects (create virtual children)
└── Other geometry objects
```

## Key Properties for Testing

### Document-Level Properties
- `AutoExportPattern` - Regex pattern for auto-export (default: ".*Export.*")
- `IgnoreAssemblyPlacement` - Global Assembly placement behavior
- `ExportDelimiter` - Path separator (default: ".")

### Object Properties (Export Group)
- `Export` - Whether to export object
- `ExportName` - Name to use in export path  
- `ExportShape` - Export object's geometry
- `ExportContainer` - Export as container (with children)
- `ExportPath` - Full hierarchical export path
- `IgnoreAssemblyPlacement` - Override global placement behavior

### Link Properties
- `LinkTreePriority` - Inheritance precedence (True = tree parent wins)

## Testing Strategy

1. **Basic Assembly Creation** - Test Assembly object creation and detection
2. **Assembly Export Properties** - Test Export property inheritance
3. **Link Virtual Children** - Test Link object virtual wrapper creation 
4. **Assembly Placement** - Test IgnoreAssemblyPlacement behavior
5. **Export Path Construction** - Test hierarchical path building
6. **Link Inheritance** - Test LinkTreePriority property inheritance
7. **Full Export Pipeline** - Test 3MF generation with Assembly objects

## Implementation Notes

- FCExport already has sophisticated Assembly support built-in
- Virtual wrapper system handles Link children automatically
- Property inheritance works correctly with Assembly hierarchies
- Assembly placement matrices are conditionally applied based on IgnoreAssemblyPlacement
- JointGroup objects are automatically excluded from export