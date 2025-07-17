from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from fastapi import Body
from typing import Dict
from fastapi import Request

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DietInput(BaseModel):
    age: int
    sex: str  # 'male' or 'female'
    weight: float  # kg
    height: float  # cm
    activity_factor: float
    stress_factor: float
    caloric_target: Optional[float] = None
    carbs_percent: float
    protein_percent: float
    fats_percent: float
    clinical_condition: Optional[str] = None
    # Optional fields for special cases
    tbsa: Optional[float] = None  # Total Body Surface Area (burns)
    body_temp: Optional[float] = None  # Body temperature (burns)
    normal_daily_calories: Optional[float] = None  # For burns
    bmr_override: Optional[float] = None  # For burns

class RenalDietInput(BaseModel):
    age: int
    sex: str
    weight: float
    height: float
    activity_factor: float
    stress_factor: float
    caloric_target: Optional[float] = None
    carbs_percent: float
    protein_percent: float
    fats_percent: float
    clinical_condition: Optional[str] = None
    potassium_limit: Optional[float] = 2000  # mg/day
    phosphate_limit: Optional[float] = 1000  # mg/day
    sodium_limit: Optional[float] = 2000     # mg/day
    # Optionally: adjusted weight, etc.

# Food Exchange Calculation
FOOD_GROUPS = [
    {
        "name": "milk_skimmed",
        "carb_per_serv": 12,
        "protein_per_serv": 8,
        "fat_per_serv": 0,
        "calories_per_serv": 80
    },
    {
        "name": "milk_full_cream",
        "carb_per_serv": 12,
        "protein_per_serv": 8,
        "fat_per_serv": 10,
        "calories_per_serv": 150
    },
    {
        "name": "vegetables",
        "carb_per_serv": 5,
        "protein_per_serv": 2,
        "fat_per_serv": 0,
        "calories_per_serv": 25
    },
    {
        "name": "fruits",
        "carb_per_serv": 15,
        "protein_per_serv": 0,
        "fat_per_serv": 0,
        "calories_per_serv": 60
    },
    {
        "name": "sugar",
        "carb_per_serv": 0,
        "protein_per_serv": 0,
        "fat_per_serv": 0,
        "calories_per_serv": 20
    },
    {
        "name": "legumes",
        "carb_per_serv": 15,
        "protein_per_serv": 7,
        "fat_per_serv": 6,
        "calories_per_serv": 88
    },
    {
        "name": "carbohydrates",
        "carb_per_serv": 15,
        "protein_per_serv": 3,
        "fat_per_serv": 0,
        "calories_per_serv": 75
    },
    {
        "name": "protein",
        "carb_per_serv": 0,
        "protein_per_serv": 7,
        "fat_per_serv": 5,
        "calories_per_serv": 75
    },
    {
        "name": "fats",
        "carb_per_serv": 0,
        "protein_per_serv": 0,
        "fat_per_serv": 5,
        "calories_per_serv": 45
    }
]

