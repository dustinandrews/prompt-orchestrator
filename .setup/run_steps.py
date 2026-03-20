# Program to read the steps.yaml file and execute each command

class Command:
    """Example of the structure of the steps.yaml command
  - command: "/speckit.specify"
    model: "moonshotai/kimi-k2-turbo-preview"
    files:
      - ".opencode/command/speckit.specify.md"
      - ".specify/templates/spec-template.md"
      - "userspec.md"
    """
    def __init__(self, command: object):
        self.command = command.get("command")
        self.model = command.get("model")
        self.files = command.get("files", [])


class OpenCodeExecutor:

    def __init__(self):
        
        data = parse_yaml()
        self.commands = [Command(cmd) for cmd in data.get("commands", [])]
        project_name = data.get("title", "Unnamed Project")
        log_level = data.get("log_level", "INFO")
        message = data.get("message", "")
        pass

    def parse_yaml(self):
        # check for ./steps.yaml and parse it, raise error if not found or invalid
        yaml_path = "steps.yaml"
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")
        # Implement logic to parse the YAML file and extract commands, models, and files.
        print(f"Parsing YAML file: {yaml_path}")
        # return an object with the structure of the YAML file 'steps.yaml'
        return obj

    def execute_command(self, command: str, model: str = None, files: list = None):
        # Here you would implement the logic to execute the command, 
        # possibly using subprocess to call the OpenCode CLI with the appropriate arguments.
        print(f"Executing command: {command} ", end="")
        if model:
            print(f"Using model: {model} ",end="")
        if files:
            print(f"Including files: {files}",end="")
        print()  # Print a newline after all the information
        # execute using subprocess. Each file gets passed with it's own -f flag
        # opencode run --log-level INFO -f userspec.md -f .opencode/command/speckit.specify.md -f .specify/templates/spec-template.md --model moonshotai/kimi-k2-turbo-preview "K.I.S.S. DO NOT ask clarifying questions. Make decisions and proceed."

    def verify_files(self, files: list):
        # Implement logic to check if the required files are present in the expected locations.
        print(f"Verifying presence of files: {files}")
        # raise file not found error if any file is missing
`
    def verify_implmentation(self):
        """
        .
        ├── pyproject.toml
        ├── README.md
        ├── requirements.txt
        ├── src
        │   ├── cli.py
        │   ├── __init__.py
        │   └── main.py
        └── tests
            ├── test_cli.py
            └── test_main.py

        Implement logic to check that the implementation files (e.g., src/) are filled in and not just stubs.
        """
        # ensure all the {{...}} placeholders are filled in
        # raise error and bail if any placeholders are found in the implementation files (e.g., src/)
`
    def run(self):
        for cmd in self.commands:
            if cmd.command.startswith("-*-verify-*-"):
                self.verify_files(cmd.files)
            elif cmd.command.startswith("-*-verify-*-implementation"):
                self.verify_implmentation(cmd.files)
            else:
                self.execute_command(cmd.command, model=cmd.model, files=cmd.files)

if __name__ == "__main__":



    obj = parse_yaml()
    executor = OpenCodeExecutor(project_name=obj.get("title", "Unnamed Project"), yaml_path="steps.yaml", log_level=obj.get("log_level", "INFO"), message=obj.get("message", "")