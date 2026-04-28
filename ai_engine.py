from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Meal:
    name: str
    meal_type: str
    diet: str
    ingredients: tuple[str, ...]
    calories: int
    protein: int
    carbs: int
    fats: int
    goal_tags: tuple[str, ...]
    benefits: str
    recipe: str


MEALS: tuple[Meal, ...] = (
    Meal(
        name="Power Oats Bowl",
        meal_type="breakfast",
        diet="veg",
        ingredients=("oats", "milk", "banana", "apple", "almond", "curd"),
        calories=360,
        protein=16,
        carbs=49,
        fats=11,
        goal_tags=("weight_loss", "maintenance", "general_fitness"),
        benefits="High-fiber breakfast that keeps hunger controlled and supports steady energy.",
        recipe="Cook oats in milk or water. Top with banana slices, curd, apple, and almonds.",
    ),
    Meal(
        name="Paneer Protein Wrap",
        meal_type="lunch",
        diet="veg",
        ingredients=("paneer", "roti", "capsicum", "onion", "tomato", "curd"),
        calories=420,
        protein=24,
        carbs=32,
        fats=20,
        goal_tags=("muscle_gain", "maintenance", "general_fitness"),
        benefits="Balanced vegetarian protein meal with good satiety and moderate calories.",
        recipe="Saute paneer with onion, tomato, and capsicum. Roll inside roti and serve with curd.",
    ),
    Meal(
        name="Moong Dal Khichdi",
        meal_type="dinner",
        diet="veg",
        ingredients=("rice", "dal", "moong", "carrot", "peas", "ghee", "jeera"),
        calories=390,
        protein=14,
        carbs=58,
        fats=10,
        goal_tags=("weight_loss", "maintenance", "recovery"),
        benefits="Easy to digest, comforting, and useful for recovery or lighter dinners.",
        recipe="Cook dal and rice with vegetables, jeera, and light seasoning. Finish with a little ghee.",
    ),
    Meal(
        name="Greek Yogurt Fruit Cup",
        meal_type="snack",
        diet="veg",
        ingredients=("curd", "banana", "apple", "berries", "almond", "honey"),
        calories=220,
        protein=12,
        carbs=24,
        fats=8,
        goal_tags=("weight_loss", "maintenance", "general_fitness"),
        benefits="Light snack with protein, probiotics, and natural sweetness.",
        recipe="Mix thick curd with chopped fruits and a small spoon of honey. Top with almonds.",
    ),
    Meal(
        name="Soya Pulao",
        meal_type="lunch",
        diet="veg",
        ingredients=("soya", "rice", "peas", "carrot", "onion", "tomato"),
        calories=430,
        protein=21,
        carbs=55,
        fats=11,
        goal_tags=("muscle_gain", "maintenance", "general_fitness"),
        benefits="Budget-friendly vegetarian protein option with familiar Indian flavors.",
        recipe="Cook soaked soya chunks with rice and mixed vegetables using light spices.",
    ),
    Meal(
        name="Paneer Salad Plate",
        meal_type="dinner",
        diet="veg",
        ingredients=("paneer", "cucumber", "tomato", "lettuce", "corn", "lemon"),
        calories=310,
        protein=20,
        carbs=15,
        fats=18,
        goal_tags=("weight_loss", "maintenance", "general_fitness"),
        benefits="Low-carb vegetarian dinner with freshness and strong satiety.",
        recipe="Lightly grill paneer and toss with cucumber, tomato, corn, lettuce, and lemon dressing.",
    ),
    Meal(
        name="Chana Sprout Bowl",
        meal_type="snack",
        diet="veg",
        ingredients=("chana", "sprouts", "onion", "tomato", "cucumber", "lemon"),
        calories=260,
        protein=15,
        carbs=39,
        fats=5,
        goal_tags=("weight_loss", "maintenance", "general_fitness"),
        benefits="Protein and fiber rich snack that feels fresh and filling.",
        recipe="Mix boiled chana or sprouts with chopped vegetables, lemon juice, and light masala.",
    ),
    Meal(
        name="Vegetable Dalia Bowl",
        meal_type="breakfast",
        diet="veg",
        ingredients=("dalia", "carrot", "peas", "beans", "onion", "tomato"),
        calories=310,
        protein=11,
        carbs=56,
        fats=6,
        goal_tags=("weight_loss", "maintenance", "recovery"),
        benefits="Slow-release carbs with vegetables for a calm, filling breakfast.",
        recipe="Roast dalia lightly, then cook with vegetables and mild spices until soft.",
    ),
    Meal(
        name="Besan Chilla Plate",
        meal_type="breakfast",
        diet="veg",
        ingredients=("besan", "onion", "tomato", "curd", "coriander", "capsicum"),
        calories=340,
        protein=18,
        carbs=38,
        fats=12,
        goal_tags=("muscle_gain", "maintenance", "general_fitness"),
        benefits="High-protein Indian breakfast that is quick and inexpensive.",
        recipe="Prepare besan batter with vegetables, cook like pancakes, and serve with curd.",
    ),
    Meal(
        name="Egg Bhurji Toast",
        meal_type="breakfast",
        diet="eggetarian",
        ingredients=("egg", "bread", "onion", "tomato", "capsicum", "butter"),
        calories=330,
        protein=20,
        carbs=25,
        fats=14,
        goal_tags=("muscle_gain", "maintenance", "general_fitness"),
        benefits="Quick, affordable breakfast with good protein and familiar taste.",
        recipe="Prepare egg bhurji with onion and tomato. Serve with toasted bread.",
    ),
    Meal(
        name="Boiled Egg Salad",
        meal_type="snack",
        diet="eggetarian",
        ingredients=("egg", "cucumber", "tomato", "lettuce", "lemon", "pepper"),
        calories=240,
        protein=18,
        carbs=10,
        fats=14,
        goal_tags=("weight_loss", "maintenance", "recovery"),
        benefits="Protein-rich snack with low calories and very simple preparation.",
        recipe="Slice boiled eggs and mix with vegetables, lemon juice, and pepper.",
    ),
    Meal(
        name="Egg Fried Rice Lite",
        meal_type="dinner",
        diet="eggetarian",
        ingredients=("egg", "rice", "peas", "carrot", "onion", "capsicum"),
        calories=400,
        protein=18,
        carbs=51,
        fats=13,
        goal_tags=("maintenance", "general_fitness"),
        benefits="Comfort meal that uses leftover rice and still keeps macros reasonable.",
        recipe="Stir fry vegetables and egg, then toss with rice and simple seasoning.",
    ),
    Meal(
        name="Masala Omelette Roti",
        meal_type="lunch",
        diet="eggetarian",
        ingredients=("egg", "roti", "onion", "tomato", "capsicum", "curd"),
        calories=410,
        protein=24,
        carbs=34,
        fats=17,
        goal_tags=("muscle_gain", "maintenance", "general_fitness"),
        benefits="Strong protein lunch with familiar ingredients and easy cooking.",
        recipe="Make a vegetable omelette and serve with roti and curd.",
    ),
    Meal(
        name="Chicken Rice Bowl",
        meal_type="lunch",
        diet="non_veg",
        ingredients=("chicken", "rice", "onion", "tomato", "curd", "cucumber"),
        calories=510,
        protein=34,
        carbs=48,
        fats=18,
        goal_tags=("muscle_gain", "maintenance", "general_fitness"),
        benefits="Lean protein focused bowl that supports muscle recovery and energy.",
        recipe="Grill or saute chicken with spices. Serve over rice with curd and cucumber salad.",
    ),
    Meal(
        name="Chicken Soup Dinner",
        meal_type="dinner",
        diet="non_veg",
        ingredients=("chicken", "carrot", "beans", "ginger", "garlic", "pepper"),
        calories=290,
        protein=28,
        carbs=14,
        fats=11,
        goal_tags=("weight_loss", "recovery", "general_fitness"),
        benefits="Light high-protein dinner that feels premium while staying lower in calories.",
        recipe="Simmer chicken with vegetables, ginger, garlic, and pepper until flavorful.",
    ),
    Meal(
        name="Tuna Salad Crunch",
        meal_type="snack",
        diet="non_veg",
        ingredients=("tuna", "cucumber", "tomato", "corn", "lettuce", "lemon"),
        calories=250,
        protein=23,
        carbs=12,
        fats=10,
        goal_tags=("weight_loss", "maintenance", "general_fitness"),
        benefits="Protein-rich snack with low prep time and fresh taste.",
        recipe="Mix tuna with chopped vegetables, lemon juice, and light seasoning.",
    ),
    Meal(
        name="Fish Curry Rice Plate",
        meal_type="dinner",
        diet="non_veg",
        ingredients=("fish", "rice", "tomato", "onion", "garlic", "lemon"),
        calories=460,
        protein=31,
        carbs=47,
        fats=15,
        goal_tags=("maintenance", "general_fitness", "recovery"),
        benefits="Lean protein with balanced carbs and a presentation-friendly Indian meal.",
        recipe="Cook fish in a light tomato-onion curry and serve with measured rice.",
    ),
    Meal(
        name="Chicken Roti Roll",
        meal_type="lunch",
        diet="non_veg",
        ingredients=("chicken", "roti", "onion", "tomato", "cucumber", "curd"),
        calories=450,
        protein=32,
        carbs=35,
        fats=15,
        goal_tags=("muscle_gain", "maintenance", "general_fitness"),
        benefits="Portable high-protein lunch that is useful for busy workdays, travel days, or active routines.",
        recipe="Fill roti with sauteed chicken, vegetables, and curd-based dressing.",
    ),
)

