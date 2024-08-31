import datetime
import random
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, JobQueue

# Constants
LANGUAGE, AGE, GENDER, WEIGHT, HEIGHT, ACTIVITY_LEVEL, WEIGHT_LOSS_GOAL, DONE, RESTART = range(9)
SCHEDULE_TIME = datetime.time(9, 0, 0)

# Initialize the bot
updater = Updater(token='TOKEN', use_context=True)
dispatcher = updater.dispatcher
job_queue = updater.job_queue

# Store user data
user_data_dict = {}
scheduled_jobs = {}

# Nutrition Tips
NUTRITION_TIPS = {
    "en": [
        "Drink at least 8 glasses of water daily to stay hydrated!",
        "Include a variety of fruits and vegetables in your diet to get essential vitamins and minerals.",
        "Balance your meals with protein, carbohydrates, and healthy fats.",
        "Regular physical activity helps maintain a healthy weight and boosts overall health.",
        "Try to limit sugary drinks and snacks, opting for whole foods instead.",
        "Eat more fiber-rich foods like whole grains, legumes, and vegetables to support digestion.",
        "Incorporate healthy fats, such as those from avocados, nuts, and olive oil, into your diet.",
        "Avoid skipping breakfast; it's important to fuel your body for the day ahead.",
        "Practice portion control to avoid overeating and maintain a healthy weight.",
        "Limit your intake of processed and fast foods, which are often high in unhealthy fats and sodium.",
        "Consider eating smaller, more frequent meals throughout the day to keep your energy levels stable.",
        "Choose lean protein sources, such as chicken, fish, and plant-based options, to support muscle growth and repair.",
        "Be mindful of your salt intake; too much sodium can lead to high blood pressure.",
        "Enjoy meals with others whenever possible, as this can encourage healthier eating habits.",
        "Plan your meals ahead of time to make healthier choices and avoid last-minute unhealthy options."
    ],
    "ru": [
        "Пейте не менее 8 стаканов воды в день, чтобы оставаться гидратированными!",
        "Включайте в свой рацион разнообразные фрукты и овощи, чтобы получать необходимые витамины и минералы.",
        "Сбалансируйте приемы пищи, включая белки, углеводы и полезные жиры.",
        "Регулярная физическая активность помогает поддерживать здоровый вес и укрепляет общее здоровье.",
        "Старайтесь ограничивать употребление сладких напитков и закусок, выбирая вместо этого цельные продукты.",
        "Ешьте больше продуктов, богатых клетчаткой, таких как цельные зерна, бобовые и овощи, чтобы поддерживать работу пищеварения.",
        "Включайте в рацион полезные жиры, такие как авокадо, орехи и оливковое масло.",
        "Не пропускайте завтрак; важно запастись энергией на весь день.",
        "Практикуйте контроль порций, чтобы избежать переедания и поддерживать здоровый вес.",
        "Ограничивайте употребление обработанных и фастфуд-продуктов, которые часто содержат вредные жиры и много соли.",
        "Рассмотрите возможность частых, но небольших приемов пищи в течение дня, чтобы поддерживать стабильный уровень энергии.",
        "Выбирайте нежирные источники белка, такие как курица, рыба и растительные продукты, для поддержки роста и восстановления мышц.",
        "Следите за потреблением соли; избыток натрия может привести к повышению артериального давления.",
        "Старайтесь есть вместе с другими людьми, это может способствовать формированию здоровых пищевых привычек.",
        "Планируйте приемы пищи заранее, чтобы делать более здоровый выбор и избегать незапланированных нездоровых вариантов."
    ]
}

