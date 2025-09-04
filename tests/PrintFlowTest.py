# -*- mode: python; eval: (auto-revert-mode 1); fill-column: 78; -*-
"""
PrintFlow Test Framework - YAML-based comprehensive testing

Tests PrintFlow functionality with multiple test cases defined in YAML.
"""

import importlib
import importlib.util
import os

import FreeCAD
import yaml

def setup_printflow_import():
    """Create temporary .py symlink for PrintFlow.FCMacro import"""
    import platform

    # Work in the same directory where FreeCAD is running this test
    test_dir = os.path.dirname(os.path.abspath(__file__))
    fcmacro_path = os.path.join(test_dir, "PrintFlow.FCMacro")
    py_path = os.path.join(test_dir, "PrintFlow.py")

    if not os.path.exists(fcmacro_path):
        raise FileNotFoundError(f"Cannot find PrintFlow.FCMacro at "
                                f"{fcmacro_path}")

    # Remove existing .py file/link if present
    if os.path.exists(py_path):
        os.remove(py_path)

    # Create symlink (cross-platform)
    try:
        if platform.system() == "Windows":
            # Try hard link first (no admin needed)
            os.link(fcmacro_path, py_path)
            print(f"Created hard link: PrintFlow.py -> PrintFlow.FCMacro")
        else:
            # Unix/Linux/Mac - use symlink
            os.symlink("PrintFlow.FCMacro", "PrintFlow.py")
            print(f"Created symlink: PrintFlow.py -> PrintFlow.FCMacro")
    except OSError:
        # Fallback: copy the file
        import shutil
        shutil.copy2(fcmacro_path, py_path)
        print(f"Created copy: PrintFlow.py from PrintFlow.FCMacro")

    return py_path

