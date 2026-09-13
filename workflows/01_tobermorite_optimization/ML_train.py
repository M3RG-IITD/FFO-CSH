import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.preprocessing import StandardScaler
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


from sklearn.preprocessing import MinMaxScaler
from botorch.models import SingleTaskGP
from botorch.fit import fit_gpytorch_mll
from botorch.acquisition import LogExpectedImprovement
from botorch.optim import optimize_acqf
from gpytorch.mlls import ExactMarginalLogLikelihood

import cma


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
def train_and_select_best_model(X_train_scaled, y_train_scaled, y_scaler,
                                 hidden_layers, dropout_p=0.5, lr=1e-3, weight_decay=1e-5,
                                 n_epochs=1000, n_trials=10, plot_loss=False):
    X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
        X_train_scaled, y_train_scaled, test_size=0.2, random_state=42)

    best_model = None
    best_val_mse = float('inf')
    best_state_dict = None

    for trial in range(n_trials):
        model = FlexibleNN(input_dim=X_train_scaled.shape[-1], hidden_layers=hidden_layers, output_dim=y_train_scaled.shape[-1], dropout_p=dropout_p)
        optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        criterion = nn.MSELoss()

        X_tensor = torch.tensor(X_train_split, dtype=torch.float32)
        y_tensor = torch.tensor(y_train_split, dtype=torch.float32)
        
        loss_all = []
        for epoch in range(n_epochs):
            model.train()
            optimizer.zero_grad()
            output = model(X_tensor)
            loss = criterion(output, y_tensor)
            loss_all.append(loss.item())
            loss.backward()
            optimizer.step()
        
        # plot loss curve as well if loss keyword is passed
        if plot_loss:
            plt.plot(loss_all, label=f'Trial {trial+1}')
            plt.xlabel('Epoch')
            plt.ylabel('Loss')
            plt.title('Training Loss Curve')
            plt.legend()
            plt.show()
        
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

    best_model = FlexibleNN(X_train_scaled.shape[-1], hidden_layers, y_train_scaled.shape[-1], dropout_p)
    best_model.load_state_dict(best_state_dict)
    print(f"\n✅ Best model selected with Val MSE: {best_val_mse:.4f}")
    return best_model


def evaluate_model(model, X_scaled, y_scaled, y_scaler, y_true=None, dataset_name="Set"):
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

def inverse_design_bo1(model, target_props, X_train, X_scaler, y_scaler, n_init=10, n_iter=25):
    model.eval()
    input_dim = X_train.shape[1]

    # === Target property scaled ===
    target_scaled = torch.tensor(y_scaler.transform([target_props]), dtype=torch.float64)

    # === Create MinMaxScaler on standard-scaled input ===
    X_train_std = X_scaler.transform(X_train)
    minmax_scaler = MinMaxScaler()
    X_train_minmax = minmax_scaler.fit_transform(X_train_std)

    # === Initial samples in [0, 1] ===
    X_init_minmax = torch.tensor(np.random.uniform(0, 1, size=(n_init, input_dim)), dtype=torch.float64)

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


def inverse_design_bo2(model, target_props, X_train, X_scaler, y_scaler, n_init=10, n_iter=25, num_restarts=10):
    model.eval()
    input_dim = X_train.shape[1]

    # Scale target properties
    target_scaled = torch.tensor(y_scaler.transform([target_props]), dtype=torch.float64)

    # Scale X_train to [0, 1] for BO
    X_train_std = X_scaler.transform(X_train)
    minmax_scaler = MinMaxScaler()
    X_train_minmax = minmax_scaler.fit_transform(X_train_std)

    # Initial samples
    X_init = torch.tensor(np.random.uniform(0, 1, size=(n_init, input_dim)), dtype=torch.float64)
    with torch.no_grad():
        y_init = model(torch.tensor(X_scaler.inverse_transform(minmax_scaler.inverse_transform(X_init)),dtype=torch.float32)).double()

    # Train GP model
    gp = SingleTaskGP(X_init, y_init)
    mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
    fit_gpytorch_mll(mll)

    # Define acquisition function
    acq_func = LogExpectedImprovement(gp, best_f=target_scaled.mean(), maximize=False)

    # Optimize acquisition
    candidates, _ = optimize_acqf(
        acq_function=acq_func,
        bounds=torch.tensor([[0.0] * input_dim, [1.0] * input_dim], dtype=torch.float64),
        q=num_restarts,
        num_restarts=num_restarts,
        raw_samples=256,
    )

    # Map candidates back to real input scale
    candidates_std = minmax_scaler.inverse_transform(candidates.numpy())
    candidates_real = X_scaler.inverse_transform(candidates_std)

    return candidates_real



