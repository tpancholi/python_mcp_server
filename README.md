# MCP Server using Python

## Requirements
- mcp[cli]

## To run the server

### Run dev server to test using [inspector](https://github.com/modelcontextprotocol/inspector)

```commandline
uv run mcp dev server.py
```

**Note:** inspector is not required to be installed separately

### Run server to test using Claude Code

```commandline
uv run mcp install server.py
```

**Note:** 
- you would need to restart the Claude Code for the updated config to reflect
- you would also need to manually remove the server from the development tab under setting, else the server would keep running in the background.
