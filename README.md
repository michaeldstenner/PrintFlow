<div align="center">

![PrintFlow](PrintFlow.svg)

# PrintFlow
**Stop fiddling with the slicer, stay focused on design.**

*From FreeCAD to Slicing in One Click*

</div>

A FreeCAD macro that transforms your 3D printing workflow by bringing advanced multi-object export capabilities and intelligent build plate management directly into FreeCAD.

## Why PrintFlow?

- **One-click export** from FreeCAD to your slicer  
- **Smart object detection** - exports what you actually want to print  
- **Build Plate Layout** - use FreeCAD Assemblies to arrange your parts perfectly
- **Embedded Print Settings** - no more reconfiguring every iteration  
- **Multi-Material Support** - set extruder and properties per-object
- **Designed Support Integration** - multi-shape objects make designed supports effortless

![Tree View](docs/tree_view.png) ![Slicer Result](docs/slicer.png)

## Three Ways to Use PrintFlow

### Method 1: Select and Go!
Perfect for rapid prototyping:
1. **Select objects** in FreeCAD Tree View
2. **Run PrintFlow** (F12 hotkey)  
3. **Done!** Slicer opens with perfect positioning

### Method 2: Smart Labels
For regular production parts:
1. **Add "Export" to object names** ("MyExportWheel", "Print_Bracket_Export")
2. **Run PrintFlow** - all Export objects automatically included
3. **Perfect for marking final parts** while excluding work-in-progress

### Method 3: Property Control  
For complex multi-material projects:
1. **Add Export properties** to objects (Boolean, Export group)
2. **Set Export=True/False** for precise control
3. **Add slicer properties** (extruder, layer_height, etc.) directly in FreeCAD

## Quick Start

1. Copy `PrintFlow.FCMacro` to your FreeCAD Macro directory
2. Open your FreeCAD document
3. Run the macro via Macro → Execute or F12 hotkey
4. Objects matching `.*Export.*` pattern export automatically, or set `Export=True` on specific objects

## Documentation

- **[User Manual](docs/PrintFlowManual.md)** - Complete usage guide with examples
- **[Design Logic](docs/planning/LOGIC.md)** - Technical architecture and property system

## Requirements

- FreeCAD 1.0+ (not tested with <1.0)

## License

MIT License - see macro header for details
