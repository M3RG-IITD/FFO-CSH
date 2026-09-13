import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from run_md_sim import MD_sim


os.chdir('ML_Pipeline')


# === 1. Load Data ===
df_a = pd.read_csv('data/training_data_123.csv')
df = df_a.dropna()

X = df.values[:, :4]
y = df.values[:, 4:]

# === 2. Split into train and test ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === 3. Scale ===
X_scaler = StandardScaler().fit(X_train)
y_scaler = StandardScaler().fit(y_train)

X_train_scaled = X_scaler.transform(X_train)
y_train_scaled = y_scaler.transform(y_train)

X_test_scaled = X_scaler.transform(X_test)
y_test_scaled = y_scaler.transform(y_test)


# === 1. Define Flexible Neural Network ===
class FlexibleNN(nn.Module):
    def __init__(self, input_dim, hidden_layers, output_dim, dropout_p=0.5):
        super().__init__()
        layers = []
        prev_dim = input_dim
        for h in hidden_layers:
            layers.append(nn.Linear(prev_dim, h))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(p=dropout_p))
            prev_dim = h
        layers.append(nn.Linear(prev_dim, output_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)

# === 2. Train & Select Best Model ===
def train_and_select_best_model(X_train_scaled, y_train_scaled, X_test_scaled, y_test_scaled,
                                 hidden_layers, dropout_p=0.5, lr=1e-3, weight_decay=1e-5,
                                 n_epochs=1000, n_trials=10):
    X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
        X_train_scaled, y_train_scaled, test_size=0.2, random_state=42)

    best_model = None
    best_val_mse = float('inf')
    best_state_dict = None

    for trial in range(n_trials):
        model = FlexibleNN(input_dim=4, hidden_layers=hidden_layers, output_dim=9, dropout_p=dropout_p)
        optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        criterion = nn.MSELoss()

        X_tensor = torch.tensor(X_train_split, dtype=torch.float32)
        y_tensor = torch.tensor(y_train_split, dtype=torch.float32)

        for epoch in range(n_epochs):
            model.train()
            optimizer.zero_grad()
            output = model(X_tensor)
            loss = criterion(output, y_tensor)
            loss.backward()
            optimizer.step()

        # Validation performance
        model.eval()
        with torch.no_grad():
            X_val_tensor = torch.tensor(X_val_split, dtype=torch.float32)
            y_val_pred_scaled = model(X_val_tensor).numpy()
            y_val_pred = y_scaler.inverse_transform(y_val_pred_scaled)
            y_val_real = y_scaler.inverse_transform(y_val_split)
            val_mse = mean_squared_error(y_val_real, y_val_pred)

        print(f"[Trial {trial+1}] Val MSE: {val_mse:.4f}")

        if val_mse < best_val_mse:
            best_val_mse = val_mse
            best_state_dict = model.state_dict()

    best_model = FlexibleNN(4, hidden_layers, 9, dropout_p)
    best_model.load_state_dict(best_state_dict)
    print(f"\n✅ Best model selected with Val MSE: {best_val_mse:.4f}")
    return best_model


def evaluate_model(model, X_scaled, y_scaled, y_true=None, dataset_name="Set"):
    model.eval()
    with torch.no_grad():
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
        y_pred_scaled = model(X_tensor).numpy()
        y_pred = y_scaler.inverse_transform(y_pred_scaled)
        y_true = y_scaler.inverse_transform(y_scaled) if y_true is None else y_true

        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        print(f"\n--- {dataset_name} Performance ---")
        print(f"MSE: {mse:.2f}, MAE: {mae:.2f}, R²: {r2:.4f}")
        
        return y_true, y_pred


import torch
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from botorch.models import SingleTaskGP
from botorch.fit import fit_gpytorch_mll
from botorch.acquisition import LogExpectedImprovement
from botorch.optim import optimize_acqf
from gpytorch.mlls import ExactMarginalLogLikelihood

