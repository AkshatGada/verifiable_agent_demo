# OLD:
# from sentient_agent_framework.interface.memory import MemoryManager
# ...
# class IndexReadmes(Action):
#     def __init__(self, mem: MemoryManager):

# NEW:
from sentient_agent_framework.interface.action import Action
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS

class IndexReadmes(Action):
    name = "index_readmes"

    def __init__(self, store: dict[str, FAISS]):
        super().__init__()
        self.store = store
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=600, chunk_overlap=100)
        self.embed = OpenAIEmbeddings()

    async def _run(self, inputs):
        for item in inputs:
            docs = self.splitter.create_documents([item.text])
            vs = FAISS.from_documents(docs, self.embed)
            self.store[f"vs:{item.payload['repo']}"] = vs
        return inputs