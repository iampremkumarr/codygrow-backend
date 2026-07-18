from fastapi import APIRouter, Depends
from app.models.schema import CodeGenerationRequest
from app.services.dataset_utils import analyze_dataset
from app.services.llm_handler import generate_code_with_openrouter
from app.services.code_executor import execute_generated_code

from app.services.auth import get_current_user
from app.models.user import User
from app.models.plan import PlanType
from app.config import settings

import os

router = APIRouter()
@router.post("/generate")
def generate_code(request: CodeGenerationRequest, user: User = Depends(get_current_user)):
    # Extract only the base filename to prevent directory traversal
    safe_filename = os.path.basename(request.dataset_filename) if request.dataset_filename else ""
    dataset_path = os.path.join(settings.DATASETS_DIR, safe_filename)

    if not safe_filename or not os.path.exists(dataset_path):
        return {"error": "Dataset file not found."}

    try:
        dataset_info = analyze_dataset(dataset_path)
        context = f"""
Dataset CSV File Name: {safe_filename}
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
            # Ensure we use forward slashes for Python path in generated script
            datasets_dir_for_code = settings.DATASETS_DIR.replace("\\", "/")
            dataset_path_for_code = f"{datasets_dir_for_code}/{safe_filename}"
            
            # Robustly replace any pd.read_csv(...) references to load from the correct datasets folder
            import re
            for name in list(set([safe_filename, request.dataset_filename])):
                if name:
                    pattern = rf"pd\.read_csv\(\s*['\"](?:[^'\"]*/)?{re.escape(name)}['\"]"
                    code = re.sub(pattern, f"pd.read_csv('{dataset_path_for_code}'", code)
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
