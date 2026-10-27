import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoConfig, AutoModel, PreTrainedModel

MODEL_NAME = "desklib/ai-text-detector-v1.01"

class AIDetector(PreTrainedModel):
    config_class = AutoConfig

    def __init__(self, config):
        super().__init__(config)
        self.model = AutoModel.from_config(config)
        self.classifier = nn.Linear(config.hidden_size, 1)
        self.post_init()

    def forward(self, input_ids, attention_mask=None):
        hidden = self.model(input_ids, attention_mask=attention_mask)[0]
        mask = attention_mask.unsqueeze(-1).expand(hidden.size()).float()
        pooled = (hidden * mask).sum(dim=1) / torch.clamp(mask.sum(dim=1), min=1e-9)
        return {"logits": self.classifier(pooled)}

_tokenizer = None
_model = None

def _load():
    global _tokenizer, _model
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AIDetector.from_pretrained(MODEL_NAME)
        _model.eval()

def ai_probability(text):
    _load()
    encoded = _tokenizer(
        text, padding="max_length", truncation=True,
        max_length=768, return_tensors="pt",
    )
    with torch.no_grad():
        out = _model(encoded["input_ids"], encoded["attention_mask"])
    return torch.sigmoid(out["logits"]).item()