def cleanup_printflow_import():
    """Remove temporary PrintFlow.py file"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    py_path = os.path.join(test_dir, "PrintFlow.py")

    if os.path.exists(py_path):
        os.remove(py_path)
        print("Cleaned up temporary PrintFlow.py")

# Setup import and import PrintFlow
setup_printflow_import()
import PrintFlow
importlib.reload(PrintFlow)
PrintFlow.DEBUG = 4  # Full debug level for tests
PrintFlow.SHOW_ERROR_DIALOGS = False  # Disable error dialogs during testing

# Configure test file paths - use realpath to resolve symlinks
TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_3MF_PATH = os.path.join(TEST_DIR, "PrintFlowTest.3mf")


def parse_test_definitions():
    """Parse YAML test definitions from external file."""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(test_dir, "PrintFlowTest.yaml")

    # Resolve symlinks to get real path
    yaml_path = os.path.realpath(yaml_path)

    PrintFlow.debug(f"Loading test definitions from: {yaml_path}")

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Test definitions file not found: "
                                f"{yaml_path}")

    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
        PrintFlow.debug(f"Loaded {len(data.get('tests', {}))} test "
                          f"definitions")
        return data

def clear_all_export_properties(doc):
    """Clear all Export properties from all objects."""
    cleared_count = 0
    for obj in doc.Objects:
        if hasattr(obj, 'Export'):
            obj.removeProperty('Export')
            PrintFlow.debug(f"  Cleared Export from {obj.Label}")
            cleared_count += 1
    PrintFlow.debug(f"Cleared {cleared_count} Export properties")

def clear_test_properties(doc):
    """Clear test-specific properties that were added during testing."""
    cleared_count = 0
    test_props_to_clear = ['LinkTreePriority']  # Add more as needed

    for obj in doc.Objects:
        for prop_name in test_props_to_clear:
            if hasattr(obj, prop_name):
                try:
                    obj.removeProperty(prop_name)
                    PrintFlow.debug(f"  Cleared {prop_name} from "
                                      f"{obj.Label}")
                    cleared_count += 1
                except Exception as e:
                    PrintFlow.debug(f"  Warning: Could not clear "
                                      f"{prop_name} from {obj.Label}: {e}")

    # Also clear all PrintFlow document properties
    printflow_props = ['LinkTreePriority', 'AutoExportPattern', 'AppendVersion', 
                       'ExportVersion', 'ExportPattern', 'ExportDelimiter',
                       'PrintFlowDebug', 'RunSlicer', 'SlicerFormat', 
                       'IgnoreAssemblyPlacement']
    for prop_name in printflow_props:
        if hasattr(doc, prop_name):
            try:
                doc.removeProperty(prop_name)
                PrintFlow.debug(f"  Cleared {prop_name} from document "
                                  f"{doc.Label}")
                cleared_count += 1
            except Exception as e:
                PrintFlow.debug(f"  Warning: Could not clear "
                                  f"{prop_name} from document: {e}")

    PrintFlow.debug(f"Cleared {cleared_count} test properties")

def apply_export_settings(doc, export_settings):
    """Apply export settings to objects."""
    PrintFlow.debug(f"Applying export settings: {export_settings}")

    for obj_label, export_value in export_settings.items():
        objs = doc.getObjectsByLabel(obj_label)
        if objs:
            obj = objs[0]
            if export_value is True:
                if not hasattr(obj, 'Export'):
                    obj.addProperty('App::PropertyBool', 'Export', 'Export')
                obj.Export = True
                PrintFlow.debug(f"  Set {obj_label}.Export = True")
            elif export_value is False:
                if not hasattr(obj, 'Export'):
                    obj.addProperty('App::PropertyBool', 'Export', 'Export')
                obj.Export = False
                PrintFlow.debug(f"  Set {obj_label}.Export = False")
            elif export_value is None:
                if hasattr(obj, 'Export'):
                    obj.removeProperty('Export')
                    PrintFlow.debug(f"  Removed Export property from "
                                      f"{obj_label}")
        else:
            PrintFlow.debug(f"  WARNING: Object {obj_label} not found")

def apply_property_settings(doc, property_settings):
    """Apply arbitrary property settings to objects or document."""
    PrintFlow.debug(f"Applying property settings: {property_settings}")

    for obj_label, properties in property_settings.items():
        # Special case: setting properties on the document itself
        if obj_label == doc.Label:
            target_obj = doc
            PrintFlow.debug(f"  Setting properties on document: "
                              f"{doc.Label}")
        else:
            objs = doc.getObjectsByLabel(obj_label)
            if objs:
                target_obj = objs[0]
            else:
                PrintFlow.debug(f"  WARNING: Object {obj_label} "
                                  f"not found")
                continue

        for prop_name, prop_value in properties.items():
            try:
                # Determine property type based on value
                if isinstance(prop_value, bool):
                    prop_type = 'App::PropertyBool'
                elif isinstance(prop_value, int):
                    prop_type = 'App::PropertyInteger'
                elif isinstance(prop_value, float):
                    prop_type = 'App::PropertyFloat'
                else:
                    prop_type = 'App::PropertyString'

                # Add property if it doesn't exist
                if not hasattr(target_obj, prop_name):
                    # Use correct property group based on property type
                    if obj_label == 'PrintFlowTest':  # Document properties
                        prop_group = 'PrintFlow'
                    else:  # Object properties
                        prop_group = 'Export'
                    target_obj.addProperty(prop_type, prop_name, prop_group)

                # Set property value
                setattr(target_obj, prop_name, prop_value)
                PrintFlow.debug(f"  Set {obj_label}.{prop_name} = "
                                  f"{prop_value}")

            except Exception as e:
                PrintFlow.debug(f"  ERROR: Failed to set "
                                  f"{obj_label}.{prop_name} = "
                                  f"{prop_value}: {e}")

def extract_metadata(element, metadata_type):
    """Extract metadata dictionary from XML element."""
    metadata = {}
    for meta in element.findall(f'metadata[@type="{metadata_type}"]'):
        key = meta.get('key')
        value = meta.get('value')
        metadata[key] = value
    return metadata

def get_name_from_metadata(metadata, fallback_id):
    """Get name from metadata, using fallback strategies."""
    return metadata.get('name',
                       metadata.get('ExportPath',
                                   f'Object{fallback_id}'))

def parse_prusaslicer_objects(config_root):
    """Parse objects from PrusaSlicer config XML."""
    structure = {}
    all_objects = []
    all_volumes = []

    objects = config_root.findall('object')
    PrintFlow.debug(f"Found {len(objects)} objects in PrusaSlicer "
                      f"metadata")

    for obj_elem in objects:
        obj_id = obj_elem.get('id')
        obj_metadata = extract_metadata(obj_elem, "object")
        obj_name = get_name_from_metadata(obj_metadata, obj_id)
        all_objects.append(obj_name)
        PrintFlow.debug(f"  Object {obj_id}: name='{obj_name}', "
                          f"metadata={obj_metadata}")

        volumes = []
        volume_elems = obj_elem.findall('volume')
        PrintFlow.debug(f"    Found {len(volume_elems)} volumes")

        for volume_elem in volume_elems:
            volume_metadata = extract_metadata(volume_elem, "volume")
            volume_name = volume_metadata.get('name',
                            volume_metadata.get('ExportPath',
                                               'UnnamedVolume'))
            volumes.append(volume_name)
            all_volumes.append(volume_name)
            PrintFlow.debug(f"      Volume: name='{volume_name}', "
                              f"metadata={volume_metadata}")

        structure[obj_name] = volumes

    return structure, all_objects, all_volumes, objects

def extract_slicer_properties(config_root):
    """Extract non-Export properties from objects and volumes."""
    properties = {}
    objects = config_root.findall('object')

    for obj_elem in objects:
        obj_metadata = extract_metadata(obj_elem, "object")
        obj_name = get_name_from_metadata(obj_metadata, obj_elem.get('id'))

        slicer_props = {k: v for k, v in obj_metadata.items()
                       if not k.startswith('Export') and k not in ['name']}

        if slicer_props:
            properties[obj_name] = slicer_props
            PrintFlow.debug(f"Object {obj_name} properties: "
                              f"{slicer_props}")

        for volume_elem in obj_elem.findall('volume'):
            volume_metadata = extract_metadata(volume_elem, "volume")
            volume_name = volume_metadata.get('name',
                            volume_metadata.get('ExportPath',
                                               'UnnamedVolume'))

            slicer_props = {k: v for k, v in volume_metadata.items()
                            if (not k.startswith('Export') and 
                                k not in ['name'])}

            if slicer_props:
                properties[volume_name] = slicer_props
                PrintFlow.debug(f"Volume {volume_name} properties: "
                                  f"{slicer_props}")

    return properties

def parse_cura_objects(model_root):
    """Parse Cura 3MF container/component structure from XML.
    
    Returns:
        tuple: (structure_dict, properties_dict)
        - structure_dict: {container_name: [volume_names]}  
        - properties_dict: {object_name: {property_name: value}}
    """
    structure = {}
    properties = {}
    
    ns = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
    
    # Find all objects in the model
    objects = model_root.findall(f'.//{ns}object')
    PrintFlow.debug(f"Found {len(objects)} objects in Cura model")
    
    # Separate shape objects (with mesh) from container objects (with components)
    shape_objects = {}  # id -> {name, metadata}
    container_objects = {}  # id -> {name, metadata, component_ids}
    build_items = set()  # ids of objects in build section
    
    for obj in objects:
        obj_id = obj.get('id')
        obj_name = obj.get('name', f'Object{obj_id}')
        obj_type = obj.get('type', 'model')
        
        PrintFlow.debug(f"  Object {obj_id}: name='{obj_name}', type={obj_type}")
        
        # Parse metadata
        metadata = {}
        metadatagroup = obj.find(f'{ns}metadatagroup')
        if metadatagroup is not None:
            for meta in metadatagroup.findall(f'{ns}metadata'):
                key = meta.get('name', '')
                value = meta.text or ''
                # Store all metadata as-is (both cura: and non-cura properties)
                metadata[key] = value
        
        # Check if this is a container (has components) or shape (has mesh)
        components = obj.find(f'{ns}components')
        mesh = obj.find(f'{ns}mesh')
        
        if components is not None:
            # Container object
            component_ids = []
            for comp in components.findall(f'{ns}component'):
                comp_id = comp.get('objectid')
                if comp_id:
                    component_ids.append(comp_id)
            
            container_objects[obj_id] = {
                'name': obj_name,
                'metadata': metadata,
                'component_ids': component_ids
            }
            PrintFlow.debug(f"    Container with {len(component_ids)} components: {component_ids}")
            
        elif mesh is not None:
            # Shape object
            shape_objects[obj_id] = {
                'name': obj_name, 
                'metadata': metadata
            }
            PrintFlow.debug(f"    Shape object")
        
        # Store properties for this object
        if metadata:
            properties[obj_name] = metadata
    
    # Parse build section to see which objects are actually printed
    build = model_root.find(f'.//{ns}build')
    if build is not None:
        for item in build.findall(f'{ns}item'):
            build_id = item.get('objectid')
            if build_id:
                build_items.add(build_id)
        PrintFlow.debug(f"Build section references: {sorted(build_items)}")
    
    # Build structure mapping: container_name -> [shape_names]
    for obj_id, container in container_objects.items():
        if obj_id in build_items:
            # This container is in the build - map its components
            shape_names = []
            for comp_id in container['component_ids']:
                if comp_id in shape_objects:
                    shape_names.append(shape_objects[comp_id]['name'])
            
            structure[container['name']] = shape_names
            PrintFlow.debug(f"Container '{container['name']}' -> {shape_names}")
    
    # Add standalone shapes (not part of any container)
    for obj_id, shape in shape_objects.items():
        if obj_id in build_items:
            # This shape is directly in build section
            structure[shape['name']] = [shape['name']]
            PrintFlow.debug(f"Standalone shape '{shape['name']}' -> ['{shape['name']}']")
    
    return structure, properties

def analyze_3mf_structure(filename):
    """Analyze 3MF file structure and return object->volumes mapping."""
    try:
        import zipfile
        import xml.etree.ElementTree as ET

        with zipfile.ZipFile(filename, 'r') as zf:
            analysis_header = [
                f"=== 3MF FILE ANALYSIS: {filename} ===",
                f"3MF contents: {zf.namelist()}",
                "",
                "Main model XML (first 300 chars):"
            ]

            model_xml = zf.read('3D/3dmodel.model').decode('utf-8')
            model_root = ET.fromstring(model_xml)
            analysis_header.append(model_xml[:300])
            PrintFlow.debug('\n'.join(analysis_header))

            # Detect format by checking namespace in XML
            cura_namespace = 'xmlns:cura="http://software.ultimaker.com/xml/cura/3mf/2015/10"'
            slic3r_namespace = 'xmlns:slic3rpe="http://schemas.slic3r.org/3mf/2017/06"'
            
            is_cura_format = cura_namespace in model_xml
            is_slic3r_format = slic3r_namespace in model_xml
            
            if is_slic3r_format:
                # PrusaSlicer format - use external config file
                config_path = 'Metadata/Slic3r_PE_model.config'
                if config_path in zf.namelist():
                    config_xml = zf.read(config_path).decode('utf-8')
                    config_root = ET.fromstring(config_xml)
                    config_info = [
                        f"PrusaSlicer metadata found ({len(config_xml)} chars)",
                        "Config XML (first 500 chars):",
                        config_xml[:500]
                    ]
                    PrintFlow.debug('\n'.join(config_info))

                    structure, all_objects, all_volumes, _ = \
                        parse_prusaslicer_objects(config_root)

                    summary = [
                        "=== SUMMARY ===",
                        f"All objects found: {all_objects}",
                        f"All volumes found: {all_volumes}",
                        f"Final structure: {structure}",
                        "=== END 3MF ANALYSIS ==="
                    ]
                    PrintFlow.debug('\n'.join(summary))

                    properties = extract_slicer_properties(config_root)
                    PrintFlow.debug(f"All properties found: {properties}")

                    return structure, properties
                else:
                    PrintFlow.debug("PrusaSlicer namespace found but no config file")
                    return {}, {}
                    
            elif is_cura_format:
                # Cura format - parse embedded metadata from main XML
                PrintFlow.debug("Cura format detected - parsing container/component structure")
                structure, properties = parse_cura_objects(model_root)
                
                summary = [
                    "=== SUMMARY ===",
                    f"Final structure: {structure}",
                    "=== END 3MF ANALYSIS ==="
                ]
                PrintFlow.debug('\n'.join(summary))
                PrintFlow.debug(f"All properties found: {properties}")
                
                return structure, properties
                
            else:
                # Unknown or standard 3MF format
                PrintFlow.debug("No slicer-specific metadata found in 3MF")
                ns = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
                objects = model_root.findall(f'.//{ns}object')
                PrintFlow.debug(f"Found {len(objects)} objects in main model")
                for obj in objects:
                    obj_id = obj.get('id')
                    obj_type = obj.get('type', 'model')
                    PrintFlow.debug(f"  Object {obj_id}: type={obj_type}")
                return {}, {}

    except Exception as e:
        PrintFlow.debug(f"Error analyzing 3MF structure: {e}")
        import traceback
        PrintFlow.debug(f"Traceback: {traceback.format_exc()}")
        return {}, {}

def validate_test_document():
    """Validate that correct test document is active."""
    doc = FreeCAD.ActiveDocument
    if not doc:
        PrintFlow.debug("ERROR: No active document")
        return None

    if doc.Label != 'PrintFlowTest':
        PrintFlow.debug(f"ERROR: Wrong document active! Expected "
                          f"'PrintFlowTest', got '{doc.Label}'")
        PrintFlow.debug("Please open the PrintFlowTest document and "
                          "try again.")
        return None

    return doc

def setup_test_environment(doc, test_config):
    """Setup test environment with properties and selections."""
    if not revert_document(doc):
        PrintFlow.debug("CRITICAL ERROR: Could not establish reliable "
                          "TreeView state")
        return False
    PrintFlow.debug("Document successfully reverted with TreeView "
                      "confirmed available")

    PrintFlow.debug("Clearing all Export and test properties...")
    clear_all_export_properties(doc)
    clear_test_properties(doc)

    apply_export_settings(doc, test_config['export_settings'])

    if 'property_settings' in test_config:
        apply_property_settings(doc, test_config['property_settings'])

    return True

def apply_selection_override(doc, test_config):
    """Apply selection override if specified in test config."""
    import FreeCADGui as Gui
    Gui.Selection.clearSelection()

    selection_override = test_config.get('selection_override', [])
    if not selection_override:
        return

    selection_details = [
        "Applying selection override...",
        f"  Selecting objects: {selection_override}"
    ]

    selected_objects = []
    for obj_label in selection_override:
        objs = doc.getObjectsByLabel(obj_label)
        if objs:
            obj = objs[0]
            Gui.Selection.addSelection(obj)
            selected_objects.append(obj_label)
            selection_details.append(f"    Selected: {obj_label}")
        else:
            selection_details.append(f"    WARNING: Object {obj_label} "
                                     "not found")

    selection_details.extend([
        f"  Successfully selected: {selected_objects}",
        "  This will override Export property behavior"
    ])
    PrintFlow.debug('\n'.join(selection_details))

def print_test_configuration(doc, test_config):
    """Print current test configuration for verification."""
    export_objects = []
    for obj in doc.Objects:
        if hasattr(obj, 'Export') and obj.Export:
            export_objects.append(obj.Label)

    config_summary = [
        f"Objects with Export=True: {export_objects}"
    ]

    selection_override = test_config.get('selection_override', [])
    if selection_override:
        import FreeCADGui as Gui
        selected = Gui.Selection.getSelection()
        selected_labels = [obj.Label for obj in selected]
        config_summary.append(f"Objects selected in TreeView: "
                              f"{selected_labels}")
        config_summary.append("Selection will override Export properties")

    PrintFlow.debug('\n'.join(config_summary))

def get_key_objects_for_inspection(test_name, test_config, result):
    """Determine which objects to inspect in checkpoints."""
    key_objects = set()

    for obj_label in test_config['export_settings'].keys():
        key_objects.add(obj_label)

    for container_name, volumes in test_config['expected_structure'].items():
        key_objects.add(container_name)
        if isinstance(volumes, list):
            key_objects.update(volumes)

    selection_override = test_config.get('selection_override', [])
    if selection_override:
        key_objects.update(selection_override)
        if test_name == 'selection_link_descendant':
            key_objects.update(['Hex', 'Hex001', 'MultiObject'])
        elif test_name == 'selection_ineligible_boolean':
            key_objects.update(['Cut', 'Cylinder', 'Sphere'])

    if hasattr(result, 'objects'):
        actual_structure, _ = analyze_3mf_structure(TEST_3MF_PATH)
        for container_name, volumes in actual_structure.items():
            key_objects.add(container_name)
            if isinstance(volumes, list):
                key_objects.update(volumes)

    return sorted([obj for obj in key_objects if obj])

def execute_printflow_with_checkpoints(test_name, test_config):
    """Execute PrintFlow and handle checkpoint inspection."""
    PrintFlow.debug("Running PrintFlow main()...")
    try:
        result = PrintFlow.main(RunSlicer=False)
        PrintFlow.debug("PrintFlow main() completed successfully")

        key_objects = get_key_objects_for_inspection(test_name, test_config,
                                                     result)
        PrintFlow.debug(f"Key objects for checkpoint inspection: "
                          f"{key_objects}")

        if hasattr(result, 'inspect_checkpoints'):
            PrintFlow.debug("\n=== CHECKPOINT INSPECTION FOR KEY "
                              "OBJECTS ===")
            result.inspect_checkpoints(key_objects)

        return True
    except Exception as e:
        import traceback
        exception_details = [
            f"EXCEPTION in PrintFlow main(): {type(e).__name__}: {e}",
            "Exception traceback:"
        ]
        for line in traceback.format_exc().strip().split('\n'):
            exception_details.append(f"  {line}")
        exception_details.append("PrintFlow main() failed due to exception")
        PrintFlow.debug('\n'.join(exception_details))
        return False

def compare_test_results(test_name, test_config, temp_3mf):
    """Compare actual vs expected test results."""
    actual_structure, actual_properties = analyze_3mf_structure(temp_3mf)
    expected_structure = test_config['expected_structure']
    expected_properties = test_config.get('expected_properties', {})

    PrintFlow.debug(f"Expected structure: {expected_structure}")
    PrintFlow.debug(f"Actual structure: {actual_structure}")

    if expected_properties:
        PrintFlow.debug(f"Expected properties: {expected_properties}")
        PrintFlow.debug(f"Actual properties: {actual_properties}")

    def normalize_structure(structure):
        """Sort volume lists to ignore order differences."""
        return {obj: sorted(volumes) for obj, volumes in structure.items()}

    normalized_expected = normalize_structure(expected_structure)
    normalized_actual = normalize_structure(actual_structure)

    structure_match = (normalized_actual == normalized_expected)

    properties_match = True
    property_failures = []

    if expected_properties:
        for obj_name, expected_props in expected_properties.items():
            actual_props = actual_properties.get(obj_name, {})

            for prop_name, expected_value in expected_props.items():
                actual_value = actual_props.get(prop_name)

                if actual_value != expected_value:
                    properties_match = False
                    property_failures.append(f"{obj_name}.{prop_name}: "
                                            f"expected '{expected_value}', "
                                            f"got '{actual_value}'")

        if property_failures:
            PrintFlow.debug(f"Property failures: {property_failures}")

    if structure_match and properties_match:
        PrintFlow.debug(f"SUCCESS: Test {test_name} passed!")
        return True
    else:
        failure_details = [
            f"FAIL: Test {test_name} failed!"
        ]

        if not structure_match:
            failure_details.extend([
                f"  Structure mismatch:",
                f"    Expected: {expected_structure}",
                f"    Actual: {actual_structure}",
                f"    Expected (normalized): {normalized_expected}",
                f"    Actual (normalized): {normalized_actual}"
            ])

        if not properties_match:
            failure_details.extend([
                f"  Property mismatches:",
                f"    Expected: {expected_properties}",
                f"    Actual: {actual_properties}"
            ])
            for failure in property_failures:
                failure_details.append(f"    {failure}")

        PrintFlow.debug('\n'.join(failure_details))
        return False

def run_single_test(test_name, test_config):
    """Run a single test case."""
    header = [
        "=" * 60,
        f"RUNNING TEST: {test_name}",
        f"Description: {test_config['description']}",
        "=" * 60
    ]
    PrintFlow.debug('\n'.join(header))

    doc = validate_test_document()
    if not doc:
        return False

    if not setup_test_environment(doc, test_config):
        return False

    apply_selection_override(doc, test_config)
    print_test_configuration(doc, test_config)

    if not hasattr(doc, 'PrintFlowDebug'):
        doc.addProperty('App::PropertyInteger', 'PrintFlowDebug', 'PrintFlow')
    doc.PrintFlowDebug = 4
    
    # Set default document properties for clean test environment
    if not hasattr(doc, 'AppendVersion'):
        doc.addProperty('App::PropertyBool', 'AppendVersion', 'PrintFlow')
    doc.AppendVersion = False

    if not execute_printflow_with_checkpoints(test_name, test_config):
        return False

    if os.path.exists(TEST_3MF_PATH):
        PrintFlow.debug(f"SUCCESS: 3MF file created: {TEST_3MF_PATH}")
        result = compare_test_results(test_name, test_config, TEST_3MF_PATH)
        PrintFlow.debug(f"KEEPING 3MF FILE FOR DEBUGGING: {TEST_3MF_PATH}")
    else:
        PrintFlow.debug(f"FAIL: No 3MF file created at {TEST_3MF_PATH}")
        result = False

    import FreeCADGui as Gui
    Gui.Selection.clearSelection()

    test_result = [
        "=" * 60,
        f"TEST {test_name}: {'PASSED' if result else 'FAILED'}",
        "=" * 60
    ]
    PrintFlow.debug('\n'.join(test_result))

    return result

def run_test(test_names=None):
    """Run all tests defined in YAML."""
    import time

    suite_start_time = time.time()
    suite_header = [
        "=" * 60,
        "PrintFlow Test Suite - YAML-based",
        "=" * 60
    ]
    PrintFlow.debug('\n'.join(suite_header))


    # Test standalone TreeView function from PrintFlow
    PrintFlow.debug("Testing PrintFlow TreeView function...")
    try:
        tree = PrintFlow.get_document_tree_treeview()
        PrintFlow.debug(f"PrintFlow TreeView result: {len(tree)} parents")
        if 'Cup' in tree:
            PrintFlow.debug(f"PrintFlow: Cup has children {tree['Cup']}")
    except Exception as e:
        PrintFlow.debug(f"PrintFlow TreeView failed: {e}")

    # Parse test definitions
    test_data = parse_test_definitions()
    tests = test_data['tests']

    PrintFlow.debug(f"Found {len(tests)} test cases")

    # Run all tests to verify everything works
    if test_names is None:
        test_names = list(tests.keys())  # Run all tests

    PrintFlow.debug(f"Running {len(test_names)} specific test cases: "
                      f"{test_names}")
    results = {}
    test_num = 0
    total_tests = len(test_names)

    for test_name in test_names:
        if test_name in tests:
            test_num += 1
            test_start_time = time.time()
            PrintFlow.debug(f"Running test: {test_name}")
            test_result = run_single_test(test_name, tests[test_name])
            results[test_name] = test_result

            # Write progress marker with fixed-width formatting
            elapsed = time.time() - test_start_time
            status = "PASSED" if test_result else "FAILED"
            # Format: TESTPROG: NN/NN name(48chars) STATUS(8) TIME(7)
            test_name_truncated = test_name[:48].ljust(48)
            if len(test_name) > 48:
                test_name_truncated = test_name[:45] + "..."
                test_name_truncated = test_name_truncated.ljust(48)

            progress_line = (f"TESTPROG: {test_num:02d}/{total_tests:02d} "
                           f"{test_name_truncated} {status:>7} "
                           f"{elapsed:>6.1f}s")
            PrintFlow.debug(progress_line)
        else:
            PrintFlow.debug(f"Test {test_name} not found!")

    # Summary
    summary_header = [
        "=" * 60,
        "TEST SUITE SUMMARY",
        "=" * 60
    ]
    PrintFlow.debug('\n'.join(summary_header))

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        PrintFlow.debug(f"{test_name}: {status}")

    PrintFlow.debug(f"\nResults: {passed}/{total} tests passed")

    # Write completion marker
    suite_elapsed = time.time() - suite_start_time
    completion_line = (f"TESTDONE: {total}/{total} tests - "
                      f"{passed} PASSED, {total - passed} FAILED - "
                      f"{suite_elapsed:.1f}s total")
    PrintFlow.debug(completion_line)

    if passed == total:
        PrintFlow.debug("ALL TESTS PASSED!")
    else:
        PrintFlow.debug(f"{total - passed} tests failed")

def revert_document(doc, max_attempts=20):
    """Revert document and ensure TreeView is available.

    Keeps reverting until TreeView returns valid data or max_attempts reached.
    Returns True if TreeView is working, False if failed after max attempts.
    """
    import FreeCADGui as Gui
    from PySide import QtCore
    import time

    for attempt in range(1, max_attempts + 1):
        PrintFlow.debug(f"  Revert attempt {attempt}/{max_attempts}")

        # Perform document revert with aggressive GUI refresh
        doc.restore()
        doc.recompute()

        # Multiple rounds of GUI updates with delays
        for _ in range(3):
            Gui.updateGui()
            QtCore.QCoreApplication.processEvents()
            time.sleep(0.1)  # Small delay for GUI to catch up

        # Force TreeView refresh by triggering selection changes
        try:
            Gui.Selection.clearSelection()
            QtCore.QCoreApplication.processEvents()

            # Try to force TreeView update by collapsing/expanding doc node
            from PySide import QtGui
            tree_widget = Gui.getMainWindow().findChildren(
                QtGui.QTreeWidget)[0]
            root = tree_widget.invisibleRootItem()
            if root.childCount() > 0:
                doc_node = root.child(0)
                if doc_node:
                    # Collapse and expand to force refresh
                    tree_widget.collapseItem(doc_node)
                    QtCore.QCoreApplication.processEvents()
                    tree_widget.expandItem(doc_node)
                    QtCore.QCoreApplication.processEvents()
                    time.sleep(0.1)
        except:
            pass  # GUI refresh failed, continue anyway

        # Test TreeView availability
        try:
            tree = PrintFlow.get_document_tree_treeview(doc)
            root_children = tree.get(None, [])

            # Check if TreeView has reasonable structure (just need some objects)
            success = len(root_children) > 0

            if success:
                PrintFlow.debug(f"  SUCCESS on attempt {attempt}: TreeView "
                                  f"available with {len(root_children)} root "
                                  f"objects")
                return True
            else:
                PrintFlow.debug(f"  Attempt {attempt} failed: Only "
                                  f"{len(root_children)} root objects: "
                                  f"{root_children}")

        except Exception as e:
            PrintFlow.debug(f"  Attempt {attempt} exception: {e}")

    PrintFlow.debug(f"  FAILED: TreeView not available after "
                      f"{max_attempts} revert attempts")
    return False

def test_treeview_reliability(reverts=5, accesses_per_revert=4):
    """Test TreeView reliability with multiple reverts and accesses.

    Reverts document multiple times, then tests TreeView access multiple
    times after each revert to identify patterns.
    """
    reliability_header = [
        "=" * 80,
        f"TREEVIEW GROUPED TEST - {reverts} reverts x "
        f"{accesses_per_revert} accesses = "
        f"{reverts * accesses_per_revert} total tests",
        "=" * 80
    ]
    PrintFlow.debug('\n'.join(reliability_header))

    doc = FreeCAD.ActiveDocument
    if not doc or doc.Label != 'PrintFlowTest':
        PrintFlow.debug("ERROR: Need PrintFlowTest document active")
        return

    all_results = []

    for revert_num in range(1, reverts + 1):
        PrintFlow.debug(f"REVERT {revert_num}/{reverts}: Ensuring "
                          f"TreeView is available...")

        try:
            # Use robust revert function
            if not revert_document(doc):
                PrintFlow.debug(f"  ERROR: Could not get TreeView working "
                                  f"for revert {revert_num}")
                # Still continue with tests to record the failure pattern

            PrintFlow.debug(f"  TreeView ready. Now testing access "
                              f"{accesses_per_revert} times...")

            revert_results = []

            for access_num in range(1, accesses_per_revert + 1):
                test_num = (revert_num - 1) * accesses_per_revert + access_num
                PrintFlow.debug(f"    Test {test_num}: Revert {revert_num}, "
                                  f"Access {access_num}")
                try:
                    # Test TreeView access
                    tree = PrintFlow.get_document_tree_treeview(doc)
                    root_children = tree.get(None, [])

                    # Check if TreeView has expected structure
                    expected_objects = {'Hex', 'Cup', 'MultiObject',
                                       'ExportGroup', 'Array', 'Assembly'}
                    found_objects = set(root_children)

                    success = (len(root_children) >= 6 and
                              expected_objects.issubset(found_objects))

                    result = {
                        'test_num': test_num,
                        'revert_num': revert_num,
                        'access_num': access_num,
                        'success': success,
                        'root_children_count': len(root_children),
                        'root_children': root_children,
                        'total_parents': len(tree),
                        'missing_objects': list(expected_objects -
                                                found_objects) if not
                                                success else []
                    }
                    revert_results.append(result)
                    all_results.append(result)

                    status = "SUCCESS" if success else "FAILURE"
                    PrintFlow.debug(f"      {status}: "
                                      f"{len(root_children)} root "
                                      f"objects: {root_children}")
                    if not success:
                        PrintFlow.debug(f"        Missing: "
                                          f"{expected_objects - found_objects}")

                except Exception as e:
                    result = {
                        'test_num': test_num,
                        'revert_num': revert_num,
                        'access_num': access_num,
                        'success': False,
                        'error': str(e),
                        'exception_type': type(e).__name__
                    }
                    revert_results.append(result)
                    all_results.append(result)
                    PrintFlow.debug(f"      ERROR: Exception during "
                                      f"TreeView access: {e}")

            # Summary for this revert
            revert_successes = sum(1 for r in revert_results if r['success'])
            PrintFlow.debug(f"  REVERT {revert_num} SUMMARY: "
                              f"{revert_successes}/{accesses_per_revert} "
                              f"successes")

        except Exception as e:
            PrintFlow.debug(f"  ERROR: Exception during revert {revert_num}: {e}")

    # Overall analysis
    total_tests = reverts * accesses_per_revert
    total_successes = sum(1 for r in all_results if r['success'])
    total_failures = total_tests - total_successes
    success_rate = (total_successes / total_tests) * 100

    summary = [
        "=" * 80,
        "TREEVIEW GROUPED TEST RESULTS",
        "=" * 80,
        f"Total tests: {total_tests}",
        f"Successes: {total_successes}",
        f"Failures: {total_failures}",
        f"Overall success rate: {success_rate:.1f}%",
        ""
    ]

    # Results by revert group
    summary.append("RESULTS BY REVERT GROUP:")
    for revert_num in range(1, reverts + 1):
        revert_tests = [r for r in all_results if r['revert_num'] == revert_num]
        revert_successes = sum(1 for r in revert_tests if r['success'])
        summary.append(f"  Revert {revert_num}: {revert_successes}"
                       f"/{accesses_per_revert} successes")

        for result in revert_tests:
            status = "SUCCESS" if result['success'] else "FAILURE"
            children = result.get('root_children_count', 0)
            summary.append(f"    Access {result['access_num']}: "
                           f"{status} ({children} root objects)")
    summary.append("")

    # Pattern analysis
    summary.append("PATTERN ANALYSIS:")

    # Success patterns by access number
    access_stats = {}
    for access_num in range(1, accesses_per_revert + 1):
        access_tests = [r for r in all_results if r['access_num'] == access_num]
        access_successes = sum(1 for r in access_tests if r['success'])
        access_stats[access_num] = {
            'successes': access_successes,
            'total': len(access_tests),
            'rate': ((access_successes / len(access_tests)) *
                     100 if access_tests else 0)
        }
        summary.append(f"  Access #{access_num}: {access_successes}/"
                       f"{len(access_tests)} successes "
                       f"({access_stats[access_num]['rate']:.1f}%)")

    summary.extend([
        "",
        "=" * 80,
        ""
    ])

    PrintFlow.debug('\n'.join(summary))
    return all_results

if __name__ == "__main__":
    # CRITICAL SAFETY CHECK: Ensure we have the correct test document
    # NEVER REMOVE THIS - prevents accidentally running tests on wrong
    # document
    doc = FreeCAD.ActiveDocument
    if not doc or doc.Label != 'PrintFlowTest':
        print(f"ERROR: Wrong document active! Expected 'PrintFlowTest', "
              f"got '{doc.Label if doc else 'None'}'")
        print("Please open the PrintFlowTest document and try again.")
    else:
        # Add startup logging messages
        print('(re)loaded PrintFlow from PrintFlowTest macro')
        print(f"Test directory: {TEST_DIR}")
        print(f"Test 3MF path: {TEST_3MF_PATH}")
        
        # Check for test selection file
        test_selection_file = os.path.join(TEST_DIR, 'test_selection.tmp')
        selected_tests = None
        
        try:
            if os.path.exists(test_selection_file):
                with open(test_selection_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        selected_tests = [line.strip() for line in content.split('\n') if line.strip()]
                        PrintFlow.log(f"Running selected tests: {selected_tests}")
                    else:
                        PrintFlow.log("Test selection file is empty, running all tests")
            else:
                PrintFlow.log("No test selection file found, running all tests")
        except Exception as e:
            PrintFlow.warn(f"Could not read test selection file: {e}")
            PrintFlow.log("Running all tests due to file read error")
        
        # Run tests
        try:
            run_test(selected_tests)
        except Exception as e:
            import traceback
            exception_details = [
                f"EXCEPTION in test suite: {type(e).__name__}: {e}",
                "Exception traceback:"
            ]
            for line in traceback.format_exc().strip().split('\n'):
                exception_details.append(f"  {line}")
            exception_details.append("Test suite failed due to exception")
            for line in exception_details:
                print(line)
        finally:
            cleanup_printflow_import()
