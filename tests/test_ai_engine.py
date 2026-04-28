from ai_engine import generate_meal_recommendations, normalize_items


def test_normalize_items_handles_common_aliases():
    assert normalize_items("chapati, dahi, eggs") == ["roti", "curd", "egg"]


def test_veg_user_does_not_receive_non_veg_meals():
    payload = generate_meal_recommendations("chicken, rice, curd", "lunch", "veg", "muscle_gain")
    assert payload["recommendations"]
    assert all(meal["diet"] == "veg" for meal in payload["recommendations"])


def test_allergy_filter_removes_blocked_ingredients():
    payload = generate_meal_recommendations("oats, milk, banana", "breakfast", "veg", "weight_loss", "dairy")
    assert payload["recommendations"]
    assert all("milk" not in meal["ingredients"] for meal in payload["recommendations"])
    assert all("curd" not in meal["ingredients"] for meal in payload["recommendations"])


def test_recommendations_include_explainable_health_score():
    payload = generate_meal_recommendations("oats, banana, curd", "breakfast", "veg", "general_fitness")
    top = payload["recommendations"][0]
    assert 0 <= top["health_score"] <= 100
    assert "goal_match" in top["score_breakdown"]
    assert "allergy_safety" in top["score_breakdown"]


def test_invalid_food_words_do_not_generate_false_meals():
    payload = generate_meal_recommendations("stone, paper, plastic", "dinner", "veg", "weight_loss")
    assert payload["recommendations"] == []
    assert payload["unrecognized_items"] == ["paper", "plastic", "stone"]
