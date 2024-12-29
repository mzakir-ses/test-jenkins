def greet(name: str) -> str:
    return f"Hello, {name}!"

def test_code(val):
    value = val + val  # Fix the typo here
    print("The value is", value)

def test_code_two(val):
    value = val + val  # Fix the typo here
    print("calculated value", value)

def test_code_three(val):
    value = val + val  # Fix the typo here
    print("last calculation", value)

if __name__ == "__main__":
    print(greet("World"))
    test_code(5) 
