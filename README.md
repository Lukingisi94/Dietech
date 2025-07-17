# Diet Planning Backend (Normal & Metabolic Stress)

## Jinsi ya Ku-run Backend

1. Hakikisha una Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run server (development mode):
   ```bash
   uvicorn main:app --reload
   ```
   Server itapatikana kwenye: http://127.0.0.1:8000

## API Endpoint

POST `/calculate-normal-metabolic-diet`

### Sample Input (JSON)
```json
{
  "age": 30,
  "sex": "male",
  "weight": 70,
  "height": 175,
  "activity_factor": 1.3,
  "stress_factor": 1.2,
  "caloric_target": 2200,
  "carbs_percent": 50,
  "protein_percent": 20,
  "fats_percent": 30,
  "clinical_condition": ""
}
```

### Sample Output (JSON)
```json
{
  "BMI": 0,
  "BMR": 0,
  "TDEE": 0,
  "macronutrients": {
    "carbs_g": 0,
    "protein_g": 0,
    "fats_g": 0
  },
  "food_exchanges": {},
  "meal_distribution": {},
  "portion_references": {}
}
```

---

**NB:** Logic ya mahesabu itaongezwa kwenye endpoint hii kulingana na formulas za Excel. 