# Renal food group definitions (per serving)
RENAL_FOOD_GROUPS = [
    {"name": "milk", "carb": 12, "protein": 8, "fat": 5, "k": 150, "na": 120, "po4": 90, "cal": 120},
    {"name": "veg_low_k", "carb": 2, "protein": 1, "fat": 0, "k": 70, "na": 10, "po4": 15, "cal": 15},
    {"name": "veg_mod_k", "carb": 2, "protein": 1, "fat": 0, "k": 150, "na": 10, "po4": 20, "cal": 15},
    {"name": "veg_high_k", "carb": 2, "protein": 1, "fat": 0, "k": 270, "na": 10, "po4": 25, "cal": 15},
    {"name": "fruit_low_k", "carb": 10, "protein": 0, "fat": 0, "k": 80, "na": 2, "po4": 10, "cal": 40},
    {"name": "fruit_mod_k", "carb": 10, "protein": 0, "fat": 0, "k": 150, "na": 2, "po4": 15, "cal": 40},
    {"name": "fruit_high_k", "carb": 10, "protein": 0, "fat": 0, "k": 250, "na": 2, "po4": 20, "cal": 40},
    {"name": "legumes", "carb": 15, "protein": 7, "fat": 6, "k": 200, "na": 5, "po4": 60, "cal": 90},
    {"name": "sugar", "carb": 5, "protein": 0, "fat": 0, "k": 0, "na": 0, "po4": 0, "cal": 20},
    {"name": "drinks", "carb": 10, "protein": 0, "fat": 0, "k": 10, "na": 5, "po4": 0, "cal": 40},
    {"name": "starch_low_k", "carb": 15, "protein": 3, "fat": 0, "k": 30, "na": 5, "po4": 20, "cal": 70},
    {"name": "starch_high_k", "carb": 15, "protein": 3, "fat": 0, "k": 120, "na": 5, "po4": 40, "cal": 70},
    {"name": "starch_low_po4", "carb": 15, "protein": 3, "fat": 0, "k": 30, "na": 5, "po4": 10, "cal": 70},
    {"name": "starch_high_po4", "carb": 15, "protein": 3, "fat": 0, "k": 30, "na": 5, "po4": 60, "cal": 70},
    {"name": "protein_low_po4", "carb": 0, "protein": 7, "fat": 5, "k": 60, "na": 50, "po4": 65, "cal": 75},
    {"name": "protein_high_po4", "carb": 0, "protein": 7, "fat": 5, "k": 60, "na": 50, "po4": 120, "cal": 75},
    {"name": "fats", "carb": 0, "protein": 0, "fat": 5, "k": 0, "na": 0, "po4": 0, "cal": 45},
]

RENAL_PORTION_REFERENCES = {
    "pdf_link": "https://drive.google.com/file/d/1f7hKLphgVfiBsMwks534DlJlmQLV827E/view?usp=drivesdk"
}

def calculate_food_exchanges(servings_dict):
    exchanges = {}
    for group in FOOD_GROUPS:
        name = group["name"]
        servings = servings_dict.get(name, 0)
        exchanges[name] = {
            "servings": servings,
            "carbs_g": servings * group["carb_per_serv"],
            "protein_g": servings * group["protein_per_serv"],
            "fats_g": servings * group["fat_per_serv"],
            "calories": servings * group["calories_per_serv"]
        }
    return exchanges

# Diabetes medication meal carb distribution
MEDICATION_CARB_DISTRIBUTION = {
    "sulfonylureas": [0.3, 0.0, 0.3, 0.0, 0.3, 0.1],  # BF, MMS, Lunch, AS, Dinner, LNS
    "meglitinides": [0.3, 0.0, 0.3, 0.0, 0.3, 0.1],
    "biguanides": [0.33, 0.0, 0.34, 0.0, 0.33, 0.0],
    "glitazones": [0.33, 0.0, 0.34, 0.0, 0.33, 0.0],
    "metformin_sulfonylurea": [0.3, 0.0, 0.3, 0.0, 0.3, 0.1],
    "fast_acting": [0.2, 0.1, 0.25, 0.1, 0.25, 0.1],
    "intermediate_long_acting_bed": [0.2, 0.1, 0.3, 0.0, 0.3, 0.1],
    "biphasic": [0.2, 0.1, 0.3, 0.0, 0.3, 0.1],
    "intermediate_long_acting_breakfast": [0.2, 0.1, 0.3, 0.1, 0.3, 0.0],
    "default": [0.25, 0.05, 0.25, 0.05, 0.25, 0.15]  # fallback
}

MEALS = ["BF", "MMS", "Lunch", "AS", "Dinner", "LNS"]

def calculate_meal_distribution(total_carbs, medication_type):
    key = medication_type.lower().replace(" ", "_") if medication_type else "default"
    distribution = MEDICATION_CARB_DISTRIBUTION.get(key, MEDICATION_CARB_DISTRIBUTION["default"])
    meal_dist = {}
    for i, meal in enumerate(MEALS):
        meal_dist[meal] = round(total_carbs * distribution[i], 2)
    return meal_dist

