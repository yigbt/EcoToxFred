def parse_write_todos_result(command_result):
    """
    Parse the result of a WriteTodos tool call and extract structured todo information.

    Args:
        command_result: Command object containing 'update' dict with 'todos' list

    Returns:
        dict: Structured todo information with the following keys:
            - 'todos': list of todo items
            - 'completed': list of completed todos
            - 'in_progress': list of todos currently in progress
            - 'pending': list of pending todos
            - 'total_count': total number of todos
            - 'completed_count': number of completed todos
            - 'in_progress_count': number of in-progress todos
            - 'pending_count': number of pending todos
    """
    # Extract todos from the command result
    todos = []
    if hasattr(command_result, 'update') and 'todos' in command_result.update:
        todos = command_result.update['todos']
    elif isinstance(command_result, dict) and 'update' in command_result:
        todos = command_result['update'].get('todos', [])
    elif isinstance(command_result, dict) and 'todos' in command_result:
        todos = command_result['todos']

    # Categorize todos by status
    completed = [todo for todo in todos if todo.get('status') == 'completed']
    in_progress = [todo for todo in todos if todo.get('status') == 'in_progress']
    pending = [todo for todo in todos if todo.get('status') == 'pending']

    return {
        'todos': todos,
        'completed': completed,
        'in_progress': in_progress,
        'pending': pending,
        'total_count': len(todos),
        'completed_count': len(completed),
        'in_progress_count': len(in_progress),
        'pending_count': len(pending)
    }


def format_todos_for_display(parsed_todos, include_completed=True):
    """
    Format parsed todos into a human-readable string for display.

    Args:
        parsed_todos (dict): Output from parse_write_todos_result()
        include_completed (bool): Whether to include completed tasks in the output

    Returns:
        str: Formatted markdown string of todos
    """
    lines = []

    # Add summary

    # Add in-progress todos
    if parsed_todos['in_progress']:
        for todo in parsed_todos['in_progress']:
            lines.append(f"✏️ {todo['content']}\n")

    # Add pending todos
    if parsed_todos['pending']:
        for todo in parsed_todos['pending']:
            lines.append(f"☐ {todo['content']}\n")

    # Add completed todos if requested
    if include_completed and parsed_todos['completed']:
        for todo in parsed_todos['completed']:
            lines.append(f"✅ {todo['content']}\n")

    return "\n".join(lines)
