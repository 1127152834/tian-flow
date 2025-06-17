#!/usr/bin/env python3
"""
Test get_training_examples tool
"""
import json
from src.tools.text2sql_tools import get_training_examples

def test_training_examples():
    """Test get_training_examples tool"""
    try:
        print("=== Testing get_training_examples tool ===")
        
        # Test with limit 100 to get more datasources
        result = get_training_examples.invoke({'limit': 100})
        result_data = json.loads(result)
        
        print(f"Success: {result_data.get('success')}")
        print(f"Message: {result_data.get('message')}")
        
        if result_data.get('success') and result_data.get('data'):
            examples = result_data['data']['examples']
            print(f"Total examples: {len(examples)}")
            
            # Group by datasource_id
            datasource_groups = {}
            for example in examples:
                datasource_id = example.get('datasource_id', 'unknown')
                if datasource_id not in datasource_groups:
                    datasource_groups[datasource_id] = []
                datasource_groups[datasource_id].append(example)
            
            print("\n=== Datasource Distribution ===")
            for ds_id, group in datasource_groups.items():
                print(f"  数据源 {ds_id}: {len(group)} 个示例")
                
                # Show first example
                if group:
                    first_example = group[0]
                    content_preview = first_example.get('question') or first_example.get('content', 'N/A')
                    if len(content_preview) > 50:
                        content_preview = content_preview[:50] + "..."
                    print(f"    示例: {first_example.get('content_type', 'N/A')} - {content_preview}")
        else:
            print(f"Error: {result_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_training_examples()