def calculate_fluid_requirement(weight_kg):
    if weight_kg <= 10:
        return weight_kg * 100
    elif weight_kg <= 20:
        return 1000 + (weight_kg - 10) * 50
    else:
        return 1500 + (weight_kg - 20) * 20

def calculate_pediatric_energy(age_years, weight, height, sex, activity_factor):
    # Returns (eer, kcal_per_kg)
    if age_years < 0.25:  # 0-3 months
        eer = ((89 * weight) - 100) + 175
    elif age_years < 0.5:  # 4-6 months
        eer = ((89 * weight) - 100) + 56
    elif age_years < 1:  # 7-12 months
        eer = ((89 * weight) - 100) + 22
    elif age_years < 2:  # 1-2 years
        eer = ((89 * weight) - 100) + 20
    elif age_years < 3:  # 2-3 years
        eer = ((89 * weight) - 100) + 20
    elif age_years < 9:  # 3-8 years
        if sex == 'male':
            eer = (88.5 - (61.9 * age_years)) + (activity_factor * ((26.7 * weight) + (903 * (height / 100)))) + 20
        else:
            eer = (135.3 - (30.8 * age_years)) + (activity_factor * ((10 * weight) + (934 * (height / 100)))) + 20
    elif age_years <= 18:  # 9-18 years
        if sex == 'male':
            eer = (88.5 - (61.9 * age_years)) + (activity_factor * ((26.7 * weight) + (903 * (height / 100)))) + 25
        else:
            eer = (135.3 - (30.8 * age_years)) + (activity_factor * ((10 * weight) + (934 * (height / 100)))) + 25
    else:
        eer = None
    kcal_per_kg = eer / weight if eer and weight else None
    return eer, kcal_per_kg

def calculate_burn_energy(weight, tbsa, bmr, sex, normal_daily_calories, body_temp, age_years):
    # Toronto Equation (adults)
    if sex == 'male':
        toronto = -4343 + (10.5 * tbsa) + (0.23 * normal_daily_calories) + (0.84 * bmr) + (114 * body_temp) - (4.5 * tbsa)
    else:
        toronto = -4343 + (10.5 * tbsa) + (0.23 * normal_daily_calories) + (0.84 * bmr) + (114 * body_temp) - (4.5 * tbsa)
    # Curreli (adults)
    curreli = (25 * weight) + (40 * tbsa)
    # Curreli Junior (children)
    if age_years < 1:
        curreli_junior = None  # Needs RDA kcals input
    elif age_years < 4:
        curreli_junior = None  # Needs RDA kcals input
    elif age_years < 16:
        curreli_junior = None  # Needs RDA kcals input
    else:
        curreli_junior = None
    return {
        "toronto": toronto,
        "curreli": curreli,
        "curreli_junior": curreli_junior
    }

def auto_food_servings(carbs_g, protein_g, fats_g):
    # Estimate servings for each group automatically (simple logic, can be improved)
    # Start with standard allocations, then allocate residuals
    servings = {
        "milk_skimmed": 2,
        "milk_full_cream": 0,
        "vegetables": 3,
        "fruits": 2,
        "sugar": 1,
        "legumes": 1,
    }
    # Calculate carbs, protein, fats from above
    milk_carb = servings["milk_skimmed"] * 12
    milk_protein = servings["milk_skimmed"] * 8
    veg_carb = servings["vegetables"] * 5
    veg_protein = servings["vegetables"] * 2
    fruit_carb = servings["fruits"] * 15
    legume_carb = servings["legumes"] * 15
    legume_protein = servings["legumes"] * 7
    # Residual carbs (to carbs group)
    used_carb = milk_carb + veg_carb + fruit_carb + legume_carb
    servings["carbohydrates"] = max(round((carbs_g - used_carb) / 15), 0)
    # Residual protein (to protein group)
    used_protein = milk_protein + veg_protein + legume_protein
    servings["protein"] = max(round((protein_g - used_protein) / 7), 0)
    # Residual fats (to fats group)
    # Assume no fats in above, all to fats group
    servings["fats"] = max(round(fats_g / 5), 0)
    return servings

