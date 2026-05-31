"""Custom smolagents tools for filesystem operations."""

from smolagents import Tool


class ReadFileTool(Tool):
    name = "read_file"
    description = "Read a file from the filesystem and return its contents"
    inputs = {"path": {"type": "string", "description": "Path to the file to read"}}
    output_type = "string"

    def forward(self, path: str) -> str:
        import pathlib
        return pathlib.Path(path).read_text()


class WriteFileTool(Tool):
    name = "write_file"
    description = "Write content to a file on the filesystem"
    inputs = {
        "path": {"type": "string", "description": "Path to write to"},
        "content": {"type": "string", "description": "Content to write"}
    }
    output_type = "string"

    def forward(self, path: str, content: str) -> str:
        import pathlib
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(path).write_text(content)
        return f"Written to {path}"


class SearchFilesTool(Tool):
    name = "search_files"
    description = "Search for files matching a glob pattern"
    inputs = {"pattern": {"type": "string", "description": "Glob pattern to match"}}
    output_type = "string"

    def forward(self, pattern: str) -> str:
        import pathlib
        results = list(pathlib.Path().glob(pattern))
        return "\n".join(str(r) for r in results) if results else "No files found."
