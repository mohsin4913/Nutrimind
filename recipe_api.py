from __future__ import annotations

import os
import re
from html import unescape
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover - handled gracefully for clearer local errors
    requests = None  # type: ignore[assignment]

from ai_engine import expand_allergies, normalize_items


SPOONACULAR_SEARCH_URL = "https://api.spoonacular.com/recipes/complexSearch"
SPOONACULAR_INFO_URL = "https://api.spoonacular.com/recipes/{recipe_id}/information"


DIET_TO_API = {
    "veg": "vegetarian",
    "eggetarian": "vegetarian",
    "non_veg": "",
}

MEAL_TYPE_TO_API = {
    "breakfast": "breakfast",
    "lunch": "main course",
    "dinner": "main course",
    "snack": "snack",
}

ALLERGY_TO_INTOLERANCE = {
    "milk": "dairy",
    "curd": "dairy",
    "paneer": "dairy",
    "ghee": "dairy",
    "butter": "dairy",
    "egg": "egg",
    "roti": "gluten",
    "bread": "gluten",
    "dalia": "gluten",
    "peanut": "peanut",
    "almond": "tree nut",
    "fish": "seafood",
    "tuna": "seafood",
    "soya": "soy",
}


class RecipeAPIError(RuntimeError):
    """Raised when the external recipe API cannot return useful data."""


def _strip_html(value: str | None) -> str:
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", " ", value)
    text = unescape(text)
    return " ".join(text.split())


def _nutrition_lookup(recipe: dict[str, Any], nutrient_name: str) -> float | None:
    nutrition = recipe.get("nutrition") or {}
    nutrients = nutrition.get("nutrients") or []
    for nutrient in nutrients:
        if str(nutrient.get("name", "")).lower() == nutrient_name.lower():
            try:
                return round(float(nutrient.get("amount", 0)), 1)
            except (TypeError, ValueError):
                return None
    return None


def _extract_steps(recipe: dict[str, Any]) -> list[str]:
    steps: list[str] = []
    for instruction_group in recipe.get("analyzedInstructions") or []:
        for step in instruction_group.get("steps") or []:
            text = _strip_html(step.get("step"))
            if text:
                steps.append(text)
    if steps:
        return steps[:8]

    plain_instructions = _strip_html(recipe.get("instructions"))
    if plain_instructions:
        split_steps = [part.strip() for part in re.split(r"(?<=[.!?])\s+", plain_instructions) if part.strip()]
        return split_steps[:8]

    return []


def _extract_ingredients(recipe: dict[str, Any]) -> list[str]:
    ingredients: list[str] = []
    for item in recipe.get("extendedIngredients") or recipe.get("missedIngredients") or []:
        original = _strip_html(item.get("original") or item.get("name"))
        if original:
            ingredients.append(original)
    return ingredients[:12]


def _normalise_api_recipe(recipe: dict[str, Any], *, rank: int) -> dict[str, Any]:
    calories = _nutrition_lookup(recipe, "Calories")
    protein = _nutrition_lookup(recipe, "Protein")
    carbs = _nutrition_lookup(recipe, "Carbohydrates")
    fats = _nutrition_lookup(recipe, "Fat")

    title = _strip_html(recipe.get("title")) or "External recipe result"
    ready_in = recipe.get("readyInMinutes")
    servings = recipe.get("servings")
    ingredients = _extract_ingredients(recipe)
    steps = _extract_steps(recipe)
    source_url = recipe.get("sourceUrl") or recipe.get("spoonacularSourceUrl") or ""
    summary = _strip_html(recipe.get("summary"))

    return {
        "rank": rank,
        "id": recipe.get("id"),
        "name": title,
        "title": title,
        "image": recipe.get("image") or "",
        "source_url": source_url,
        "ready_in_minutes": ready_in,
        "servings": servings,
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fats": fats,
        "ingredients": ingredients,
        "steps": steps,
        "summary": summary[:420] if summary else "Recipe found from the external food API.",
        "recipe": " ".join(steps[:3]) if steps else "Open the source recipe link for full cooking steps.",
    }


