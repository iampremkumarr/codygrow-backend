# pyrefly: ignore [missing-import]
from openai import OpenAI
from app.config import settings
from app.models.plan import PlanType
import logging

client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
)


def clean_generated_code(raw_code: str) -> str:
    if raw_code.startswith("```"):
        lines = raw_code.strip().splitlines()
        if lines[0].startswith("```") and lines[-1].startswith("```"):
            return "\n".join(lines[1:-1])
    return raw_code.strip()


def get_model_routing(user_tier: PlanType) -> dict:

    if user_tier in (PlanType.premium,):
        return {
            "primary": "anthropic/claude-3.5-sonnet",
            "fallback": "tencent/hy3:free",
        }

    elif user_tier in (PlanType.pro, PlanType.studio):
        return {
            "primary": "tencent/hy3:free",
            "fallback": "tencent/hy3:free",
        }

    else:
        return {
            "primary": "tencent/hy3:free",
            "fallback": "tencent/hy3:free",
        }


def generate_code_with_openrouter(
    context: str,
    user_prompt: str,
    user_tier: PlanType = PlanType.free,
) -> str:

    models = get_model_routing(user_tier)

    system_prompt = (
        "You are a Python machine learning assistant. "
        "Use pandas, scikit-learn, and matplotlib. "
        "Return ONLY clean executable Python code. "
        "No explanations. No markdown. No backticks. "
        "You MUST load the dataset from the specified 'Dataset CSV File Name' using pandas (e.g., pd.read_csv('filename.csv')). "
        "Do NOT include mock datasets, hardcoded data arrays, or lists in the code. "
        "CRITICAL: You MUST strictly use the exact machine learning algorithm specified by the user in the prompt (e.g., Naive Bayes, SVM, etc.). Do not substitute it with another algorithm like Random Forest. "
        "CRITICAL: If the user requests a Classification algorithm (like Naive Bayes) but the chosen target column contains continuous float values, you MUST convert the target column into discrete categories (e.g., using LabelEncoder or pd.cut) before fitting the model so the code does not crash."
    )

    user_message = f"Dataset context:\n{context}\n\nTask:\n{user_prompt}"

    try:
        response = client.chat.completions.create(
            model=models["primary"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=2000,
        )

        return clean_generated_code(response.choices[0].message.content)

    except Exception as e:
        logging.warning(
            f"Primary model {models['primary']} failed: {e}. Trying fallback..."
        )

        try:
            fallback_response = client.chat.completions.create(
                model=models["fallback"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
                max_tokens=2000,
            )

            return clean_generated_code(
                fallback_response.choices[0].message.content
            )

        except Exception as fallback_e:
            logging.error(f"Fallback also failed: {fallback_e}")
            raise RuntimeError(
                f"OpenRouter failed for both primary and fallback models.\nPrimary: {models['primary']}\nFallback: {models['fallback']}\nError: {fallback_e}"
            )