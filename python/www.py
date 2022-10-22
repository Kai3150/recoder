import pickle
with open("text/text_dict.pkl", "rb") as f:
    text_dict = pickle.load(f)

print(text_dict)