# Language dictionaries
LANGUAGE_OPTIONS = {
    "en": {
        "start": "Hello! I'm your diet planner bot. Let's get started.",
        "choose_language": "Please choose your language:",
        "age_prompt": "Step 1 of 6: Please provide your age (e.g., 25):",
        "gender_prompt": "Step 2 of 6: Please specify your gender (Male or Female):",
        "height_prompt": "Step 3 of 6: Please enter your height in cm (e.g., 170):",
        "weight_prompt": "Step 4 of 6: Please enter your weight in kg (e.g., 70):",
        "activity_prompt": "Step 5 of 6: Please select your activity level:",
        "weight_loss_goal_prompt": "Step 6 of 6: Please enter your weight loss goal in kg per week (e.g., 0.5):",
        "age_error": "Please enter a valid age (e.g., 25).",
        "height_error": "Please enter a valid height (e.g., 170 cm).",
        "weight_error": "Please enter a valid weight (e.g., 70 kg).",
        "activity_error": "Invalid activity level. Please choose one from the options provided.",
        "weight_loss_goal_error": "Please enter a valid weight loss goal (e.g., 0.5 kg per week).",
        "weight_loss_goal_warning": "Losing more than 1 kg per week is generally not recommended as it can be unhealthy. "
                                    "Remember, 'Patience is a virtue'. Please consider setting a more gradual goal.",
        "diet_plan_ready": "Your diet plan is ready!\n"
                           "Recommended daily calorie intake: {} calories.\n"
                           "Suggested daily calorie intake for weight loss: {} calories.\n"
                           "Remember: 'Slow and steady wins the race.'",
        "gender_error": "Invalid input. Please select your gender using the buttons.",
        "cancel": "You have canceled the conversation.",
        "recalculate_prompt": "If you would like to recalculate, please press the 'Recalculate' button.",
        "recalculate_button": "Recalculate",
        "restart_prompt": "You've entered incorrect values multiple times. Would you like to start over or use your previous valid inputs?",
        "restart_options": [["Start Over", "Use Previous"]],
        "invalid_input": "Invalid input. Please follow the instructions.",
        "language_options": [["English", "Русский"]],
        "nutrition_tip": "Here's a nutrition tip for you: ",
        "progress_reminder": "It's time to update your progress! How are you doing with your weight loss goal?",
    },
    "ru": {
        "start": "Здравствуйте! Я ваш бот-диетолог. Давайте начнем.",
        "choose_language": "Пожалуйста, выберите ваш язык:",
        "age_prompt": "Шаг 1 из 6: Пожалуйста, укажите ваш возраст (например, 25):",
        "gender_prompt": "Шаг 2 из 6: Пожалуйста, укажите ваш пол (Мужской или Женский):",
        "height_prompt": "Шаг 3 из 6: Пожалуйста, введите ваш рост в см (например, 170):",
        "weight_prompt": "Шаг 4 из 6: Пожалуйста, введите ваш вес в кг (например, 70):",
        "activity_prompt": "Шаг 5 из 6: Пожалуйста, выберите ваш уровень активности:",
        "weight_loss_goal_prompt": "Шаг 6 из 6: Пожалуйста, введите вашу цель по снижению веса в кг в неделю (например, 0.5):",
        "age_error": "Пожалуйста, введите корректный возраст (например, 25).",
        "height_error": "Пожалуйста, введите корректный рост (например, 170 см).",
        "weight_error": "Пожалуйста, введите корректный вес (например, 70 кг).",
        "activity_error": "Неверный уровень активности. Пожалуйста, выберите один из предложенных вариантов.",
        "weight_loss_goal_error": "Пожалуйста, введите корректное значение для вашей цели по снижению веса (например, 0.5 кг в неделю).",
        "weight_loss_goal_warning": "Похудение более чем на 1 кг в неделю обычно не рекомендуется, "
                                    "так как это может быть нездорово. "
                                    "Помните, 'Терпение — добродетель'. Пожалуйста, рассмотрите возможность установки более постепенной цели.",
        "diet_plan_ready": "Ваш план диеты готов!\n"
                           "Рекомендуемое ежедневное потребление калорий: {} калорий.\n"
                           "Предлагаемое ежедневное потребление калорий для снижения веса: {} калорий.\n"
                           "Помните: 'Тише едешь — дальше будешь.'",
        "gender_error": "Неверный ввод. Пожалуйста, выберите ваш пол, используя кнопки.",
        "cancel": "Вы отменили разговор.",
        "recalculate_prompt": "Если вы хотите пересчитать, нажмите кнопку 'Пересчитать'.",
        "recalculate_button": "Пересчитать",
        "restart_prompt": "Вы несколько раз ввели неверные данные. Хотите начать сначала или использовать предыдущие допустимые значения?",
        "restart_options": [["Начать сначала", "Использовать предыдущие"]],
        "invalid_input": "Неверный ввод. Пожалуйста, следуйте инструкциям.",
        "language_options": [["English", "Русский"]],
        "nutrition_tip": "Вот совет по питанию: ",
        "progress_reminder": "Пора обновить ваши данные! Как у вас дела с достижением цели по снижению веса?",
    }
}

