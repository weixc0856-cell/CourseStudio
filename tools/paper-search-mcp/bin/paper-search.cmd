@echo off
rem Project-local launcher for paper-search (isolated venv + project config).
setlocal
if "%PAPER_SEARCH_MCP_ENV_FILE%"=="" set "PAPER_SEARCH_MCP_ENV_FILE=D:\CourseStudio\.config\paper-search-mcp\.env"
"%~dp0..\.venv\Scripts\paper-search.exe" %*
