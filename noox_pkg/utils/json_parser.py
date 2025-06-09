import json
import os

def load_apps_from_json(filepath: str) -> dict | None:
    """
    Loads application names and URLs from a JSON file.

    Args:
        filepath: Path to the JSON file.

    Returns:
        A dictionary of {app_name: url} if successful, None otherwise.
    """
    if not os.path.exists(filepath):
        print(f"Error: JSON file not found at {filepath}")
        return None

    try:
        with open(filepath, 'r') as f:
            content = f.read()
            # Handle empty file case before json.loads
            if not content.strip():
                print(f"Error: JSON file is empty at {filepath}")
                return None
            data = json.loads(content)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")
        return None
    except Exception as e: # Catch other potential file reading errors
        print(f"Error reading file {filepath}: {e}")
        return None

    if not isinstance(data, dict):
        print("Error: JSON root must be an object/dictionary")
        return None

    validated_apps = {}
    for key, value in data.items():
        if not isinstance(key, str):
            print(f"Error: App name (JSON key) must be a string. Found: {key} (type: {type(key).__name__})")
            return None

        app_name = key

        if not isinstance(value, str):
            print(f"Error: App URL (JSON value) must be a string for app '{app_name}'. Found: {value} (type: {type(value).__name__})")
            return None

        url = value

        if not (url.startswith('http://') or url.startswith('https://')):
            print(f"Warning: URL for app '{app_name}' does not look valid: {url}")

        validated_apps[app_name] = url

    return validated_apps

if __name__ == '__main__':
    # --- Test Cases ---
    def create_test_file(filename, content):
        with open(filename, 'w') as f:
            f.write(content)
        print(f"\nCreated test file: {filename}")

    # Test 1: Valid JSON
    create_test_file("test_valid.json", '''
{
  "AppName1": "http://example.com/download1",
  "AppName2": "https://othersite.org/app.zip",
  "AppWithOddUrl": "ftp://another.com/file"
}
    ''')
    result = load_apps_from_json("test_valid.json")
    print(f"Result for test_valid.json: {result}")
    assert result is not None
    assert result["AppName1"] == "http://example.com/download1"
    assert "ftp://another.com/file" in result.values()


    # Test 2: File not found
    print("\nTesting non_existent_file.json:")
    result = load_apps_from_json("non_existent_file.json")
    print(f"Result for non_existent_file.json: {result}")
    assert result is None

    # Test 3: Invalid JSON format (e.g., trailing comma)
    create_test_file("test_invalid_format.json", '''
{
  "AppName1": "http://example.com/download1",
  "AppName2": "https://othersite.org/app.zip",
}
    ''') # Trailing comma makes it invalid
    result = load_apps_from_json("test_invalid_format.json")
    print(f"Result for test_invalid_format.json: {result}")
    assert result is None

    # Test 4: Root is not a dictionary
    create_test_file("test_not_dict.json", '''
[
  {"AppName1": "http://example.com/download1"}
]
    ''')
    result = load_apps_from_json("test_not_dict.json")
    print(f"Result for test_not_dict.json: {result}")
    assert result is None

    # Test 5: Key is not a string
    # create_test_file("test_invalid_key.json", '''
    # {
    #  123: "http://example.com/download1"
    # }
    # ''') # Technically, json.loads converts numeric keys in objects to strings.
         # However, if the JSON was constructed in a way that a non-string key
         # was forced (e.g. via Python dict with int key then dumped),
         # this tests the explicit isinstance check.
         # Standard JSON requires keys to be strings.
    # Let's make a json that is valid but our stricter check should catch
    # For example, if a non-string key was somehow loaded by json if it wasn't pure json spec
    # but python dict conversion. json.loads actually makes keys strings.
    # So this test case as written for `json.loads` behavior is tricky.
    # The `isinstance(key, str)` check is more of a safeguard.
    # Standard JSON parsers should enforce string keys.
    # Let's assume for now json.loads always gives string keys from valid JSON.
    # The check is there for robustness.
    # To truly test this, we'd need a dict `d = {123: "url"}` and then `json.dumps(d)`
    # which results in `{"123": "url"}`. So `json.loads` will always make the key a string.
    # The check `isinstance(key, str)` will thus always pass if `json.loads` succeeds with an object.
    # This test case might be more relevant if the input `data` came from a non-JSON source.
    # For now, we'll assume standard JSON behavior.
    # print("\nSkipping direct test for non-string key as json.loads stringifies numeric keys.")
    # Test for non-string key is skipped as json.loads stringifies numeric keys from valid JSON.

    # Test 6: Value is not a string
    create_test_file("test_invalid_value.json", '''
{
  "AppName1": 12345
}
    ''')
    result = load_apps_from_json("test_invalid_value.json")
    print(f"Result for test_invalid_value.json: {result}")
    assert result is None

    # Test 7: URL doesn't start with http/https (Warning)
    create_test_file("test_bad_url_format.json", '''
{
  "AppNameFtp": "ftp://example.com/download.zip",
  "AppNameNoScheme": "example.com/file"
}
    ''')
    result = load_apps_from_json("test_bad_url_format.json")
    print(f"Result for test_bad_url_format.json: {result}")
    assert result is not None
    assert "AppNameFtp" in result
    assert "AppNameNoScheme" in result

    # Test 8: Empty JSON file
    create_test_file("test_empty.json", "")
    result = load_apps_from_json("test_empty.json")
    print(f"Result for test_empty.json: {result}")
    assert result is None

    # Test 9: JSON file with only whitespace
    create_test_file("test_whitespace.json", "   \n\t   ")
    result = load_apps_from_json("test_whitespace.json")
    print(f"Result for test_whitespace.json: {result}")
    assert result is None

    print("\nAll local tests for json_parser.py completed.")

    # Clean up test files
    os.remove("test_valid.json")
    os.remove("test_invalid_format.json")
    os.remove("test_not_dict.json")
    # os.remove("test_invalid_key.json") # File not created as test is skipped
    os.remove("test_invalid_value.json")
    os.remove("test_bad_url_format.json")
    os.remove("test_empty.json")
    os.remove("test_whitespace.json")
    print("Cleaned up test files.")
