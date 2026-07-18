from fastapi import APIRouter
from app.models.schema import CodeGenerationRequest
from app.services.dataset_utils import analyze_dataset
from app.services.llm_handler import generate_code_with_openrouter
from app.services.code_executor import execute_generated_code
from app.services.output_handler import get_visual_outputs
from app.services.auth import get_current_user
from app.models.user import User
from app.models.plan import PlanType
from fastapi import Depends
import os

router = APIRouter()
@router.post("/generate")
def generate_code(request: CodeGenerationRequest, user: User = Depends(get_current_user)):
    # Extract only the base filename to prevent directory traversal
    safe_filename = os.path.basename(request.dataset_filename) if request.dataset_filename else ""
    dataset_path = f"generated/datasets/{safe_filename}"

    if not safe_filename or not os.path.exists(dataset_path):
        return {"error": "Dataset file not found."}

    try:
        dataset_info = analyze_dataset(dataset_path)
        context = f"""
Columns: {dataset_info['headers']}
Types & Nulls: {[ (col['column'], col['dtype'], col['missing']) for col in dataset_info.get('metadata', []) ]}
Shape: {dataset_info.get('shape', 'N/A')}
Suggested Target: {dataset_info.get('suggested_target', 'N/A')}
        """

        # Determine user tier
        active_plan = next((p for p in user.plans if p.is_active), None)
        user_tier = active_plan.plan_type if active_plan else PlanType.free

        code = generate_code_with_openrouter(context, request.prompt, user_tier)
        if safe_filename:
            code = code.replace(
                f"pd.read_csv('{safe_filename}')",
                f"pd.read_csv('generated/datasets/{safe_filename}')"
            )
            if request.dataset_filename and request.dataset_filename != safe_filename:
                code = code.replace(
                    f"pd.read_csv('{request.dataset_filename}')",
                    f"pd.read_csv('generated/datasets/{safe_filename}')"
                )
        # 🚀 NEW: pass task for later use (optional)
        execution_result = execute_generated_code(code, task=request.task.lower())

        return {
            "generated_code": code,
            "output": execution_result["stdout"],
            "errors": execution_result["stderr"],
            "success": execution_result["success"],
            "script_path": execution_result.get("script_path"),
            "metrics": execution_result.get("metrics"),
            "visuals": execution_result.get("visuals", []),
            "metrics_path": execution_result.get("metrics_path")
        }

    except Exception as e:
        return {"error": f"Code generation failed: {str(e)}"}