def inverse_design_bo3(model, target_props, X_train, X_scaler, y_scaler, n_init=10, n_iter=25, n_suggestions=10):

    model.eval()
    input_dim = X_train.shape[1]

    # Scale target
    target_scaled = torch.tensor(y_scaler.transform([target_props]), dtype=torch.float32)

    # Normalize X_train in [0, 1]
    X_train_std = X_scaler.transform(X_train)
    minmax_scaler = MinMaxScaler()
    X_train_minmax = minmax_scaler.fit_transform(X_train_std)

    # Generate initial samples in [0, 1]
    X_init = torch.tensor(np.random.uniform(0, 1, size=(n_init, input_dim)), dtype=torch.float32)
    
    def evaluate_points(X_norm):
        X_std = minmax_scaler.inverse_transform(X_norm)
        X_real = X_scaler.inverse_transform(X_std)
        X_tensor = torch.tensor(X_real, dtype=torch.float32)
        with torch.no_grad():
            y_pred_scaled = model(X_tensor).numpy()
        y_pred = y_scaler.inverse_transform(y_pred_scaled)
        return y_pred

    def compute_objective(y_pred):
        errors = (target_props - y_pred) ** 2
        normalized = errors / (np.array(target_props) **2)
        return np.mean(normalized, axis=1)  # return 1D array

    # Create initial dataset
    Y_init = compute_objective(evaluate_points(X_init.numpy()))
    Y_init = torch.tensor(Y_init, dtype=torch.float32).unsqueeze(-1)  # shape (n, 1)

    X = X_init.clone()
    Y = Y_init.clone()

    for i in range(n_iter):
        gp = SingleTaskGP(X, Y)
        mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
        fit_gpytorch_mll(mll)

        acquisition = LogExpectedImprovement(gp, best_f=Y.min())
        candidate, _ = optimize_acqf(
            acquisition,
            bounds=torch.stack([torch.zeros(input_dim), torch.ones(input_dim)]),
            q=1,
            num_restarts=5,
            raw_samples=100,
        )

        y_new = compute_objective(evaluate_points(candidate.detach().numpy()))
        X = torch.cat([X, candidate], dim=0)
        Y = torch.cat([Y, torch.tensor(y_new, dtype=torch.float32).unsqueeze(-1)], dim=0)

    # Select best n_suggestions points
    best_indices = torch.topk(-Y.squeeze(), n_suggestions).indices
    best_X = X[best_indices]

    # Convert from normalized → standard scaled → real scale
    best_X_std = minmax_scaler.inverse_transform(best_X.detach().numpy())
    best_X_real = X_scaler.inverse_transform(best_X_std)
    
    print("✅ Bayesian optimization complete.")
    return best_X_real


def inverse_design_cma(model, target_props, X_train, X_scaler, y_scaler, n_iter=25, popsize=10, sigma0=0.1, verbose=True):
    target_props = np.array(target_props)
    evaluated_x = []
    evaluated_losses = []

    # === 1. Objective Function ===
    def objective(x):
        x = np.atleast_2d(x)
        x_scaled = X_scaler.transform(x)
        
        model.eval()
        with torch.no_grad():
            y_pred_scaled = model(torch.tensor(x_scaled, dtype=torch.float32)).numpy()
        
        y_pred = y_scaler.inverse_transform(y_pred_scaled)
        rel_error = np.abs((y_pred[0] - target_props) / target_props)
        loss = np.sum(rel_error**2)
        
        # Track for top-10
        evaluated_x.append(x[0].copy())
        evaluated_losses.append(loss)
        
        if verbose:
            print(f"[CMA-ES] Eval: x={x[0].round(3)}, loss={loss:.4f}")

        return loss

    # === 2. CMA Initialization ===
    x0 = X_train[np.random.randint(len(X_train))]
    es = cma.CMAEvolutionStrategy(
        x0.tolist(),  # initial mean
        sigma0,       # initial standard deviation
        {'popsize': popsize}
    )

    # === 3. Optimize ===
    # result = es.optimize(objective, iterations=n_iter).result
    # x_opt = result.xbest
    
    es.optimize(objective, iterations=n_iter)
    top10 = sorted(zip(evaluated_x, evaluated_losses), key=lambda p: p[1])[:10]
    top10_x = [np.array(x) for x, _ in top10]
    top10_loss = [np.array(_) for x, _ in top10]
    return np.array(top10_x), top10_loss


