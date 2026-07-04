from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

from app.core.config import settings
from app.models.document import Chunk


class PromptBuilder:
    def build(self, question: str, chunks: list[tuple[Chunk, float]]) -> str:
        context_parts = []
        for chunk, _ in chunks:
            context_parts.append(f"[page {chunk.page_number}] {chunk.content}")

        context = "\n\n".join(context_parts)

        return (
            f"Tu es un assistant qui répond uniquement à partir du contexte fourni. "
            f"Si la réponse n'est pas dans le contexte, dis-le clairement.\n\n"
            f"CONTEXTE :\n{context}\n\n"
            f"QUESTION : {question}\n\n"
            f"RÉPONSE :"
        )


class Generator:
    def __init__(self):
        self._model = None
        self._tokenizer = None

    def _load(self):
        if self._model is None:
            self._tokenizer = AutoTokenizer.from_pretrained(
                settings.LLM_MODEL, local_files_only=True
            )
            self._model = AutoModelForCausalLM.from_pretrained(
                settings.LLM_MODEL,
                dtype=torch.float32,
                device_map="cpu",
                local_files_only=True,
            )
            self._model.eval()

    def generate(self, prompt: str, max_new_tokens: int = 512) -> str:
        self._load()

        messages = [{"role": "user", "content": prompt}]
        text = self._tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self._tokenizer(text, return_tensors="pt")

        with torch.no_grad():
            output_ids = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self._tokenizer.eos_token_id,
            )

        # on retire les tokens du prompt, on garde seulement la génération
        new_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
        return self._tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


prompt_builder = PromptBuilder()
generator = Generator()
