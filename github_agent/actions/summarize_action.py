# github_agent/actions/summarise_action.py
from sentient_agent_framework.interface.action import Action
from sentient_agent_framework.interface.event import TextChunkEvent, DoneEvent
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

class SummariseRepos(Action):
    def __init__(self, store: dict[str, object]):
        super().__init__()
        self.store = store
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    async def _run(self, inputs, rh):
        for item in inputs:
            repo  = item.payload["repo"]
            vs    = self.store[f"vs:{repo}"]
            chain = RetrievalQA.from_chain_type(self.llm,
                                                retriever=vs.as_retriever())
            summary = chain.run("Give a concise 5‑sentence overview …")
            await rh.emit_text_block(repo, summary)
        await rh.complete()
        return "ok"