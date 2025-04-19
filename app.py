from sentient_agent_framework import DefaultServer
from github_agent.agent import GitHubSummaryAgent

if __name__ == "__main__":
    DefaultServer(GitHubSummaryAgent()).run(host="0.0.0.0", port=8000)