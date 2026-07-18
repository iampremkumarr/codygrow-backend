import tempfile, subprocess, os, uuid, json, sys
from app.services.output_handler import get_visual_outputs
from app.config import settings

def execute_generated_code(code: str, task: str = "classification") -> dict:
    run_id = uuid.uuid4().hex[:8]
    os.makedirs(settings.SCRIPTS_DIR, exist_ok=True)
    script_path = os.path.join(settings.SCRIPTS_DIR, f"{run_id}.py")
    output = {"stdout": "", "stderr": "", "success": False, "script_path": script_path}

    try:
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
