import litellm
from rapidfuzz import fuzz, process

# models = [m for m in litellm.model_list if "gemini" in m]
# models.sort()

query = "gemini 3.5"
models = process.extract(query, litellm.model_list, limit=10)
models = [m[0] for m in models]

for model in models:
    print(model)

# print (len(litellm.model_list))