def _intolerances_from_allergies(allergies_raw: str) -> str:
    blocked = expand_allergies(allergies_raw)
    intolerances = sorted({ALLERGY_TO_INTOLERANCE[item] for item in blocked if item in ALLERGY_TO_INTOLERANCE})
    return ",".join(intolerances)


def search_recipe_api(
    kitchen_items_raw: str,
    meal_type: str,
    diet_preference: str,
    goal: str,
    allergies_raw: str = "",
    *,
    number: int = 3,
    timeout_seconds: int = 8,
) -> dict[str, Any]:
    """Search Spoonacular for real recipes from user ingredients.

    The app stays presentation-safe: if no key/network/API result exists, callers receive an
    explanatory status and can continue with the offline recommendation engine.
    """
    api_key = os.environ.get("SPOONACULAR_API_KEY", "").strip()
    if not api_key:
        return {
            "enabled": False,
            "status": "disabled",
            "summary": "External recipe API is disabled. Add SPOONACULAR_API_KEY to enable live recipe search.",
            "recipes": [],
        }

    if requests is None:
        return {
            "enabled": False,
            "status": "missing_dependency",
            "summary": "The requests package is missing. Run pip install -r requirements.txt.",
            "recipes": [],
        }

    ingredients = normalize_items(kitchen_items_raw)
    if not ingredients:
        return {
            "enabled": True,
            "status": "empty_input",
            "summary": "Add ingredients before using live recipe search.",
            "recipes": [],
        }

    diet = DIET_TO_API.get(diet_preference, "")
    api_type = MEAL_TYPE_TO_API.get(meal_type, "")
    intolerances = _intolerances_from_allergies(allergies_raw)

    query_parts = ingredients[:6]
    if goal == "weight_loss":
        query_parts.append("healthy low calorie")
    elif goal == "muscle_gain":
        query_parts.append("high protein")

    params: dict[str, Any] = {
        "apiKey": api_key,
        "query": " ".join(query_parts),
        "includeIngredients": ",".join(ingredients[:8]),
        "number": max(1, min(number, 5)),
        "ranking": 1,
        "ignorePantry": True,
        "instructionsRequired": True,
        "addRecipeInformation": True,
        "addRecipeNutrition": True,
        "fillIngredients": True,
    }
    if diet:
        params["diet"] = diet
    if api_type:
        params["type"] = api_type
    if intolerances:
        params["intolerances"] = intolerances

    try:
        response = requests.get(SPOONACULAR_SEARCH_URL, params=params, timeout=timeout_seconds)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:  # type: ignore[union-attr]
        return {
            "enabled": True,
            "status": "api_error",
            "summary": f"Live recipe API could not be reached: {exc.__class__.__name__}. Offline AI recommendations are still available.",
            "recipes": [],
        }
    except ValueError:
        return {
            "enabled": True,
            "status": "bad_response",
            "summary": "Live recipe API returned an unreadable response. Offline AI recommendations are still available.",
            "recipes": [],
        }

    raw_results = data.get("results") or []
    detailed_results: list[dict[str, Any]] = []
    for item in raw_results[: max(1, min(number, 5))]:
        recipe = item
        recipe_id = item.get("id")
        has_steps = bool(_extract_steps(recipe))
        has_ingredients = bool(_extract_ingredients(recipe))
        if recipe_id and (not has_steps or not has_ingredients):
            try:
                info_response = requests.get(
                    SPOONACULAR_INFO_URL.format(recipe_id=recipe_id),
                    params={"apiKey": api_key, "includeNutrition": True},
                    timeout=timeout_seconds,
                )
                info_response.raise_for_status()
                recipe = info_response.json()
            except (requests.RequestException, ValueError):  # type: ignore[union-attr]
                recipe = item
        detailed_results.append(recipe)

    recipes = [_normalise_api_recipe(recipe, rank=index) for index, recipe in enumerate(detailed_results, start=1)]
    recipes = [recipe for recipe in recipes if recipe["name"]]

    if not recipes:
        return {
            "enabled": True,
            "status": "no_results",
            "summary": "No live recipe matched those ingredients, diet, and allergy filters. Try simpler ingredients or remove strict filters.",
            "recipes": [],
        }

    return {
        "enabled": True,
        "status": "success",
        "summary": f"Found {len(recipes)} live recipe result(s) from the external food API.",
        "recipes": recipes,
    }