# Common functions
def start_conversation(update: Update, text: str, next_state: int, reply_markup=None):
    update.message.reply_text(text, reply_markup=reply_markup)
    return next_state

def get_user_data(update: Update) -> dict:
    user_id = update.effective_user.id
    if user_id not in user_data_dict:
        user_data_dict[user_id] = {}
    return user_data_dict[user_id]

def calculate_bmr(age, gender, weight, height):
    if gender == 'male':
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

def calculate_tdee(bmr, activity_level):
    activity_factors = {
        'sedentary': 1.2,
        'lightly active': 1.375,
        'moderately active': 1.55,
        'very active': 1.725,
        'super active': 1.9
    }
    return bmr * activity_factors.get(activity_level.lower(), 1.2)

# Conversation Handlers
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    user_data = get_user_data(update)
    user_data['language'] = "en"  # Default to English
    user_data['invalid_attempts'] = 0  # Track invalid attempts
    language_options = LANGUAGE_OPTIONS[user_data['language']]

    keyboard = language_options["language_options"]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    return start_conversation(update, language_options["choose_language"], LANGUAGE, reply_markup=reply_markup)

def language(update: Update, context: CallbackContext):
    user_data = get_user_data(update)
    chosen_language = update.message.text.lower()

    if "english" in chosen_language:
        user_data['language'] = "en"
    elif "русский" in chosen_language:
        user_data['language'] = "ru"
    else:
        return start_conversation(update, "Please choose a valid language option:", LANGUAGE)

    language_options = LANGUAGE_OPTIONS[user_data['language']]
    return start_conversation(update, language_options["age_prompt"], AGE)

