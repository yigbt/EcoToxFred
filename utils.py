import yaml

def get_version() -> str:
    try:
        with open("values.yaml") as f:
            data = yaml.safe_load(f)
            return data["ecotoxfred"]["image"]["tag"]
    except FileNotFoundError:
        print("Error: File 'values.yaml' not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return "no version info"

