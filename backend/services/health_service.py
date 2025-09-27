# backend/services/health_service.py

def calculate_bmr(gender, weight, height, age):
    """기초대사량(BMR)을 계산합니다."""
    if gender == 'male':
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

def calculate_tdee(bmr):
    """활동대사량(TDEE)을 계산합니다. (활동 수준은 보통으로 가정)"""
    return bmr * 1.375

def calculate_recommended_calories(tdee, goal):
    """목표에 따른 일일 권장 섭취 칼로리를 계산합니다."""
    if goal == '다이어트':
        return tdee - 500
    elif goal == '근성장':
        return tdee + 300
    else: # 건강유지
        return tdee

def calculate_bmi(weight, height):
    """체질량지수(BMI)를 계산합니다."""
    height_in_meters = height / 100
    bmi = weight / (height_in_meters ** 2)
    
    if bmi < 18.5:
        category = '저체중'
    elif 18.5 <= bmi < 25:
        category = '정상'
    elif 25 <= bmi < 30:
        category = '과체중'
    else:
        category = '비만'
        
    return round(bmi, 2), category

def calculate_recommended_macros(recommended_calories, goal):
    """권장 칼로리에 따른 탄단지(g)를 계산합니다."""
    if goal == '근성장':
        protein_ratio, fat_ratio = 0.30, 0.25
    elif goal == '다이어트':
        protein_ratio, fat_ratio = 0.35, 0.30
    else: # 건강유지
        protein_ratio, fat_ratio = 0.20, 0.25
    
    macros = {
        'protein': round((recommended_calories * protein_ratio) / 4),
        'carbs': round((recommended_calories * (1 - protein_ratio - fat_ratio)) / 4),
        'fat': round((recommended_calories * fat_ratio) / 9)
    }
    return macros