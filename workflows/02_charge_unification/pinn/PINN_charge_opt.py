import torch
import torch.nn as nn
import torch.optim as optim

# Load your charge distribution data (assumed format)
# X: Charge distributions, y: Corresponding surface energy
X = torch.tensor([...], dtype=torch.float32)  # Shape: (num_samples, num_charges)
y = torch.tensor([...], dtype=torch.float32)  # Shape: (num_samples, 1)

# Define the Physics-Informed Neural Network (PINN)
class PINN(nn.Module):
    def __init__(self, input_dim, hidden_dim=32, output_dim=1):
        super(PINN, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, output_dim)
        self.activation = nn.Tanh()  # Smooth activation function

    def forward(self, x):
        x = self.activation(self.fc1(x))
        x = self.activation(self.fc2(x))
        x = self.fc3(x)
        return x

# Initialize model, optimizer, and loss function
model = PINN(input_dim=X.shape[1])
optimizer = optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.MSELoss()

# Physics-informed constraint: Charge Conservation
def charge_conservation_loss(pred_charges):
    return torch.abs(torch.sum(pred_charges, dim=1))  # Total charge should be near zero

# Training loop
num_epochs = 1000
for epoch in range(num_epochs):
    optimizer.zero_grad()
    
    # Predict surface energy from charge distributions
    predictions = model(X)

    # Compute physics-informed loss
    energy_loss = loss_fn(predictions, y)  # Standard MSE loss
    physics_loss = charge_conservation_loss(X).mean()  # Enforce charge neutrality
    total_loss = energy_loss + 0.1 * physics_loss  # Weighted loss function
    
    total_loss.backward()
    optimizer.step()

    if epoch % 100 == 0:
        print(f"Epoch {epoch}: Loss = {total_loss.item()}")

# Use trained model to find optimal charge distribution
optimal_charges = model(X).detach().numpy()
print("Optimized Charge Distributions:", optimal_charges)