def inverse_design_bo(model, target_props, X_train, X_scaler, y_scaler, n_init=10, n_iter=25):
    model.eval()
    input_dim = X_train.shape[1]

    # === Target property scaled ===
    target_scaled = torch.tensor(y_scaler.transform([target_props]), dtype=torch.float64)

    # === Create MinMaxScaler on standard-scaled input ===
    X_train_std = X_scaler.transform(X_train)
    minmax_scaler = MinMaxScaler()
    X_train_minmax = minmax_scaler.fit_transform(X_train_std)

    # === Initial samples in [0, 1] ===
    X_init_minmax = torch.tensor(
        np.random.uniform(0, 1, size=(n_init, input_dim)),
        dtype=torch.float64
    )

    def evaluate_model(x_minmax_tensor):
        x_std_np = minmax_scaler.inverse_transform(x_minmax_tensor.cpu().numpy())
        x_tensor_std = torch.tensor(x_std_np, dtype=torch.float32)  # model expects float32
        with torch.no_grad():
            y_pred = model(x_tensor_std).detach()
        return y_pred.to(dtype=torch.float64)

    # === Evaluate initial samples ===
    Y_init_model = evaluate_model(X_init_minmax)
    Y_obj = torch.mean((Y_init_model - target_scaled) ** 2, dim=1, keepdim=True)

    X_train_bo = X_init_minmax.clone()
    Y_train_bo = Y_obj.clone()

    bounds_bo = torch.tensor([[0.0] * input_dim, [1.0] * input_dim], dtype=torch.float64)

    for i in range(n_iter):
        # 1. Fit GP model
        gp = SingleTaskGP(X_train_bo, Y_train_bo)
        mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
        fit_gpytorch_mll(mll)

        # 2. Acquisition function
        acq_func = LogExpectedImprovement(gp, best_f=Y_train_bo.min().item())

        # 3. Optimize acquisition function
        candidate, _ = optimize_acqf(
            acq_function=acq_func,
            bounds=bounds_bo,
            q=1,
            num_restarts=10,
            raw_samples=100,
        )

        # 4. Evaluate new point
        y_new_model = evaluate_model(candidate)
        y_obj = torch.mean((y_new_model - target_scaled) ** 2, dim=1, keepdim=True)

        # 5. Update dataset
        X_train_bo = torch.cat([X_train_bo, candidate], dim=0)
        Y_train_bo = torch.cat([Y_train_bo, y_obj], dim=0)

        print(f"Iter {i+1:02d}: MSE = {y_obj.item():.4f}")

    # === Final result ===
    best_idx = torch.argmin(Y_train_bo)
    best_input_minmax = X_train_bo[best_idx].numpy()
    best_input_std = minmax_scaler.inverse_transform([best_input_minmax])
    best_input_real = X_scaler.inverse_transform(best_input_std)[0]

    print("\n✅ Bayesian optimization complete.")
    print("Optimized input (real scale):", best_input_real)
    return best_input_real


# === 6. Main Active Learning Loop ===
for iteration in range(10):
    print(f"\n=== Iteration {iteration} ===")
    model = train_and_select_best_model(
        X_train_scaled, y_train_scaled,
        X_test_scaled, y_test_scaled,
        hidden_layers=[64, 32],
        dropout_p=0.3,
        lr=5e-4,
        weight_decay=1e-4,
        n_epochs=1000,
        n_trials=10
    )
    y_train_real, y_train_pred = evaluate_model(model, X_train_scaled, y_train_scaled, y_train, "Train")
    y_test_real, y_test_pred = evaluate_model(model, X_test_scaled, y_test_scaled, y_test, "Test")


    # Step 1: Define target properties
    target_y = [2.46, 2.39, 2.23, 680, 325, 635, 71, 55.35, 47]

    # Step 2: Inverse design
    optimal_params = inverse_design_bo(
        model=model,
        target_props=target_y,
        X_train=X_train,
        X_scaler=X_scaler,
        y_scaler=y_scaler,
        n_init=10,
        n_iter=25
    )

    print("Suggested parameters:", optimal_params)

    # Step 3: Run simulation
    
    df_new = MD_sim(np.atleast_2d(optimal_params))
    
    x_new = df_new.values[:,:4]
    y_new = df_new.values[:,4:]
    
    y_error = 100*(y_new - np.array(target_y))/np.array(target_y)
    
    if y_error[:, :3]<=1:
        print("targeted density successfully achived")
        

    # Step 4: Append new data
    X_train = np.vstack([X_train, x_new])
    y_train = np.vstack([y_train, y_new])
    
    X_train_scaled = X_scaler.transform(X_train)
    y_train_scaled = y_scaler.transform(y_train)

    pd.DataFrame(np.hstack([X_train, y_train]), columns=df_new.columns).to_csv('data/updated.csv', index=False)
