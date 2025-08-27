# src/train.py
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, random_split
import pandas as pd
import preprocess  # your preprocess.py

# ----------------------
# Load and preprocess data
# ----------------------
df = preprocess.load_matches("data/raw/matches.json")
df, team2id = preprocess.encode_teams(df)
df, map2id = preprocess.encode_maps(df)
df = preprocess.create_target(df)
df = preprocess.add_score_diff(df)

# Convert to tensors
X = torch.tensor(df[["team1_id", "team2_id", "map_id"]].values, dtype=torch.float32)
y = torch.tensor(df["target"].values, dtype=torch.float32).unsqueeze(1)

dataset = TensorDataset(X, y)

# Train/Validation split (80/20)
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32)

# ----------------------
# Define model
# ----------------------
class MatchPredictor(nn.Module):
    def __init__(self, input_dim=3, hidden_dim=16):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
    def forward(self, x):
        return self.net(x)

model = MatchPredictor()
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# ----------------------
# Training loop
# ----------------------
EPOCHS = 10
start_time = time.time()

for epoch in range(EPOCHS):
    # Training
    model.train()
    train_loss = 0
    correct_train = 0
    for xb, yb in train_loader:
        optimizer.zero_grad()
        preds = model(xb)
        loss = criterion(preds, yb)
        loss.backward()
        optimizer.step()
        train_loss += loss.item() * xb.size(0)
        correct_train += ((preds > 0.5) == yb).sum().item()

    train_loss /= train_size
    train_acc = correct_train / train_size

    # Validation
    model.eval()
    val_loss = 0
    correct_val = 0
    with torch.no_grad():
        for xb, yb in val_loader:
            preds = model(xb)
            loss = criterion(preds, yb)
            val_loss += loss.item() * xb.size(0)
            correct_val += ((preds > 0.5) == yb).sum().item()
    val_loss /= val_size
    val_acc = correct_val / val_size

    print(f"Epoch {epoch+1}/{EPOCHS}, "
          f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, "
          f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")

end_time = time.time()
print(f"Training completed in {end_time - start_time:.2f} seconds")

# ----------------------
# Save model
# ----------------------
torch.save(model.state_dict(), "models/match_predictor.pth")
print("Model saved to models/match_predictor.pth")
