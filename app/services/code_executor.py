import tempfile, subprocess, os, uuid, json, sys

from app.config import settings

def execute_generated_code(code: str, task: str = "classification") -> dict:
    run_id = uuid.uuid4().hex[:8]
    os.makedirs(settings.SCRIPTS_DIR, exist_ok=True)
    script_path = os.path.join(settings.SCRIPTS_DIR, f"{run_id}.py")
    output = {"stdout": "", "stderr": "", "success": False, "script_path": script_path}

    try:
        # For classification tasks, inject a safety header that auto-converts
        # continuous float targets to discrete categories before fitting.
        # This prevents sklearn's "Unknown label type: continuous" crash.
        if task == "classification":
            safety_header = (
                "# --- Auto-injected safety wrapper for classification ---\n"
                "import warnings as _warnings; _warnings.filterwarnings('ignore')\n"
                "import numpy as _np; import pandas as _pd\n"
                "_orig_train_test_split = None\n"
                "try:\n"
                "    from sklearn.model_selection import train_test_split as _orig_tts\n"
                "    def _safe_train_test_split(*args, **kwargs):\n"
                "        result = _orig_tts(*args, **kwargs)\n"
                "        # Check if y_train (index 2) contains continuous floats\n"
                "        if len(result) == 4:\n"
                "            X_tr, X_te, y_tr, y_te = result\n"
                "            is_float = False\n"
                "            try: is_float = _pd.api.types.is_float_dtype(y_tr)\n"
                "            except: pass\n"
                "            if is_float:\n"
                "                # Convert continuous targets to discrete bins\n"
                "                all_y = _np.concatenate([y_tr, y_te])\n"
                "                n_bins = min(10, len(_np.unique(all_y)))\n"
                "                bins = _np.linspace(all_y.min(), all_y.max(), n_bins + 1)\n"
                "                y_tr = _np.digitize(y_tr, bins[:-1]) - 1\n"
                "                y_te = _np.digitize(y_te, bins[:-1]) - 1\n"
                "                return X_tr, X_te, y_tr, y_te\n"
                "        return result\n"
                "    import sklearn.model_selection as _skms\n"
                "    _skms.train_test_split = _safe_train_test_split\n"
                "except: pass\n"
                "# --- End safety wrapper ---\n\n"
            )
            code = safety_header + code

        # Save the code
        with open(script_path, "w") as f:
            f.write(code)

        # Determine the correct Python interpreter (prefer virtual environment)
        # Calculate backend root dir based on current file location: backend/app/services/code_executor.py
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        venv_python_win = os.path.join(backend_dir, ".venv", "Scripts", "python.exe")
        venv_python_unix = os.path.join(backend_dir, ".venv", "bin", "python")
        
        if os.path.exists(venv_python_win):
            executable = venv_python_win
        elif os.path.exists(venv_python_unix):
            executable = venv_python_unix
        else:
            executable = sys.executable

        # Ensure the subprocess inherits the parent's runtime python paths (crucial for Vercel/serverless environments)
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(sys.path)

        # Run the code
        result = subprocess.run(
            [executable, script_path],
            capture_output=True,
            text=True,
            timeout=90,
            env=env
        )

        output.update({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        })

        # Save metrics & visuals if output is valid
        if output["success"]:
            # You can insert a global variable here later if needed
            # Assume that your generated code saves predictions in a known location (future feature)
            # For now, let’s assume visual/metrics are generated externally.

            # Example placeholder:
            # metrics, visual_paths = { "r2": 0.9 }, ["generated/outputs/plot.png"]
            metrics = {}  # insert real metrics if available
            visual_paths = []  # insert plot paths if applicable

            # Save metrics (optional for now)
            os.makedirs(settings.METRICS_DIR, exist_ok=True)
            metrics_path = os.path.join(settings.METRICS_DIR, f"{run_id}.json")
            with open(metrics_path, "w") as m:
                json.dump(metrics, m, indent=2)

            output.update({
                "visuals": visual_paths,
                "metrics": metrics,
                "metrics_path": metrics_path
            })

        return output

    except Exception as e:
        output["stderr"] = str(e)
        return output