DIET_COMPATIBILITY = {
    "veg": {"veg"},
    "eggetarian": {"veg", "eggetarian"},
    "non_veg": {"veg", "eggetarian", "non_veg"},
}

GOAL_TEXT = {
    "weight_loss": "focuses on fiber, protein, and controlled calories",
    "muscle_gain": "pushes protein and energy for better recovery",
    "maintenance": "keeps calories balanced for a sustainable routine",
    "general_fitness": "supports steady energy and daily activity",
    "recovery": "keeps the meal light, nourishing, and easy to digest",
}

ALIASES = {
    "chapati": "roti",
    "phulka": "roti",
    "dahi": "curd",
    "yogurt": "curd",
    "yoghurt": "curd",
    "lentils": "dal",
    "lentil": "dal",
    "green gram": "moong",
    "moong dal": "moong",
    "gram flour": "besan",
    "chickpea": "chana",
    "chickpeas": "chana",
    "soya chunks": "soya",
    "soy chunks": "soya",
    "peanuts": "peanut",
    "almonds": "almond",
    "eggs": "egg",
    "curds": "curd",
    "brown rice": "rice",
    "boiled rice": "rice",
    "wheat bread": "bread",
    "bell pepper": "capsicum",
}

ALLERGY_GROUPS = {
    "nuts": {"almond", "peanut"},
    "nut": {"almond", "peanut"},
    "peanut": {"peanut"},
    "almond": {"almond"},
    "dairy": {"milk", "curd", "paneer", "ghee", "butter"},
    "lactose": {"milk", "curd", "paneer", "ghee", "butter"},
    "milk": {"milk", "curd", "paneer", "ghee", "butter"},
    "egg": {"egg"},
    "eggs": {"egg"},
    "gluten": {"roti", "bread", "dalia", "besan"},
    "fish": {"fish", "tuna"},
    "seafood": {"fish", "tuna"},
    "soy": {"soya"},
    "soya": {"soya"},
}

