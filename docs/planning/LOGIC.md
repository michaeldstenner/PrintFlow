# Logic for the FCExport FreeCAD Macro
 - Make simple things easy: provide "do the right thing" simplicity
   for most common use cases with very little thought applied
   specifically to export.  Attempt to use common existing FreeCAD
   logic and organization to infer intended behavior.  Assumptions
   include:
   - FreeCAD Groups and Assemblies should not be exported as
     monolithic entities, but rather are organizational (logical
     for Groups, logical *and* spatial for Assemblies).
   - StdPart objects are monolithic and will be mapped to a top-level
     object in the slicer.  When a StdPart consists of more than one
     sub-shapes (in the Tree View) they will each become a "part" in
     the slicer, allowing for different material, properties, etc.
   - All other objects (booleans, compounds, etc.) are assumed to
     represent a single shape, which will become a "part" if contained
     within a StdPart, or otherwise will become an "object" in the slicer.
 - Make hard things possible: provide enough flexibility that any
   arbitrary mapping of FreeCAD objects to slicer objects is possible
   and *obvious*.  It may require more clicking and typing, but it's
   very clear how to brute-force the intended outcome.
 - Provide some space in-between: make some helper-properties that
   make the most common variations easy to implement.

## Property Management

### Macro Control Properties

Behavior of the macro managed through FreeCAD object properties.
Properties are managed in three places:
 - Document Properties: These are used for document level settings and
   overriding defaults for the entire document.
 - Object Properties: These are used to affect the object they apply
   to, and many are inherited by sub-objects in the tree view.
 - Internal Properties: These are not (by default) stored in the
   FreeCAD objects themselves, but are calculated and managed within
   the macro each time it is run.  This is where inheritance is
   handled.
   
