# app/services/output_handler.py

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid
from sklearn.metrics import confusion_matrix, mean_squared_error, r2_score
import numpy as np
from app.config import settings

def save_plot(fig, prefix: str = "plot") -> str:
    os.makedirs(settings.OUTPUTS_DIR, exist_ok=True)
    filename = f"{prefix}_{uuid.uuid4().hex[:8]}.png"
    path = os.path.join(settings.OUTPUTS_DIR, filename)
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    return f"generated/outputs/{filename}"

def get_visual_outputs(task: str, y_true, y_pred, model=None, X=None):
    visuals = []
    metrics = {}

    # Convert to numpy for safety
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    if task == "classification" and len(y_true) > 0:
        try:
            cm = confusion_matrix(y_true, y_pred)
            fig, ax = plt.subplots()
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)
            ax.set_title("Confusion Matrix")
            visuals.append(save_plot(fig, "confusion"))

            accuracy = (y_true == y_pred).sum() / len(y_true)
            metrics["accuracy"] = round(accuracy, 4)
        except Exception as e:
            metrics["error"] = f"Error creating classification plot: {str(e)}"

    elif task == "regression" and len(y_true) > 0:
        try:
            fig, ax = plt.subplots()
            ax.scatter(y_true, y_pred, alpha=0.6)
            ax.set_xlabel("Actual")
            ax.set_ylabel("Predicted")
            ax.set_title("Actual vs Predicted")
            visuals.append(save_plot(fig, "regression"))

            metrics["mse"] = round(mean_squared_error(y_true, y_pred), 4)
            metrics["r2"] = round(r2_score(y_true, y_pred), 4)
        except Exception as e:
            metrics["error"] = f"Error creating regression plot: {str(e)}"

    else:
        metrics["note"] = "Insufficient data or unsupported task type"

    return {
        "visual_paths": visuals,
        "metrics": metrics
    }
