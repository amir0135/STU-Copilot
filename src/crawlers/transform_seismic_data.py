#!/usr/bin/env python3
"""
Script to transform currentPageDocs JSON data to match SeismicContent data model.
Flattens the structure and maps fields appropriately.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the parent directory to the path to import data_models
sys.path.append(str(Path(__file__).parent))
from data_models import SeismicContent


def extract_custom_property_value(custom_properties: List[Dict], property_name: str) -> str:
    """Extract value from custom properties array by property name."""
    for prop in custom_properties:
        if prop.get('name') == property_name:
            values = prop.get('values', [])
            if values:
                # Join multiple values with comma
                return ', '.join([v.get('value', '') for v in values if v.get('value')])
    return ''


def safe_get_nested(data: Dict, path: str, default: Any = '') -> Any:
    """Safely get nested dictionary value using dot notation."""
    try:
        keys = path.split('.')
        result = data
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key, default)
            else:
                return default
        return result if result is not None else default
    except (KeyError, TypeError, AttributeError):
        return default


def transform_seismic_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a single currentPageDocs item to SeismicContent format."""
    
    # Get original model data
    original_model = doc.get('originalModel', {})
    custom_properties = original_model.get('CustomProperties', [])
    
    # Extract basic information
    content_id = safe_get_nested(doc, 'contentId') or safe_get_nested(original_model, 'ContentId')
    name = safe_get_nested(doc, 'name') or safe_get_nested(original_model, 'Name')
    url = safe_get_nested(doc, 'urllink') or safe_get_nested(doc, 'openLink', '')
    
    # Extract version information
    version = safe_get_nested(doc, 'version', '1.0')
    version_creation_date = safe_get_nested(original_model, 'VersionCreatedDate') or safe_get_nested(doc, 'originVersionCreatedDate', '')
    publish_date = safe_get_nested(original_model, 'PublishTime') or safe_get_nested(doc, 'originPublishTime', '')
    creation_date = safe_get_nested(original_model, 'CreateTime') or safe_get_nested(doc, 'originCreateTime', '')
    expiration_date = safe_get_nested(original_model, 'ExpirationDate') or safe_get_nested(doc, 'originExpirationDate', '')
    
    # Extract description
    description = safe_get_nested(doc, 'description') or safe_get_nested(original_model, 'Description', '')
    
    # Extract file information
    size = safe_get_nested(doc, 'formatSize', '')
    format_type = safe_get_nested(doc, 'format') or safe_get_nested(original_model, 'Format', '')
    
    # Extract custom properties
    confidentiality = extract_custom_property_value(custom_properties, 'Confidentiality')
    sales_stage = extract_custom_property_value(custom_properties, 'Sales Stage')
    audience = extract_custom_property_value(custom_properties, 'Audience')
    competitor = extract_custom_property_value(custom_properties, 'Competitor')
    level = extract_custom_property_value(custom_properties, 'Level')
    language = extract_custom_property_value(custom_properties, 'Language')
    industry = extract_custom_property_value(custom_properties, 'Industry')
    initiative = extract_custom_property_value(custom_properties, 'Initiative')
    segment = extract_custom_property_value(custom_properties, 'Segment')
    content_sub_type = extract_custom_property_value(custom_properties, 'Content Sub-Type')
    industry_sub_vertical = extract_custom_property_value(custom_properties, 'Industry Sub-Vertical')
    solution_area = extract_custom_property_value(custom_properties, 'Solution Area')
    content_group = extract_custom_property_value(custom_properties, 'Content Group')
    products = extract_custom_property_value(custom_properties, 'Products')
    solution_play = extract_custom_property_value(custom_properties, 'Solution Play')
    industry_vertical = extract_custom_property_value(custom_properties, 'Industry Vertical')
    
    # Create the flattened record
    return {
        "id": content_id,
        "name": name,
        "url": url,
        "version": version,
        "version_creation_date": version_creation_date,
        "publish_date": publish_date,
        "creation_date": creation_date,
        "expiration_date": expiration_date,
        "description": description,
        "size": size,
        "format": format_type,
        "confidentiality": confidentiality,
        "sales_stage": sales_stage or "--",
        "audience": audience,
        "competitor": competitor or "--",
        "level": level,
        "language": language,
        "industry": industry or "--",
        "initiative": initiative or "--",
        "segment": segment,
        "content_sub_type": content_sub_type,
        "industry_sub_vertical": industry_sub_vertical or "--",
        "solution_area": solution_area,
        "content_group": content_group,
        "products": products or "--",
        "solution_play": solution_play or "--",
        "industry_vertical": industry_vertical or "--",
        "tags": None,
        "embedding": None
    }


def transform_currentpage_docs_json(input_file: str, output_file: str) -> None:
    """Transform currentPageDocs JSON to flattened SeismicContent format."""
    
    print(f"🔄 Transforming {input_file} to SeismicContent format...")
    
    # Read input JSON
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File {input_file} not found")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {input_file}: {e}")
        return
    
    # Extract currentPageDocs array
    current_page_docs = data.get('currentPageDocs', [])
    if not current_page_docs:
        print("❌ Error: No 'currentPageDocs' found in JSON")
        return
    
    print(f"📄 Processing {len(current_page_docs)} documents...")
    
    # Transform each document
    transformed_docs = []
    for i, doc in enumerate(current_page_docs):
        try:
            transformed_doc = transform_seismic_document(doc)
            transformed_docs.append(transformed_doc)
            print(f"✅ Processed document {i+1}: {transformed_doc.get('name', 'Unknown')}")
        except Exception as e:
            print(f"⚠️  Error processing document {i+1}: {e}")
            continue
    
    # Write output JSON (flat array)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transformed_docs, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Successfully transformed {len(transformed_docs)} documents")
        print(f"📁 Output saved to: {output_file}")
        
        # Display sample of first record
        if transformed_docs:
            print("\n📋 Sample record:")
            sample = transformed_docs[0]
            for key, value in list(sample.items())[:10]:  # Show first 10 fields
                print(f"   {key}: {value}")
            if len(sample) > 10:
                print(f"   ... and {len(sample) - 10} more fields")
                
    except Exception as e:
        print(f"❌ Error writing output file: {e}")


def validate_against_model(records: List[Dict]) -> None:
    """Validate transformed records against SeismicContent model."""
    print(f"\n🔍 Validating {len(records)} records against SeismicContent model...")
    
    errors = []
    for i, record in enumerate(records):
        try:
            # Try to create SeismicContent instance
            seismic_content = SeismicContent.from_dict(record)
            # Convert back to dict to test serialization
            seismic_content.to_dict()
        except Exception as e:
            errors.append(f"Record {i+1} ({record.get('name', 'Unknown')}): {e}")
    
    if errors:
        print(f"⚠️  Found {len(errors)} validation errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"   - {error}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more errors")
    else:
        print("✅ All records validated successfully!")


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 3:
        print("Usage: python transform_seismic_data.py <input_json> <output_json>")
        print("Example: python transform_seismic_data.py currentPageDocs.json seismic_content.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Transform the data
    transform_currentpage_docs_json(input_file, output_file)
    
    # Validate the output
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        validate_against_model(records)
    except Exception as e:
        print(f"⚠️  Could not validate output: {e}")


if __name__ == "__main__":
    main()