###################################################
###################################################
import numpy as np
import torch

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.core.problem import Problem

from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM


from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions

from pymoo.algorithms.moo.moead import MOEAD

from pymoo.core.problem import Problem

def run_nsga2(model, target_props, X_scaler, y_scaler, pop_size=20, n_gen=30, n_suggestions=10):
    input_dim = X_scaler.mean_.shape[0]

    # Multi-objective: minimize individual property errors
    class MultiObjProblem(Problem):
        def __init__(self):
            super().__init__(
                n_var=input_dim,
                n_obj=len(target_props),
                n_constr=0,
                xl=0.0,
                xu=1.0
            )

        def _evaluate(self, X, out, *args, **kwargs):
            X_std = X_scaler.inverse_transform(X)
            X_tensor = torch.tensor(X_std, dtype=torch.float32)
            
            model.eval()
            with torch.no_grad():
                Y_scaled = model(X_tensor).numpy()
            
            Y_real = y_scaler.inverse_transform(Y_scaled)
            # Calculate normalized squared error
            error = ((np.array(target_props) - Y_real) ** 2) / (np.array(target_props) ** 2)
            out["F"] = error  # shape (n_points, n_obj)  # np.mean(error, axis=1).reshape(-1, 1)


    algorithm = NSGA2(
        pop_size=pop_size,
        sampling=FloatRandomSampling(),
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True
    )

    result = minimize(MultiObjProblem(), algorithm, termination=('n_gen', n_gen), verbose=False)

    best_X = result.X[:n_suggestions]  # pick top-n
    best_X_std = X_scaler.inverse_transform(best_X)
    return best_X_std


def run_nsga3(model, target_props, X_scaler, y_scaler, pop_size=91, n_gen=40, n_suggestions=10, n_partitions=2):
    input_dim = X_scaler.mean_.shape[0]
    
    # Multi-objective: minimize individual property errors
    class MultiObjProblem(Problem):
        def __init__(self):
            super().__init__(
                n_var=input_dim,
                n_obj=len(target_props),
                n_constr=0,
                xl=0.0,
                xu=1.0
            )

        def _evaluate(self, X, out, *args, **kwargs):
            X_std = X_scaler.inverse_transform(X)
            X_tensor = torch.tensor(X_std, dtype=torch.float32)
            with torch.no_grad():
                Y_scaled = model(X_tensor).numpy()
            Y_real = y_scaler.inverse_transform(Y_scaled)
            error = ((np.array(target_props) - Y_real) ** 2) / (np.array(target_props) ** 2)
            out["F"] = error  # shape (n_points, n_obj)

    ref_dirs = get_reference_directions("das-dennis", len(target_props), n_partitions=n_partitions) # division parameter

    algorithm = NSGA3(
        pop_size=pop_size,
        ref_dirs=ref_dirs,
        sampling=FloatRandomSampling(),
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True
    )

    result = minimize(MultiObjProblem(), algorithm, termination=('n_gen', n_gen), verbose=False)
    
    best_X = result.X[:n_suggestions]
    return X_scaler.inverse_transform(best_X)


# def run_moead(model, target_props, X_scaler, y_scaler, n_gen=40, n_suggestions=10):
#     input_dim = X_scaler.mean_.shape[0]

#     class MultiObjProblem(Problem):
#         def __init__(self):
#             super().__init__(
#                 n_var=input_dim,
#                 n_obj=len(target_props),
#                 n_constr=0,
#                 xl=0.0,
#                 xu=1.0
#             )

#         def _evaluate(self, X, out, *args, **kwargs):
#             X_std = X_scaler.inverse_transform(X)
#             X_tensor = torch.tensor(X_std, dtype=torch.float32)
#             with torch.no_grad():
#                 Y_scaled = model(X_tensor).numpy()
#             Y_real = y_scaler.inverse_transform(Y_scaled)
#             error = ((np.array(target_props) - Y_real) ** 2) / (np.array(target_props) ** 2)
#             out["F"] = error

#     ref_dirs = get_reference_directions("uniform", len(target_props), n_partitions=3)

#     algorithm = MOEAD(
#         ref_dirs=ref_dirs,
#         sampling=FloatRandomSampling(),
#         crossover=SBX(prob=0.9, eta=15),
#         mutation=PM(eta=20)
#     )

#     result = minimize(MultiObjProblem(), algorithm, termination=('n_gen', n_gen), verbose=False)

#     best_X = result.X[:n_suggestions]
#     return X_scaler.inverse_transform(best_X)