KNOWN_INGREDIENTS = frozenset(
    {ingredient for meal in MEALS for ingredient in meal.ingredients}
    | set(ALIASES.values())
    | set(ALLERGY_GROUPS.keys())
)


def normalize_items(raw_items: str | Iterable[str]) -> list[str]:
    """Turn comma/newline separated kitchen text into clean ingredient tokens."""
    if isinstance(raw_items, str):
        text = raw_items.lower()
    else:
        text = ",".join(str(item) for item in raw_items).lower()

    for separator in ["\n", ";", "|", "/", "&"]:
        text = text.replace(separator, ",")

    cleaned: list[str] = []
    for item in text.split(","):
        token = " ".join(item.strip().split())
        if not token:
            continue
        cleaned.append(ALIASES.get(token, token))
    return cleaned


def expand_allergies(allergies_raw: str) -> set[str]:
    blocked: set[str] = set()
    for item in normalize_items(allergies_raw):
        blocked.update(ALLERGY_GROUPS.get(item, {item}))
    return blocked


def _score_meal(meal: Meal, kitchen_items: set[str], goal: str, meal_type: str, diet_preference: str) -> tuple[int, list[str], list[str]]:
    score = 0
    reasons: list[str] = []

    overlap = sorted(set(meal.ingredients).intersection(kitchen_items))
    missing = sorted(set(meal.ingredients).difference(kitchen_items))

    if overlap:
        score += len(overlap) * 5
        reasons.append(f"uses your available items: {', '.join(overlap)}")
    else:
        reasons.append("works as a smart fallback when exact ingredient overlap is low")

    if goal in meal.goal_tags:
        score += 7
        reasons.append(f"matches your goal because it {GOAL_TEXT.get(goal, 'supports your routine')}")

    if meal.meal_type == meal_type:
        score += 5
        reasons.append(f"fits the selected meal timing: {meal_type}")
    else:
        score -= 1

    if meal.diet in DIET_COMPATIBILITY.get(diet_preference, {diet_preference}):
        score += 3
        reasons.append(f"respects your {diet_preference.replace('_', '-')} preference")

    # Prefer simpler recipes when ingredients are missing.
    score -= min(len(missing), 4)
    return score, reasons, missing[:4]


