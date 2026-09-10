"""
VARUNA Dynamic Tool Registry
Provides declarative tool registration, schema discovery, and autonomous invocation
for the Master Orchestrator Agent.
"""

from typing import Dict, Any, Callable, List, Optional
import inspect

class ToolRegistry:
    """
    Registry for tools that sub-agents and the Master Orchestrator can dynamically invoke.
    """

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, description: str, category: str = "GENERAL"):
        """Decorator to register a tool function with metadata."""
        def decorator(func: Callable):
            sig = inspect.signature(func)
            params = {
                param_name: {
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                    "default": param.default if param.default != inspect.Parameter.empty else None,
                    "required": param.default == inspect.Parameter.empty
                }
                for param_name, param in sig.parameters.items()
            }
            self._tools[name] = {
                "name": name,
                "description": description,
                "category": category,
                "func": func,
                "parameters": params,
                "doc": inspect.getdoc(func) or description
            }
            return func
        return decorator

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        return self._tools.get(name)

    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        tools = []
        for t in self._tools.values():
            if category is None or t["category"] == category:
                tools.append({
                    "name": t["name"],
                    "description": t["description"],
                    "category": t["category"],
                    "parameters": t["parameters"]
                })
        return tools

    def invoke(self, name: str, **kwargs) -> Any:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' is not registered in ToolRegistry.")
        tool_entry = self._tools[name]
        func = tool_entry["func"]
        return func(**kwargs)

# Global tool registry singleton
tool_registry = ToolRegistry()