In general, Internal Properties are managed through a lot of logic
(that's what this document is about), but all of that complex logic
can be overridden or short-circuited by explicitly defining an Object
Property. 

All properties are placed in the "Export" group (by default) of their
various objects.

### Slicer Behavior Properties

Definition of properties is also used to control slicer behavior.
Slicer modifiers can be included as object properties, and they will
be included in the slicer output. FCExport processes all properties
regardless of their FreeCAD property group assignment, giving users
maximum flexibility to organize properties visually however they prefer.

Some example slicer properties are included below, but the list is
determined mostly by the slicer itself, not the macro.  That is, the
macro simply passes properties on to the slicer without understanding
(or needing to understand) them.  The easiest way to learn new
properties is to set them in your slicer, save the project as a .3mf
file, unzip it (3MF is a zip file), and explore the files therein.

#### Multi-Slicer Property Compatibility

PrintFlow supports multiple slicer formats (PrusaSlicer, Cura) but does
**NOT** translate properties between formats. Each slicer format uses its
own property naming conventions:

- **PrusaSlicer**: Properties like `extruder`, `perimeters`, `fill_density`
- **Cura**: Properties like `extruder_nr`, `wall_line_count`, `infill_sparse_density`

Users should set properties using the naming convention appropriate for
their target slicer. PrintFlow will pass all properties through unchanged
to the 3MF output, with appropriate namespace formatting applied during
file generation. This approach:

1. **Preserves user intent** - No automatic translation means no surprises
2. **Maintains compatibility** - Both slicers can coexist in the same document
3. **Supports future formats** - New slicer formats work without code changes
4. **Enables mixed workflows** - Different objects can target different slicers

## Export Processing Architecture

### Wrapper Tree System

FCExport creates an internal **Wrapper Tree** that mirrors the FreeCAD Tree but with modifications for export processing:

1. **Wrapper Objects**: Each FreeCAD object gets a corresponding wrapper object that tracks export-related metadata
2. **Link Expansion**: Link objects are replaced with **link wrapper** subtrees that represent the linked object hierarchy at the Link's tree position
3. **Property Inheritance**: Properties flow down the Wrapper Tree according to inheritance rules
4. **Export List Generation**: Final export decisions are made based on Wrapper Tree structure and properties

### Three-Tier Export Exclusion Logic

Objects are excluded from export through three logically separate mechanisms:

#### 1. Basic Eligibility (Initial Tree Creation)
Objects fundamentally unsuitable for 3D printing are eliminated during initial Wrapper Tree creation:
- **2D objects**: Sketches, planes, axes
- **Infrastructure objects**: Origins, coordinate systems
- **Assembly metadata**: JointGroups, constraints
- **Rationale**: "You can't 3D print a 2D object"

#### 2. Structural Eligibility (False/False Designation)
Objects that could be printed but whose shape is represented at a different granularity level:
- **Children of shape-bearing non-App::Part objects**: Their shape is included in the parent's shape
- **Link array elements**: Individual `Link002_i*` objects included in parent Link's shape
- **PartDesign features within Bodies**: Represented by the Body's final shape
- **Properties**: `ExportShape=false, ExportContainer=false`
- **Rationale**: "The shape exists but is represented elsewhere in the tree"

#### 3. User Choice (Export=False)
Eligible objects explicitly excluded by user preference:
- **Explicit setting**: User sets `Export=false` property
- **Selection override**: User selects specific objects, excluding others
- **Rationale**: "User override of default behavior"

#### PrusaSlicer

| Property | Type | Description | Example Values |
|----------|------|-------------|----------------|
| `extruder` | int | Extruder number | `1`, `2`, `3` |
| `layer_height` | float | Layer height in mm | `0.2`, `0.15`, `0.3` |
| `perimeters` | int | Number of perimeters | `2`, `3`, `4` |
| `bottom_solid_layers` | int | Bottom solid layers | `3`, `5` |
| `top_solid_layers` | int | Top solid layers | `3`, `5` |
| `fill_density` | string | Infill density as percentage | `"15%"`, `"20%"`, `"100%"` |
| `fill_pattern` | string | Infill pattern type | `"grid"`, `"rectilinear"`, `"gyroid"`, `"cubic"`, `"honeycomb"` |
| `support_material` | int | Enable supports | `0` (off), `1` (on) |
| `support_material_auto` | int | Auto-generate supports | `0` (off), `1` (on) |
| `support_material_buildplate_only` | int | Supports from buildplate only | `0` (off), `1` (on) |
| `support_material_interface_pattern` | string | Support interface pattern | `"auto"`, `"rectilinear"` |
| `support_material_pattern` | string | Support pattern | `"rectilinear"`, `"grid"` |
| `support_material_spacing` | float | Support spacing in mm | `2.5`, `3.0` |
| `support_material_threshold` | float | Support threshold angle in degrees | `45`, `60` |
| `wipe_into_infill` | int | Wipe into infill | `0` (off), `1` (on) |
| `wipe_into_objects` | int | Wipe into objects | `0` (off), `1` (on) |

## Property List (Objects)

### `ExportPath` (String)

This is the property that most directly impacts export, and can be
overridden only by explicit Object Property definition or selection in
the tree view.  It is a string consisting of one or more names
separated by the `ExportDelimiter` (default = `"."`).

**Purpose**: Each name refers to a level in the slicer object hierarchy.

**Forward Compatibility**: If there are more levels than the slicer can handle, parts will be peeled off the top levels.

**Example**: `"Wheel.Rim.Lugnut"` would become:
```
- Wheel
   - Rim.Lugnut
```

**Derivation**: Automatically derived from `ExportName`, `ExportContainer`, and `ExportShape` unless explicitly overridden in the FreeCAD object properties.

**Important**: When selecting individual shape objects without their containers, the full `ExportPath` becomes both the object name and volume name in the 3MF output. This occurs because the referenced container objects are not included in the export, preventing hierarchical structure creation.

### `ExportName` (String)

The string used to represent one level of `ExportPath` for the given object.

**Default**: Uses the wrapper object's `label` property, which reflects the FreeCAD object's `Label`

**Override**: Can be explicitly set to use a different name in export

**Relationship to ExportPath**: `ExportPath` is built by walking up the wrapper tree and joining `ExportName` values with the delimiter

**Use Case**: When multiple parts should have the same name in the slicer but different names in FreeCAD
- FreeCAD: `Lugnut001`, `Lugnut002`, `Lugnut003`  
- Export: All become `Lugnut`

**Important**: For wrapper objects, `label` always contains the actual FreeCAD object's Label (with special handling for Links). Tree hierarchy is maintained through parent/children relationships, not encoded in labels.

### `ExportShape` (Boolean)

Specifies that the object should be exported as a physical shape to the slicer.

**Behavior**:
- Uses the object's `.Shape` attribute directly
- Sub-objects are ignored
- Object becomes a "part" in the slicer

**Example**: For a `Part.Cut` object, exports the *result* of the boolean subtraction, not the base and tool shapes used to create it.

**Guarantee**: Any object with `ExportShape=true` explicitly set *will* be included in the exported data.

**Note**: If neither `ExportShape` nor `ExportContainer` is true, the object contributes only its name to the export path.

### `ExportContainer` (Boolean)

Specifies that the object should be exported as a container to the slicer.

**Behavior**:
- The object's `.Shape` attribute is *not* used
- Shape comes from its sub-objects
- Object becomes an "object" in the slicer, containing multiple "parts"

**Example**: Multi-material sign
- `Sign` object (StdPart) with `ExportContainer=true`
- Contains `Letters` object and `Background` object
- Results in one slicer object with two parts

**Conflict Resolution**: If both `ExportContainer=true` and `ExportShape=true` are explicitly set, `ExportShape` takes priority (console warning issued).

### `LinkTreePriority` (Boolean)

Controls property inheritance priority for Link objects in the virtual wrapper system.

**Default**: `true` (tree parent takes priority)

**Behavior**:
- `true`: Tree parent properties override linked object properties
- `false`: Linked object properties override tree parent properties

**Use Case**: When you want a Link to inherit most properties from its linked object rather than its tree position (e.g., material properties from master part vs. assembly-level settings).

**Note**: Explicit properties set directly on the Link object always take highest priority regardless of this setting.

### `IgnoreAssemblyPlacement` (Boolean)

Controls whether Assembly placement matrices are included in tessellation calculations for objects within the Assembly.

**Default**: `true` (Assembly placements are ignored)

**Behavior**:
- `true`: Skip Assembly placement matrices during tessellation (relative positioning within Assembly)
- `false`: Include Assembly placement matrices (absolute positioning including Assembly position)

**Scope**: Can be set at document level (affects all Assemblies) or on individual Assembly objects

**Use Case**: 
- **Build plate workflow** (default): Objects maintain relative positions within Assembly, ignoring Assembly's absolute position
- **Absolute positioning**: Include Assembly placement for objects that need to maintain absolute world coordinates

**Example**: Assembly at (100, 50, 0) containing wheel at relative (10, 10, 0):
- `IgnoreAssemblyPlacement=true`: Wheel exports at (10, 10, 0) 
- `IgnoreAssemblyPlacement=false`: Wheel exports at (110, 60, 0)

## Property List (Document)

### `ExportDelimiter` (String)

The string delimiter used to generate and parse the names of objects to be exported.

**Default**: `"."`

### `AutoExportPattern` (String)

A regular expression pattern used to identify objects that should have `Export=true` by default based on their `Label`.

**Default**: `".*Export.*"` (matches any object whose Label contains "Export")

**Examples**:
- `"MyExportGroup"` -> matches
- `"ExportWheel"` -> matches  
- `"WheelExport"` -> matches
- `"MyGroup"` -> does not match

### `ExportSlicer` (String)

Specifies which slicer to target for export processing.

**Default**: "PrusaSlicer"

**Behavior**: Controls which objects are included in export when `ExportSlicer` properties are present on objects (see Multi-Slicer Support section below).

## Property Derivation

This section and the next one have similar names (Derivation vs
inheritance) but are logically distinct.  In this section we discuss
how (for example) the ExportPath property is calculated from other
properties such as ExportName and ExportContainer.  The next section
discusses how sub-objects may "inherit" properties from parents in the
tree view.

 - Export structure in the output file is uniquely determined by the
   ExportPath property, but may depend on the capabilities of the
   target slicer and its export class.  For example, as discussed
   above, for slicers that only allow two levels, then only one level
   of containers will be used.
 - **ExportPath Boundary Rules**: ExportPath construction is bounded by ExportContainer and ExportShape properties:
   - **Above topmost ExportContainer**: Objects get ExportPath='' (empty) and are excluded from export
   - **ExportContainer to ExportShape "sandwich"**: Normal ExportPath construction applies
   - **Below bottommost ExportShape**: Objects get ExportPath='' (empty) and are excluded from export
   - This creates clean semantic boundaries where only the meaningful export hierarchy appears in the 3MF structure
   - **Example**: `Assembly -> BuildPlate(ExportContainer=true) -> MidObj(false/false) -> Body(ExportShape=true) -> Pad(Export=true)`
     - `Assembly`: ExportPath='' (above topmost container)
     - `BuildPlate`: ExportPath="BuildPlate" (topmost container)  
     - `MidObj`: ExportPath="BuildPlate.MidObj" (in sandwich)
     - `Body`: ExportPath="BuildPlate.MidObj.Body" (bottommost shape)
     - `Pad`: ExportPath='' (below bottommost shape)
     - **3MF Result**: Object "BuildPlate", Volume "MidObj.Body"
 - Within the valid boundary range, an object's ExportPath consists of its own
   ExportName, preceded by the ExportName of all ExportContainer=true
   objects above it in the Tree View, regardless of whether they have
   ExportShape=True.
 - ExportName is the object's .Label property unless the user has
   explicitly set the object's ExportName property.
 - **ExportShape and ExportContainer combinations:**

   | `ExportShape` | `ExportContainer` | Behavior |
   |---------------|-------------------|----------|
   | `true` | `false` | Object exports its `.Shape` as physical geometry |
   | `false` | `true` | Object acts as container, sub-objects are evaluated |
   | `false` | `false` | Object contributes only its `ExportName` to `ExportPath` (naming layer) |
   | `true` | `true` | `ExportShape` takes priority, object exports its `.Shape` and ignores sub-objects (WARNING) |
   
   *Console warning issued when both are explicitly set to `true`*
 - ExportShape will default to true for any object that:
   - has a 3D Shape (not axes, for example),
   - is not a Group, Assembly, StdPart with multiple 3D-shaped
     sub-objects, or a Link to one of these, and
   - has Export set to true
 - ExportContainer will default to true for any object that:
   - is a StdPart with multiple 3D-shaped sub-objects and
   - has Export set to true
 - Export will default to true for any object whose Label matches the
   AutoExportPattern regular expression (default: ".*Export.*")

## Inheritance
 - Unless otherwise noted in this or the previous section, Internal
   Properties are inherited within the Tree View.  For example, if a
   Group has Export=true set either explicitly or because it is named
   "MyExportGroup", then all descendents within that group will also
   have Export=true unless explicitly set.
 - ExportContainer, ExportShape, ExportName, and ExportPath are not
   inherited along the Tree View structure.
 - **Link Wrapper System:** Links are replaced with link wrapper subtrees in the Wrapper Tree that create
   "hardlink-like" behavior for export purposes:
   
   **Link Wrapper Creation:**
   - Each Link object is replaced by a link wrapper representing the linked object at the Link's tree position
   - Link wrapper subtrees are created recursively for all children of the linked object
   - **Link wrapper labels**: Link wrapper gets the Link's Label; descendant wrappers get their original object's Label
   - **Tree hierarchy**: Maintained through parent/children relationships, not encoded in labels
   - Example: `WheelFL` Link → `MasterWheel` creates:
     - `WheelFL` link wrapper (label=`"WheelFL"`, wraps MasterWheel)
     - Child wrappers: `Tire` (label=`"Tire"`), `Rim` (label=`"Rim"`)
     - ExportPath built by joining: `"WheelFL.Tire"`, `"WheelFL.Rim"`
   
   **Property Inheritance Strategy:**
   - **Link wrapper**: Inherits properties from both tree parent and linked object,
     with priority determined by `LinkTreePriority` (default=true, tree wins)
   - **Link wrapper children**: Inherit properties normally through the link wrapper subtree
   - **Namespace isolation**: Each Link creates its own export namespace
     (`WheelFL.Tire` vs `WheelFR.Tire` for same underlying FreeCAD object)
   
   **Export Behavior:**
   - Link wrappers with `ExportContainer=true` export their children as separate objects  
   - Link wrappers with `ExportShape=true` export the linked object's shape directly
   - **Link Array Handling**: Individual array elements (`Link002_i*`) get False/False designation (Structural Eligibility exclusion) and are excluded from final export, with their shapes included in the parent Link's representation
   - **User Intent Disambiguation**: When the same FreeCAD object appears in multiple wrapper paths and has `Export=true`, Link wrapper children are excluded if their Link parent does NOT have `Export=true`. This assumes the user intended to export the object through a different (non-Link) path rather than as part of a Link subtree.
 - **Selection Override:** When objects are selected in the Tree View,
   selection overrides the top-level Export behavior:
   - Selected objects will be exported regardless of their Export property
   - Non-selected objects will not be exported, even if Export=true
   - Selection propagates Export=true down the tree (normal inheritance applies)
   - ExportPath construction remains normal for selected objects, providing
     visual feedback about partial export scope

## Assembly and Group Handling

Both Groups and Assemblies are treated as organizational containers by default:

### Default Properties
- `ExportContainer=false, ExportShape=false` (organizational, not exportable units)
- Objects within are treated as distinct (do not merge into single slicer object)
- Groups and Assemblies contribute their `ExportName` to sub-object `ExportPaths` when in the inheritance chain

### Assembly Object Types (FreeCAD 1.0+)
- **`Assembly::AssemblyObject`**: Main Assembly container with spatial placement relationships
- **`Assembly::JointGroup`**: Contains joints/constraints (automatically pruned from export)

### Assembly Spatial Behavior
**Assemblies** preserve spatial placement relationships for build plate layout, while **Groups** are purely organizational.

**Placement Control**: Assembly objects get `IgnoreAssemblyPlacement=true` by default
- Objects within Assembly maintain relative positions to each other
- Assembly's absolute position is ignored during export
- Can be overridden at document or object level for absolute positioning needs

### Build Plate Workflow
Common use case: Assembly as "build plate" for arranging multiple parts:

```
BuildPlate (Assembly::AssemblyObject, Export=true, IgnoreAssemblyPlacement=true)
├── Part1 (Link, at relative position (0, 0, 0))
├── Part2 (Link, at relative position (50, 0, 0))  
└── Part3 (Link, at relative position (0, 50, 0))
```

**Export Result**: Parts maintain relative 50mm spacing regardless of BuildPlate's absolute position

## Link Wrapper Example

**FreeCAD Tree Structure:**
```
Car (Group, Export=true)
├── WheelFL (Link → MasterWheel)  
├── WheelFR (Link → MasterWheel)
├── WheelRL (Link → MasterWheel)
└── WheelRR (Link → MasterWheel)

MasterWheel (App::Part, ExportContainer=true)
├── Tire (Part::Cylinder, ExportShape=true)
└── Rim (Part::Cylinder, ExportShape=true)
```

**Link Wrapper Subtree Created:**
```
Car (Export=true)
├── WheelFL (Export=true, ExportContainer=true) 
│   ├── WheelFL.Tire (Export=true, ExportShape=true)
│   └── WheelFL.Rim (Export=true, ExportShape=true)
├── WheelFR (Export=true, ExportContainer=true)
│   ├── WheelFR.Tire (Export=true, ExportShape=true) 
│   └── WheelFR.Rim (Export=true, ExportShape=true)
├── WheelRL (Export=true, ExportContainer=true)
│   ├── WheelRL.Tire (Export=true, ExportShape=true)
│   └── WheelRL.Rim (Export=true, ExportShape=true)
└── WheelRR (Export=true, ExportContainer=true)
    ├── WheelRR.Tire (Export=true, ExportShape=true)
    └── WheelRR.Rim (Export=true, ExportShape=true)
```

**Final Export Result:**
- 8 objects exported: `WheelFL.Tire`, `WheelFL.Rim`, `WheelFR.Tire`, `WheelFR.Rim`, `WheelRL.Tire`, `WheelRL.Rim`, `WheelRR.Tire`, `WheelRR.Rim`
- Each tire/rim object points to the same underlying FreeCAD geometry but appears as separate components in the slicer
- Spatial transformations from Link placements are applied to position each wheel correctly

## Multi-Slicer Support

FCExport supports targeting multiple slicer applications through the Link wrapper system and `ExportSlicer` property filtering. This allows complete property separation without namespace conflicts by organizing geometry into slicer-specific Link trees.

### Slicer Selection Hierarchy
1. **Document Level**: `ExportSlicer` property sets the default target slicer for the entire document
2. **Object Level**: `ExportSlicer` property on individual objects overrides document default
3. **Default Behavior**: If no `ExportSlicer` property is found, defaults to "PrusaSlicer"

### Selection Override Behavior
- **User selection present**: Export selected objects regardless of document-level `ExportSlicer` setting
- **Slicer detection from selection**: 
  - If all selected objects have the same `ExportSlicer` value, use that slicer
  - If selected objects have mixed `ExportSlicer` values, use document-level setting
  - If no `ExportSlicer` properties on selected objects, use document-level setting

### Export Filtering Rules (No Selection)
- Only objects whose effective `ExportSlicer` value matches the current export target are processed
- Objects with mismatched `ExportSlicer` values are completely ignored during export
- Standard inheritance rules apply: object-level overrides document-level

### Multi-Slicer Workflow Pattern
**Recommended organization for multi-slicer projects:**
```
Document ExportSlicer: PrusaSlicer (default)

MyProject/
├── Geometry/                    # Original objects (no ExportSlicer)
│   ├── MainPart
│   └── SupportPart
├── PrusaSlicer_Assembly/        # ExportSlicer: PrusaSlicer
│   ├── MainPart_Link → MainPart (PrusaSlicer properties)
│   └── SupportPart_Link → SupportPart
└── Cura_Assembly/               # ExportSlicer: Cura  
    ├── MainPart_Link → MainPart (Cura properties)
    └── SupportPart_Link → SupportPart
```

### Implementation Details
- Export target slicer specified via command-line argument or document property
- Selection behavior overrides document-level filtering rules
- Users can export to multiple slicers by running FCExport multiple times with different targets
- Single-slicer users can continue using properties directly without any `ExportSlicer` properties

### Backward Compatibility
- Existing documents without `ExportSlicer` properties continue working unchanged
- Default slicer target remains PrusaSlicer
- All existing property and inheritance behavior preserved

## Data Structure Design Decisions

### Document vs Object Property Access

**Design Principle**: Documents and FreeCAD objects are accessed using different patterns that reflect their fundamental differences.

**Document Properties** (configuration, global settings):
- **Access Pattern**: Direct via `FreeCAD.ActiveDocument.PropertyName`
- **Examples**: `SlicerFormat`, `ExportDelimiter`, `AppendVersion`, `PrintFlowDebug`
- **Rationale**: Documents are containers that hold configuration. Direct access is simple, efficient, and matches FreeCAD's API design.

**Object Properties** (geometry, per-object settings):
- **Access Pattern**: Through FCObjectTree via `objects[key].iprop['PropertyName']`  
- **Examples**: `Export`, `ExportName`, `ExportPath`, slicer settings
- **Rationale**: Objects are wrapped to enable property inheritance, tree relationships, and unified processing.

**Tree Structure**: 
- `objects[None]` represents the tree root (top-level container), not the document itself
- The document does not participate in the parent/child object hierarchy
- Tree relationships are between FreeCAD objects, not between document and objects

**Property Validation**:
PrintFlow maintains a centralized registry of recognized document properties (`RECOGNIZED_DOCUMENT_PROPERTIES`) to help users catch typos and understand active settings:

- **Recognized properties**: Logged at info level during startup
- **Unrecognized properties**: Logged at warn level (potential typos in PrintFlow group)
- **Registry maintenance**: Add new properties to the registry when implementing new features

This separation keeps the codebase conceptually clean and operationally efficient while matching FreeCAD's natural API patterns.
