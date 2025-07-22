# Points to consider in MCP Server

- MCP Server extends the functionality of LLMs by providing information to improve outputs or ways to perform actions.
- Inpsector is a React Based client to test MCP server configuration.
  - It does not use LLM, allowing developer to save tokens and just focus on request and response parameters. 
- Claude Desktop is also a simpler way to configure and test MCP server during testing, however it consumes LLM tokens during testing.
- VSCode can also be used to test MCP server, it also uses LLM tokens but provides a bit more control over testing functionality then Claude Code.
- My Recommendation is to use Inspector during development / unit testing and Claude Code for integration testing.
- ***Note*** Be very careful when adding any MCP server and only add which you trust completely.
