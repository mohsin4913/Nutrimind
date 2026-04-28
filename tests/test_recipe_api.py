from recipe_api import search_recipe_api


def test_recipe_api_is_safe_without_key(monkeypatch):
    monkeypatch.delenv("SPOONACULAR_API_KEY", raising=False)
    payload = search_recipe_api("oats, banana", "breakfast", "veg", "general_fitness")
    assert payload["enabled"] is False
    assert payload["status"] == "disabled"
    assert payload["recipes"] == []