def _health_score_details(meal: Meal, kitchen_items: set[str], goal: str, meal_type: str, missing: list[str]) -> dict:
    """Create an easy-to-explain 0-100 meal score for the UI."""
    overlap_count = len(set(meal.ingredients).intersection(kitchen_items))
    total_ingredients = max(len(meal.ingredients), 1)
    ingredient_points = min(22, int((overlap_count / total_ingredients) * 30))

    goal_points = 22 if goal in meal.goal_tags else 12
    timing_points = 14 if meal.meal_type == meal_type else 8
    protein_points = 18 if meal.protein >= 25 else 14 if meal.protein >= 18 else 10

    if goal == "weight_loss":
        calorie_points = 16 if meal.calories <= 380 else 11 if meal.calories <= 480 else 7
        calorie_label = "controlled calories" if meal.calories <= 420 else "moderate calories"
    elif goal == "muscle_gain":
        calorie_points = 16 if meal.protein >= 22 and meal.calories >= 330 else 11
        calorie_label = "supports protein and energy needs"
    else:
        calorie_points = 14 if 240 <= meal.calories <= 520 else 10
        calorie_label = "balanced calories"

    simplicity_points = 8 if len(missing) <= 1 else 5 if len(missing) <= 3 else 3
    health_score = max(50, min(98, ingredient_points + goal_points + timing_points + protein_points + calorie_points + simplicity_points))

    return {
        "health_score": health_score,
        "score_breakdown": {
            "ingredient_match": f"{overlap_count}/{total_ingredients} key ingredients already available",
            "goal_match": "Strong" if goal in meal.goal_tags else "Moderate",
            "protein_match": "Excellent" if meal.protein >= 25 else "Good" if meal.protein >= 18 else "Light",
            "calorie_fit": calorie_label.title(),
            "allergy_safety": "Safe after allergy filter",
            "prep_effort": "Easy" if len(missing) <= 1 else "Moderate",
        },
    }


