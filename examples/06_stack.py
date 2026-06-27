"""Stack — Last In, First Out (LIFO). A pattern, not a type. Just use a list.

Run me:  uv run python learn/examples/06_stack.py
"""


def basic_stack() -> None:
    stack: list[str] = []
    stack.append("page1")     # push — O(1)
    stack.append("page2")
    stack.append("page3")
    print("stack:", stack)
    print("pop  :", stack.pop())   # "page3" — last in, first out
    print("pop  :", stack.pop())   # "page2"
    print("stack:", stack)


def browser_back_button() -> None:
    """A stack is literally how the browser back button works."""
    history: list[str] = []
    for page in ["home", "search", "product", "checkout"]:
        history.append(page)
        print(f"visit {page!r:12} -> history {history}")
    print("\npress BACK:")
    while history:
        print(f"  back to {history.pop()!r}")


def balanced_parentheses(s: str) -> bool:
    """Classic interview question — stacks are the natural tool for matching pairs."""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack            # leftover opens => unbalanced


if __name__ == "__main__":
    print("== basic stack =="); basic_stack()
    print("\n== browser back button =="); browser_back_button()
    print("\n== balanced parentheses ==")
    for test in ["(a[b]{c})", "(]", "((("]:
        print(f"  {test!r:12} -> {balanced_parentheses(test)}")
