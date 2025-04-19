# github_agent/tools/github_readme_tool.py
import os, requests
from sentient_agent_framework.interface.tool import Tool, ToolIO

class GitHubReadmeTool(Tool):
    """
    Input : a GitHub repo URL
    Output: ToolIO(text=<readme>, payload={'repo': 'org/name'})
    """
    name = "github_readme"

    async def _run(self, inp: ToolIO) -> ToolIO:
        url = inp.text.strip().rstrip("/")
        owner, name = url.split("/")[-2:]
        api = f"https://api.github.com/repos/{owner}/{name}/readme"
        headers = {"Accept": "application/vnd.github.raw"}
        if tok := os.getenv("GH_TOKEN"):
            headers["Authorization"] = f"token {tok}"
        res = requests.get(api, headers=headers, timeout=20)
        res.raise_for_status()
        return ToolIO(text=res.text,
                      payload={"repo": f"{owner}/{name}"})