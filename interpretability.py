# import torch
# from captum.attr import IntegratedGradients
#
# # Token Attribution
# from captum.attr import IntegratedGradients
# import torch
#
# def get_token_attributions(model, inputs, target_label, entity_features):
#     # forward function must accept all arguments your model expects
#     def forward_func(input_ids, attention_mask, num_actors, num_directors,
#                      actor_mentions, director_mentions, entity_sentiment):
#         outputs = model(
#             input_ids=input_ids.long(),
#             attention_mask=attention_mask,
#             num_actors=num_actors,
#             num_directors=num_directors,
#             actor_mentions=actor_mentions,
#             director_mentions=director_mentions,
#             entity_sentiment=entity_sentiment
#         )
#         return outputs["logits"]
#
#     ig = IntegratedGradients(forward_func)
#
#     attributions = ig.attribute(
#         inputs["input_ids"].long(),
#         target=target_label,
#         additional_forward_args=(
#             inputs["attention_mask"],
#             torch.tensor([entity_features["num_actors"]]),
#             torch.tensor([entity_features["num_directors"]]),
#             torch.tensor([entity_features["actor_mentions"]]),
#             torch.tensor([entity_features["director_mentions"]]),
#             torch.tensor([entity_features["entity_sentiment"]])
#         ), allow_unused=True
#     )
#     return attributions.squeeze().detach().cpu().tolist()
#
# # Entity Skew
# def compute_entity_skew(model, tokenizer, review_text, actor_name, entity_features):
#     # Convert features to tensors
#     entity_features_tensors = {
#         "num_actors": torch.tensor([entity_features["num_actors"]]),
#         "num_directors": torch.tensor([entity_features["num_directors"]]),
#         "actor_mentions": torch.tensor([entity_features["actor_mentions"]]),
#         "director_mentions": torch.tensor([entity_features["director_mentions"]]),
#         "entity_sentiment": torch.tensor([entity_features["entity_sentiment"]])
#     }
#
#     # With actor
#     inputs_with = tokenizer(review_text, return_tensors="pt", truncation=True, max_length=128)
#     outputs_with = model(**inputs_with, **entity_features_tensors)
#     probs_with = torch.softmax(outputs_with["logits"], dim=1)
#
#     # Without actor
#     if actor_name in review_text:
#         text_without = review_text.replace(actor_name, "")
#     else:
#         text_without = review_text  # fallback
#
#     inputs_without = tokenizer(text_without, return_tensors="pt", truncation=True, max_length=128)
#     outputs_without = model(**inputs_without, **entity_features_tensors)
#     probs_without = torch.softmax(outputs_without["logits"], dim=1)
#
#     skew = (probs_with - probs_without).detach().cpu().tolist()
#     return skew