import torch
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from ML_train import train_and_select_best_model, evaluate_model, inverse_design_bo3, inverse_design_cma, run_nsga2, run_nsga3

from run_md_sim import MD_sim

# === 1. Load Data ===
df_full = pd.read_csv('../../data/training/training_data_145.csv')
df_full = df_full.dropna()

X_full = df_full.values[:, :4]
y_full = df_full.values[:, 4:]

# === 2. Fixed Train/Test Split ===
X_train, X_test, y_train, y_test = train_test_split(X_full, y_full, test_size=0.2, random_state=42)

# Save original test set once
X_test_orig = X_test.copy()
y_test_orig = y_test.copy()
pd.DataFrame(np.hstack([X_test_orig, y_test_orig]), columns=df_full.columns).to_csv(f'../../data/training/models/NSGA2/data_test.csv', index=False)

for AL_run in range(10):

    print(f"\n=== Active Learning Iteration {AL_run} ===")

    # === 3. Scale ===
    X_scaler = StandardScaler().fit(X_train)
    y_scaler = StandardScaler().fit(y_train)

    X_train_scaled = X_scaler.transform(X_train)
    y_train_scaled = y_scaler.transform(y_train)
    X_test_scaled = X_scaler.transform(X_test_orig)
    y_test_scaled = y_scaler.transform(y_test_orig)

    # === 4. Train model ===
    model = train_and_select_best_model(
        X_train_scaled, y_train_scaled, y_scaler,
        hidden_layers=[64, 32],  # customize this
        dropout_p=0.3,                # try 0.2, 0.3, 0.5
        lr=5e-4,                      # try 1e-3, 5e-4, 1e-4
        weight_decay=1e-4,               # L2 regularization
        n_epochs=1000,
        n_trials=10
    )

    # === 5. Evaluate model ===
    y_train_real, y_train_pred = evaluate_model(model, X_train_scaled, y_train_scaled, y_scaler, dataset_name="Train")
    y_test_real, y_test_pred = evaluate_model(model, X_test_scaled, y_test_scaled, y_scaler, dataset_name="Test")

    # Save test set accuracy
    test_r2 = r2_score(y_test_real, y_test_pred)
    
    with open(f'../../data/training/models/NSGA2/test_accuracy_{AL_run}.txt', 'w') as f:
        f.write(f'R2 score: {test_r2}\n')

    # save the model
    torch.save(model.state_dict(), f'../../data/training/models/NSGA2/model_{AL_run}.pth')
    # # load the model
    # model.load_state_dict(torch.load(f'../../data/training/models/NSGA2/model_{AL_run}.pth'))

    # === 6. Inverse Design ===
    target_y = [2.46, 2.39, 2.23, 680, 325, 635, 71, 55.35, 47]

    x_opt_nsga2 = run_nsga2(
        model=model,
        target_props=target_y,
        X_scaler=X_scaler,
        y_scaler=y_scaler,
        pop_size=100, # Population size — number of candidate solutions (individuals) in each generation
        n_gen=100, # Number of generations — how many iterations the algorithm evolves the population
        n_suggestions=10
        )

    # === 7. Run MD simulation ===
    df_new_nsga2 = MD_sim(np.atleast_2d(x_opt_nsga2), optimizer= 'NSGA2')
    df_new_nsga2 = df_new_nsga2.dropna()
    
    # === 8. Evaluate match ===
    md_prop_pred = df_new_nsga2.values[:,4:]
    y_error = np.abs(100*(md_prop_pred - np.array(target_y))/np.array(target_y))

    for i in range(len(y_error)):
        targeted_error = np.array([1, 1, 1, 5, 5, 5, 10, 10, 10])
        if (y_error[i] <= targeted_error).sum() == 9:
            print("All properties are within error limits")
            print(df_new_nsga2.iloc[i])
            break # break Active learning loop.

        else:
            total_false = (~(y_error[i] <= targeted_error)).sum()
            print("❌ Failure! Outside acceptable error range.")
            print(f"Failed for {total_false} properties")
            print("Error percentage:", y_error[i].round(2))

    
    # === 9. Append new data to TRAIN set ===
    X_train = np.vstack([X_train, df_new_nsga2.values[:, :4]])
    y_train = np.vstack([y_train, df_new_nsga2.values[:, 4:]])

    # Save cumulative data
    df_updated = pd.DataFrame(np.hstack([X_train, y_train]))
    df_updated.columns = df_full.columns
    df_updated.to_csv(f'../../data/training/models/NSGA2/data_{AL_run}.csv', index=False)