def generate_meal_recommendations(
    kitchen_items_raw: str,
    meal_type: str,
    diet_preference: str,
    goal: str,
    allergies_raw: str = "",
) -> dict:
    """Return ranked meal recommendations with nutrition details and plain-English reasoning."""
    meal_type = meal_type if meal_type in {"breakfast", "lunch", "dinner", "snack"} else "breakfast"
    diet_preference = diet_preference if diet_preference in DIET_COMPATIBILITY else "veg"
    goal = goal if goal in GOAL_TEXT else "general_fitness"

    kitchen_items = set(normalize_items(kitchen_items_raw))
    recognized_items = kitchen_items.intersection(KNOWN_INGREDIENTS)
    unrecognized_items = sorted(kitchen_items.difference(KNOWN_INGREDIENTS))
    blocked_ingredients = expand_allergies(allergies_raw)
    allowed_diets = DIET_COMPATIBILITY.get(diet_preference, {diet_preference})

    if not kitchen_items:
        return {
            "summary": "Please enter at least one real kitchen ingredient to generate an accurate recommendation.",
            "input_items": [],
            "recognized_items": [],
            "unrecognized_items": [],
            "blocked_ingredients": sorted(blocked_ingredients),
            "recommendations": [],
        }

    if not recognized_items:
        return {
            "summary": "No recognizable food ingredients matched the offline nutrition database. Please enter common food items such as oats, rice, dal, paneer, egg, chicken, curd, vegetables, or enable the live recipe API.",
            "input_items": sorted(kitchen_items),
            "recognized_items": [],
            "unrecognized_items": unrecognized_items,
            "blocked_ingredients": sorted(blocked_ingredients),
            "recommendations": [],
        }

    candidates: list[tuple[int, Meal, list[str], list[str]]] = []

    for meal in MEALS:
        if meal.diet not in allowed_diets:
            continue
        if blocked_ingredients.intersection(meal.ingredients):
            continue
        score, reasons, missing = _score_meal(meal, kitchen_items, goal, meal_type, diet_preference)
        candidates.append((score, meal, reasons, missing))

    candidates.sort(key=lambda item: (item[0], item[1].protein, -item[1].calories), reverse=True)

    recommendations = []
    for index, (score, meal, reasons, missing) in enumerate(candidates[:3], start=1):
        reason_text = reasons[0] if reasons else "supports your health profile"
        missing_text = ", ".join(missing) if missing else "nothing major"
        explanation = (
            f"This recommendation {GOAL_TEXT.get(goal, 'supports your routine')} and {reason_text}. "
            f"It gives about {meal.protein}g protein, {meal.calories} kcal, and needs {missing_text} extra."
        )
        health_details = _health_score_details(meal, kitchen_items, goal, meal_type, missing)
        recommendations.append(
            {
                "rank": index,
                "score": max(score, 0),
                "health_score": health_details["health_score"],
                "score_breakdown": health_details["score_breakdown"],
                "name": meal.name,
                "meal_type": meal.meal_type,
                "diet": meal.diet,
                "ingredients": list(meal.ingredients),
                "missing_ingredients": missing,
                "calories": meal.calories,
                "protein": meal.protein,
                "carbs": meal.carbs,
                "fats": meal.fats,
                "benefits": meal.benefits,
                "recipe": meal.recipe,
                "reasons": reasons,
                "explanation": explanation,
            }
        )

    if not recommendations:
        return {
            "summary": "No safe meal could be generated for the selected diet/allergy combination. Please update allergy details or add more kitchen items.",
            "input_items": sorted(kitchen_items),
            "recognized_items": sorted(recognized_items),
            "unrecognized_items": unrecognized_items,
            "blocked_ingredients": sorted(blocked_ingredients),
            "recommendations": [],
        }

    best = recommendations[0]
    items_text = ", ".join(sorted(kitchen_items)) if kitchen_items else "your profile defaults"
    summary = (
        f"Best match: {best['name']}. It suits a {diet_preference.replace('_', '-')} routine, "
        f"supports {goal.replace('_', ' ')}, fits {meal_type}, and was ranked using: {items_text}."
    )

    return {
        "summary": summary,
        "input_items": sorted(kitchen_items),
        "recognized_items": sorted(recognized_items),
        "unrecognized_items": unrecognized_items,
        "blocked_ingredients": sorted(blocked_ingredients),
        "recommendations": recommendations,
    }
