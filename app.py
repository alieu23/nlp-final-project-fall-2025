from fastapi import FastAPI
from pydantic import BaseModel
import torch
from torch.nn.functional import softmax
from transformers import DistilBertTokenizerFast
# from interpretability import get_token_attributions, compute_entity_skew
from model_def import DistilBertWithEntities
from safetensors.torch import load_file

# Load tokenizer
tokenizer = DistilBertTokenizerFast.from_pretrained("./distilbert-entity-improved")

# Load model weights from safetensors
state_dict = load_file("./distilbert-entity-improved/model.safetensors")
model = DistilBertWithEntities(num_labels=2, entity_dim=5)
model.load_state_dict(state_dict)
model.eval()

app = FastAPI()

class ReviewInput(BaseModel):
    text: str
    num_actors: float = 0
    num_directors: float = 0
    actor_mentions: float = 0
    director_mentions: float = 0
    entity_sentiment: float = 0
    actor_name: str

@app.post("/analyze")
def analyze(review: ReviewInput):
    # Tokenize text
    inputs = tokenizer(review.text, return_tensors="pt", truncation=True, max_length=128)
    # inputs["input_ids"] = inputs["input_ids"].long() #casting

    # Add entity features
    with torch.no_grad():
        outputs = model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            num_actors=torch.tensor([review.num_actors]),
            num_directors=torch.tensor([review.num_directors]),
            actor_mentions=torch.tensor([review.actor_mentions]),
            director_mentions=torch.tensor([review.director_mentions]),
            entity_sentiment=torch.tensor([review.entity_sentiment])
        )
        probs = softmax(outputs["logits"], dim=1)
        pred = torch.argmax(probs, dim=1).item()
        score = probs[0][pred].item()

        # Attribution scores
    # entity_features = {
    #     "num_actors": review.num_actors,
    #     "num_directors": review.num_directors,
    #     "actor_mentions": review.actor_mentions,
    #     "director_mentions": review.director_mentions,
    #     "entity_sentiment": review.entity_sentiment
    # }
    #
    # attributions = get_token_attributions(model, inputs, target_label=pred, entity_features=entity_features)
    # token_scores = attributions.squeeze().tolist()

    # if review.actor_name:
    #     skew = compute_entity_skew(model, tokenizer, review.text, review.actor_name, {
    #         "num_actors": torch.tensor([review.num_actors]),
    #         "num_directors": torch.tensor([review.num_directors]),
    #         "actor_mentions": torch.tensor([review.actor_mentions]),
    #         "director_mentions": torch.tensor([review.director_mentions]),
    #         "entity_sentiment": torch.tensor([review.entity_sentiment])
    #     }).tolist()
    # else:
    #     skew = None

    return {
        "label": int(pred),
        "score": score,
        # "token_attributions": token_scores,
        # "entity_skew": skew
    }
