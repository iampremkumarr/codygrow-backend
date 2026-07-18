import tempfile, subprocess, os, uuid, json
from app.services.output_handler import get_visual_outputs

def execute_generated_code(code: str, task: str = "classification") -> dict:
    run_id = uuid.uuid4().hex[:8]
    script_path = f"generated/scripts/{run_id}.py"
    output = {"stdout": "", "stderr": "", "success": False, "script_path": script_path}

    try:
        # Save the code
        with open(script_path, "w") as f:
            f.write(code)

        # Run the code
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            timeout=90
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
            metrics_path = f"generated/metrics/{run_id}.json"
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
