import pickle
import gzip

# load original model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# save compressed model
with gzip.open("model.pkl.gz", "wb") as f:
    pickle.dump(model, f)

print("✅ Model compressed successfully!")