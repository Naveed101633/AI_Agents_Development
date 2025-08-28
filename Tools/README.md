**🛠️ Tools in OpenAI Agents SDK**

Tools let agents take real-world actions: fetching data, running code, calling APIs, and even using other agents.
They’re what make agents more than just chatbots — they become problem-solvers.

The Agents SDK supports three main classes of tools:

1. Hosted Tools → run on LLM servers (retrieval, web search, computer use).

2. Function Calling → turn any Python function into a tool automatically.

3. Agents as Tools → let agents call other agents.

**📌 Function Tools**

Function tools are the most flexible:

1. The tool name comes from the function name (or you can override).
2. The description comes from the docstring (or you can override).
3. The schema for inputs is generated automatically from the function signature.
4. Argument descriptions are parsed from the docstring.

**⚠️ What if the tool fails?**
In the real world, tools fail all the time due to:

- API timeouts
- Bad credentials
- Invalid input
- Server not reachable
- Bugs in the code
That’s why failure_error_function exists — so your agent doesn’t crash when a tool fails.


| Name                     | Type              | Description                                     | Default                       |
| ------------------------ | ----------------- | ----------------------------------------------- | ----------------------------- |
| `func`                   | ToolFunction      | Function to wrap as tool                        | None                          |
| `name_override`          | str               | Custom tool name instead of function name       | None                          |
| `description_override`   | str               | Custom description instead of docstring         | None                          |
| `docstring_style`        | DocstringStyle    | Force a docstring style                         | Auto-detect                   |
| `use_docstring_info`     | bool              | Use docstring for tool + arg descriptions       | True                          |
| `failure_error_function` | ToolErrorFunction | Custom error handler for tool failure           | `default_tool_error_function` |
| `strict_mode`            | bool              | Enforce strict JSON schema for input validation | True                          |
| `is_enabled`             | bool / Callable   | Whether the tool is enabled at runtime          | True                          |