PORTION_REFERENCES = {
    "milk": [
        "1 cup (250ml) of fat free milk",
        "2/3 cup (175ml) of fat free yoghurt",
        "1/2 cup evaporated milk or 1 scoop of ice-cream"
    ],
    "protein": [
        "20g low fat cheese",
        "2 tbsp peanut butter",
        "Matchbox size piece of meat/chicken/fillet",
        "1 egg (albumin 5.5g) chicken thigh"
    ],
    "vegetables": [
        "1/2 cup of cooked vegetables without sweetcorn",
        "1 cup of raw vegetables"
    ],
    "fruits": [
        "1 medium (tennis ball size) fresh fruit",
        "1/2 cup of fresh chopped fruit",
        "1/2 cup unsweetened fruit juice"
    ],
    "starch": [
        "1 slice of wholemeal bread",
        "1/2 cup cooked rice/pasta",
        "1/2 cup cooked porridge/cassava",
        "1/2 cup sweet potato"
    ],
    "fats": [
        "1 tsp oil",
        "1 tsp butter/margarine",
        "1 tbsp salad dressing",
        "5 nuts (1 Tbsp)",
        "1 tbsp shredded coconut"
    ]
}

def auto_renal_servings(carbs_g, protein_g, fats_g, k_limit, po4_limit, na_limit):
    # Simple greedy allocation: prioritize low K/PO4 groups, fill macros, don't exceed limits
    servings = {g["name"]: 0 for g in RENAL_FOOD_GROUPS}
    macros = {"carb": carbs_g, "protein": protein_g, "fat": fats_g}
    electrolytes = {"k": 0, "po4": 0, "na": 0}
    # Try to fill macros with lowest K/PO4 groups first
    for g in RENAL_FOOD_GROUPS:
        max_serv = 0
        if g["carb"] > 0:
            max_serv = min(macros["carb"] // g["carb"], 10)
        elif g["protein"] > 0:
            max_serv = min(macros["protein"] // g["protein"], 10)
        elif g["fat"] > 0:
            max_serv = min(macros["fat"] // g["fat"], 10)
        max_serv = int(max_serv)
        for _ in range(max_serv):
            # Check if adding this serving would exceed any electrolyte limit
            if (electrolytes["k"] + g["k"] > k_limit) or (electrolytes["po4"] + g["po4"] > po4_limit) or (electrolytes["na"] + g["na"] > na_limit):
                break
            servings[g["name"]] += 1
            macros["carb"] -= g["carb"]
            macros["protein"] -= g["protein"]
            macros["fat"] -= g["fat"]
            electrolytes["k"] += g["k"]
            electrolytes["po4"] += g["po4"]
            electrolytes["na"] += g["na"]
    return servings, electrolytes

@app.post("/calculate-normal-metabolic-diet")
def calculate_diet(input: DietInput):
    # BMI
    height_m = input.height / 100
    bmi = input.weight / (height_m ** 2)

    # BMR (Harris-Benedict or override)
    if input.bmr_override is not None:
        bmr = input.bmr_override
    else:
        if input.sex.lower() == 'male':
            bmr = 66.5 + (13.75 * input.weight) + (5.003 * input.height) - (6.75 * input.age)
        else:
            bmr = 655.1 + (9.563 * input.weight) + (1.85 * input.height) - (4.676 * input.age)

    # TDEE
    tdee = bmr * input.activity_factor * input.stress_factor

    # Caloric target
    total_calories = input.caloric_target if input.caloric_target else tdee

    # Macronutrient grams
    carbs_g = ((input.carbs_percent / 100) * total_calories) / 4
    protein_g = ((input.protein_percent / 100) * total_calories) / 4
    fats_g = ((input.fats_percent / 100) * total_calories) / 9

    # Auto servings allocation
    servings_dict = auto_food_servings(carbs_g, protein_g, fats_g)
    food_exchanges = calculate_food_exchanges(servings_dict)

    # Dynamic residuals
    residuals = {
        "carbs_g": round(carbs_g - sum([food_exchanges[g]["carbs_g"] for g in food_exchanges]), 2),
        "protein_g": round(protein_g - sum([food_exchanges[g]["protein_g"] for g in food_exchanges]), 2),
        "fats_g": round(fats_g - sum([food_exchanges[g]["fats_g"] for g in food_exchanges]), 2)
    }

    # Meal distribution (automatic, based on clinical_condition)
    meal_distribution = calculate_meal_distribution(carbs_g, input.clinical_condition)

    # Portion references (automatic)
    portion_references = PORTION_REFERENCES

    # Fluid requirements (automatic)
    fluid_requirement_ml = calculate_fluid_requirement(input.weight)

    # Pediatric energy requirements (automatic if age < 19)
    pediatric_energy = None
    if input.age < 19:
        pediatric_energy = {}
        eer, kcal_per_kg = calculate_pediatric_energy(
            input.age, input.weight, input.height, input.sex, input.activity_factor
        )
        pediatric_energy["EER"] = eer
        pediatric_energy["kcal_per_kg"] = kcal_per_kg

    # Burn calculations (automatic if clinical_condition is burn)
    burn_energy = None
    if input.clinical_condition and "burn" in input.clinical_condition.lower():
        burn_energy = calculate_burn_energy(
            input.weight,
            tbsa=input.tbsa if input.tbsa is not None else 20,
            bmr=bmr,
            sex=input.sex,
            normal_daily_calories=input.normal_daily_calories if input.normal_daily_calories is not None else 2000,
            body_temp=input.body_temp if input.body_temp is not None else 37,
            age_years=input.age
        )

    return {
        "success": True,
        "message": "Calculation successful.",
        "data": {
            "BMI": round(bmi, 2),
            "BMR": round(bmr, 2),
            "TDEE": round(tdee, 2),
            "macronutrients": {
                "carbs_g": round(carbs_g, 2),
                "protein_g": round(protein_g, 2),
                "fats_g": round(fats_g, 2)
            },
            "food_exchanges": food_exchanges,
            "meal_distribution": meal_distribution,
            "portion_references": portion_references,
            "fluid_requirement_ml": fluid_requirement_ml,
            "pediatric_energy": pediatric_energy,
            "burn_energy": burn_energy,
            "residuals": residuals,
            # MEAL PLAN EXAMPLE
            "meal_plan": {
                "breakfast": [
                    {"food": "Oats", "quantity": "1 cup"},
                    {"food": "Milk", "quantity": "1 glass"}
                ],
                "lunch": [
                    {"food": "Rice", "quantity": "1 cup"},
                    {"food": "Chicken", "quantity": "100g"},
                    {"food": "Vegetables", "quantity": "1 cup"}
                ],
                "dinner": [
                    {"food": "Sweet Potato", "quantity": "1 cup"},
                    {"food": "Fish", "quantity": "100g"},
                    {"food": "Salad", "quantity": "1 cup"}
                ],
                "snacks": [
                    {"food": "Apple", "quantity": "1"},
                    {"food": "Almonds", "quantity": "10 pieces"}
                ]
            }
        }
    }

@app.post("/calculate/normal_user")
async def calculate_normal_user(request: Request):
    data = await request.json()
    # Fill in default values for advanced fields if not provided
    data.setdefault('activity_factor', 1.2)
    data.setdefault('stress_factor', 1.0)
    data.setdefault('carbs_percent', 50)
    data.setdefault('protein_percent', 20)
    data.setdefault('fats_percent', 30)
    # Fill in other required fields with defaults if needed
    # Use DietInput model for validation
    input_data = DietInput(**data)
    return calculate_diet(input_data)

@app.post("/calculate/dietitian")
def calculate_dietitian(input: DietInput):
    return calculate_diet(input)

@app.post("/calculate-renal-diet")
def calculate_renal_diet(input: RenalDietInput = Body(...)):
    # BMI
    height_m = input.height / 100
    bmi = input.weight / (height_m ** 2)
    # BMR (Harris-Benedict)
    if input.sex.lower() == 'male':
        bmr = 66.5 + (13.75 * input.weight) + (5.003 * input.height) - (6.75 * input.age)
    else:
        bmr = 655.1 + (9.563 * input.weight) + (1.85 * input.height) - (4.676 * input.age)
    # TDEE
    tdee = bmr * input.activity_factor * input.stress_factor
    # Caloric target
    total_calories = input.caloric_target if input.caloric_target else tdee
    # Macronutrient grams
    carbs_g = ((input.carbs_percent / 100) * total_calories) / 4
    protein_g = ((input.protein_percent / 100) * total_calories) / 4
    fats_g = ((input.fats_percent / 100) * total_calories) / 9
    # Auto servings allocation (renal)
    servings_dict, electrolyte_totals = auto_renal_servings(
        carbs_g, protein_g, fats_g,
        input.potassium_limit, input.phosphate_limit, input.sodium_limit
    )
    # Calculate food exchanges (with electrolytes)
    food_exchanges = {}
    for g in RENAL_FOOD_GROUPS:
        s = servings_dict[g["name"]]
        food_exchanges[g["name"]] = {
            "servings": s,
            "carbs_g": s * g["carb"],
            "protein_g": s * g["protein"],
            "fats_g": s * g["fat"],
            "calories": s * g["cal"],
            "k_mg": s * g["k"],
            "na_mg": s * g["na"],
            "po4_mg": s * g["po4"]
        }
    # Residuals
    residuals = {
        "carbs_g": round(carbs_g - sum([food_exchanges[g]["carbs_g"] for g in food_exchanges]), 2),
        "protein_g": round(protein_g - sum([food_exchanges[g]["protein_g"] for g in food_exchanges]), 2),
        "fats_g": round(fats_g - sum([food_exchanges[g]["fats_g"] for g in food_exchanges]), 2)
    }
    # Meal distribution (reuse logic from normal, based on clinical_condition)
    meal_distribution = calculate_meal_distribution(carbs_g, input.clinical_condition)
    # Fluid requirements
    fluid_requirement_ml = calculate_fluid_requirement(input.weight)
    # Response
    return {
        "success": True,
        "message": "Renal diet calculation successful.",
        "data": {
        "BMI": round(bmi, 2),
        "BMR": round(bmr, 2),
        "TDEE": round(tdee, 2),
        "macronutrients": {
            "carbs_g": round(carbs_g, 2),
            "protein_g": round(protein_g, 2),
            "fats_g": round(fats_g, 2)
        },
        "food_exchanges": food_exchanges,
        "meal_distribution": meal_distribution,
            "fluid_requirement_ml": fluid_requirement_ml,
            "electrolyte_totals": electrolyte_totals,
            "portion_references": RENAL_PORTION_REFERENCES,
            "residuals": residuals,
            # MEAL PLAN EXAMPLE
            "meal_plan": {
                "breakfast": [
                    {"food": "Oats", "quantity": "1 cup"},
                    {"food": "Milk", "quantity": "1 glass"}
                ],
                "lunch": [
                    {"food": "Rice", "quantity": "1 cup"},
                    {"food": "Chicken", "quantity": "100g"},
                    {"food": "Vegetables", "quantity": "1 cup"}
                ],
                "dinner": [
                    {"food": "Sweet Potato", "quantity": "1 cup"},
                    {"food": "Fish", "quantity": "100g"},
                    {"food": "Salad", "quantity": "1 cup"}
                ],
                "snacks": [
                    {"food": "Apple", "quantity": "1"},
                    {"food": "Almonds", "quantity": "10 pieces"}
                ]
            }
        }
    } 