# model_def.py - custom DistilBERT model with entity features
import torch
import torch.nn as nn
from transformers import DistilBertModel
# from transformers.modeling_outputs import SequenceClassifierOutput

class DistilBertWithEntities(nn.Module):
    def __init__(self, num_labels, entity_dim=5):
        super().__init__()
        self.bert = DistilBertModel.from_pretrained("distilbert-base-uncased")
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(768 + entity_dim, num_labels)

    # DistilBERT forward method
    def forward(self,input_ids=None,attention_mask=None,labels=None,num_actors=None,num_directors=None,actor_mentions=None,
                director_mentions=None,entity_sentiment=None):

        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0]  # CLS token

        # Stack entity features
        entity_tensors = [
            num_actors.unsqueeze(1).float(),
            num_directors.unsqueeze(1).float(),
            actor_mentions.unsqueeze(1).float(),
            director_mentions.unsqueeze(1).float(),
            entity_sentiment.unsqueeze(1).float(),
        ]
        entity_tensor = torch.cat(entity_tensors, dim=1)

        # Combine text + entity features
        combined = torch.cat((pooled_output, entity_tensor), dim=1)
        combined = self.dropout(combined)
        logits = self.fc(combined)

        # Loss with optional class weights
        loss = None
        if labels is not None:
            class_counts = torch.bincount(labels)
            class_weights = (1.0 / class_counts.float()).to(logits.device)
            loss_fn = nn.CrossEntropyLoss(weight=class_weights)
            loss = loss_fn(logits, labels)

        return {"loss": loss, "logits": logits}

