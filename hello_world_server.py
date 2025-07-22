"""
Minimal hello world server

To test this server:
- "test MCP"
- "say hello"
- "are you working?"
"""

from mcp.server.fastmcp import FastMCP

# create a server instance
mcp = FastMCP("hello-world")


## Tool registry
@mcp.tool()
def health_check(ping: str) -> str:
	"""health check endpoint"""
	return "Health is Ok!"


## Dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
	"""get a personalized greeting"""
	return f"Hello {name}!"


## Runner
if __name__ == "__main__":
	mcp.run()