def age(update: Update, context: CallbackContext):
    user_data = get_user_data(update)
    language_options = LANGUAGE_OPTIONS[user_data['language']]

    try:
        age = int(update.message.text)
        if age > 120 or age < 10:
            user_data['invalid_attempts'] += 1
            if user_data['invalid_attempts'] >= 3:
                return ask_restart(update, context)
            return start_conversation(update, language_options["age_error"], AGE)

        user_data['age'] = age
        user_data['invalid_attempts'] = 0  # Reset invalid attempts
        keyboard = [["Male", "Female"]] if user_data['language'] == "en" else [["Мужской", "Женский"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        return start_conversation(update, language_options["gender_prompt"], GENDER, reply_markup=reply_markup)

    except ValueError:
        user_data['invalid_attempts'] += 1
        if user_data['invalid_attempts'] >= 3:
            return ask_restart(update, context)
        return start_conversation(update, language_options["age_error"], AGE)

def gender(update: Update, context: CallbackContext):
    user_data = get_user_data(update)
    language_options = LANGUAGE_OPTIONS[user_data['language']]
    gender_input = update.message.text.lower()

    if user_data['language'] == "en" and gender_input in ["male", "female"]:
        user_data['gender'] = gender_input
    elif user_data['language'] == "ru" and gender_input in ["мужской", "женский"]:
        user_data['gender'] = "male" if gender_input == "мужской" else "female"
    else:
        user_data['invalid_attempts'] += 1
        if user_data['invalid_attempts'] >= 3:
            return ask_restart(update, context)
        keyboard = [["Male", "Female"]] if user_data['language'] == "en" else [["Мужской", "Женский"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        return start_conversation(update, language_options["gender_error"], GENDER, reply_markup=reply_markup)

    user_data['invalid_attempts'] = 0  # Reset invalid attempts
    return start_conversation(update, language_options["height_prompt"], HEIGHT)

def height(update: Update, context: CallbackContext):
    user_data = get_user_data(update)
    language_options = LANGUAGE_OPTIONS[user_data['language']]

    try:
        height = float(update.message.text)
        if height > 250 or height < 50:
            user_data['invalid_attempts'] += 1
            if user_data['invalid_attempts'] >= 3:
                return ask_restart(update, context)
            return start_conversation(update, language_options["height_error"], HEIGHT)

        user_data['height'] = height
        user_data['invalid_attempts'] = 0  # Reset invalid attempts
        return start_conversation(update, language_options["weight_prompt"], WEIGHT)

    except ValueError:
        user_data['invalid_attempts'] += 1
        if user_data['invalid_attempts'] >= 3:
            return ask_restart(update, context)
        return start_conversation(update, language_options["height_error"], HEIGHT)

def weight(update: Update, context: CallbackContext):
    user_data = get_user_data(update)
    language_options = LANGUAGE_OPTIONS[user_data['language']]

    try:
        weight = float(update.message.text)
        if weight > 180 or weight < 30:
            user_data['invalid_attempts'] += 1
            if user_data['invalid_attempts'] >= 3:
                return ask_restart(update, context)
            return start_conversation(update, language_options["weight_error"], WEIGHT)

        user_data['weight'] = weight
        user_data['invalid_attempts'] = 0  # Reset invalid attempts
        keyboard = [["Sedentary", "Lightly Active"], ["Moderately Active", "Very Active", "Super Active"]] \
            if user_data['language'] == "en" else \
            [["Сидячий", "Малоактивный"], ["Умеренно активный", "Очень активный", "Суперактивный"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        # Show a nutrition tip
        update.message.reply_text(language_options["nutrition_tip"] + random.choice(NUTRITION_TIPS[user_data['language']]))

        return start_conversation(update, language_options["activity_prompt"], ACTIVITY_LEVEL, reply_markup=reply_markup)

    except ValueError:
        user_data['invalid_attempts'] += 1
        if user_data['invalid_attempts'] >= 3:
            return ask_restart(update, context)
        return start_conversation(update, language_options["weight_error"], WEIGHT)

def activity_level(update: Update, context: CallbackContext):
    user_data = get_user_data(update)
    language_options = LANGUAGE_OPTIONS[user_data['language']]
    activity_input = update.message.text.lower()
    valid_activities = ["sedentary", "lightly active", "moderately active", "very active", "super active"] \
        if user_data['language'] == "en" else \
        ["сидячий", "малоактивный", "умеренно активный", "очень активный", "суперактивный"]

    if activity_input in valid_activities:
        user_data['activity_level'] = activity_input
        user_data['invalid_attempts'] = 0  # Reset invalid attempts

        # Show a nutrition tip
        update.message.reply_text(language_options["nutrition_tip"] + random.choice(NUTRITION_TIPS[user_data['language']]))

        return start_conversation(update, language_options["weight_loss_goal_prompt"], WEIGHT_LOSS_GOAL)
    else:
        user_data['invalid_attempts'] += 1
        if user_data['invalid_attempts'] >= 3:
            return ask_restart(update, context)
        keyboard = [["Sedentary", "Lightly Active"], ["Moderately Active", "Very Active", "Super Active"]] \
            if user_data['language'] == "en" else \
            [["Сидячий", "Малоактивный"], ["Умеренно активный", "Очень активный", "Суперактивный"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        return start_conversation(update, language_options["activity_error"], ACTIVITY_LEVEL, reply_markup=reply_markup)

def weight_loss_goal(update: Update, context: CallbackContext):
    user_data = get_user_data(update)
    language_options = LANGUAGE_OPTIONS[user_data['language']]

    try:
        weight_loss_goal = float(update.message.text)
        if weight_loss_goal > 1:
            return start_conversation(update, language_options["weight_loss_goal_warning"], WEIGHT_LOSS_GOAL)
        elif weight_loss_goal <= 0:
            user_data['invalid_attempts'] += 1
            if user_data['invalid_attempts'] >= 3:
                return ask_restart(update, context)
            return start_conversation(update, language_options["weight_loss_goal_error"], WEIGHT_LOSS_GOAL)

        user_data['weight_loss_goal'] = weight_loss_goal
        user_data['invalid_attempts'] = 0  # Reset invalid attempts

        # Calculate BMR and TDEE
        bmr = calculate_bmr(user_data['age'], user_data['gender'], user_data['weight'], user_data['height'])
        tdee = calculate_tdee(bmr, user_data['activity_level'])

        # Convert weight loss goal from kg to calories (1 kg ≈ 7700 calories)
        daily_calories = tdee - (weight_loss_goal * 7700) / 7

        # Show diet plan
        update.message.reply_text(
            language_options["diet_plan_ready"].format(int(tdee), int(daily_calories)),
            reply_markup=ReplyKeyboardRemove()
        )

        # Provide option to recalculate
        keyboard = [[language_options["recalculate_button"]]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        # Schedule weekly progress reminders
        job_queue.run_repeating(send_progress_reminder, interval=604800, first=604800, context=update.message.chat_id)

        return start_conversation(update, language_options["recalculate_prompt"], DONE, reply_markup=reply_markup)

    except ValueError:
        user_data['invalid_attempts'] += 1
        if user_data['invalid_attempts'] >= 3:
            return ask_restart(update, context)
        return start_conversation(update, language_options["weight_loss_goal_error"], WEIGHT_LOSS_GOAL)

def ask_restart(update: Update, context: CallbackContext):
    user_data = get_user_data(update)
    language_options = LANGUAGE_OPTIONS[user_data['language']]

    keyboard = language_options["restart_options"]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    # Present a summary of the previously entered valid data
    summary = "\n".join([f"{key.capitalize()}: {value}" for key, value in user_data.items() if key != 'language' and key != 'invalid_attempts'])

    update.message.reply_text(
        f"{language_options['restart_prompt']}\n\n{summary}",
        reply_markup=reply_markup
    )

    return RESTART

def restart(update: Update, context: CallbackContext):
    user_data = get_user_data(update)
    choice = update.message.text.lower()

    if choice in ["start over", "начать сначала"]:
        return start(update, context)
    elif choice in ["use previous", "использовать предыдущие"]:
        # Restart the process using previous data, starting from weight_loss_goal step
        return weight_loss_goal(update, context)
    else:
        return start_conversation(update, LANGUAGE_OPTIONS[user_data['language']]["invalid_input"], RESTART)

def done(update: Update, context: CallbackContext):
    return start(update, context)  # Restart the process

def cancel(update: Update, context: CallbackContext):
    user_data = get_user_data(update)
    language_options = LANGUAGE_OPTIONS[user_data['language']]
    update.message.reply_text(language_options["cancel"], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def fallback(update: Update, context: CallbackContext):
    user_data = get_user_data(update)
    language_options = LANGUAGE_OPTIONS[user_data['language']]
    update.message.reply_text(language_options["invalid_input"])

def send_progress_reminder(context: CallbackContext):
    chat_id = context.job.context
    user_data = user_data_dict.get(chat_id, {})
    language_options = LANGUAGE_OPTIONS[user_data.get('language', 'en')]
    context.bot.send_message(chat_id=chat_id, text=language_options["progress_reminder"])

# Setup conversation handler
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        LANGUAGE: [MessageHandler(Filters.text & ~Filters.command, language)],
        AGE: [MessageHandler(Filters.text & ~Filters.command, age)],
        GENDER: [MessageHandler(Filters.text & ~Filters.command, gender)],
        HEIGHT: [MessageHandler(Filters.text & ~Filters.command, height)],
        WEIGHT: [MessageHandler(Filters.text & ~Filters.command, weight)],
        ACTIVITY_LEVEL: [MessageHandler(Filters.text & ~Filters.command, activity_level)],
        WEIGHT_LOSS_GOAL: [MessageHandler(Filters.text & ~Filters.command, weight_loss_goal)],
        DONE: [MessageHandler(Filters.text & ~Filters.command, done)],
        RESTART: [MessageHandler(Filters.text & ~Filters.command, restart)],
    },
    fallbacks=[MessageHandler(Filters.text & ~Filters.command, fallback), CommandHandler('cancel', cancel)],
)

# Add the handlers to the dispatcher
dispatcher.add_handler(conversation_handler)

# Start the bot
updater.start_polling()
updater.idle()
