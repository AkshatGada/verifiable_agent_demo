from sentient_agent_framework.interface.agent import AbstractAgent
from sentient_agent_framework.interface.response_handler import ResponseHandler
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

from github_agent.utils.github_readme import fetch_readme

class GitHubSummaryAgent(AbstractAgent):
    name = "github_summary"

    def __init__(self):
        super().__init__(self.name)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=600, chunk_overlap=100)
        self.embed = OpenAIEmbeddings()
        self.llm   = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    async def assist(self, session, query, rh: ResponseHandler):
        urls = [u for u in query.prompt.split() if u.startswith("http")]
        for url in urls:
            repo, readme = fetch_readme(url)
            docs = self.splitter.create_documents([readme])
            vs   = FAISS.from_documents(docs, self.embed)
            chain = RetrievalQA.from_chain_type(
                self.llm, retriever=vs.as_retriever())
            summary = chain.run(
                "Provide a concise 5‑sentence overview of this repository."
            )
            await rh.emit_text_block(repo, summary)
        await rh.complete()