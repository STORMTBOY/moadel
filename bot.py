from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# مراحل گفتگو
ASK_NUM_COURSES, ASK_GRADE, ASK_UNIT, ASK_COEF = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! میخوای معدلت رو حساب کنیم 😊\nچند تا درس داری؟\nبرای لغو هر زمان میتونی /cancel بزنی."
    )
    return ASK_NUM_COURSES

async def ask_num_courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num = int(update.message.text)
        if num <= 0:
            raise ValueError
        context.user_data['num_courses'] = num
        context.user_data['current_course'] = 1
        context.user_data['grades'] = []
        context.user_data['units'] = []
        context.user_data['coefs'] = []
        await update.message.reply_text(f"درس 1، نمره‌ات چند شد؟")
        return ASK_GRADE
    except:
        await update.message.reply_text("لطفا یک عدد معتبر وارد کن.")
        return ASK_NUM_COURSES

async def ask_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        grade = float(update.message.text)
        if not (0 <= grade <= 20):
            raise ValueError
        context.user_data['grades'].append(grade)
        await update.message.reply_text(f"درس {context.user_data['current_course']} چند واحده؟")
        return ASK_UNIT
    except:
        await update.message.reply_text("لطفا یک عدد معتبر بین 0 تا 20 وارد کن.")
        return ASK_GRADE

async def ask_unit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        unit = float(update.message.text)
        if unit <= 0:
            raise ValueError
        context.user_data['units'].append(unit)
        await update.message.reply_text(f"درس {context.user_data['current_course']} ضریبش چند هست؟")
        return ASK_COEF
    except:
        await update.message.reply_text("لطفا یک عدد معتبر وارد کن.")
        return ASK_UNIT

async def ask_coef(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        coef = float(update.message.text)
        if coef <= 0:
            raise ValueError
        context.user_data['coefs'].append(coef)
        # آماده شدن برای درس بعدی یا محاسبه معدل
        if context.user_data['current_course'] < context.user_data['num_courses']:
            context.user_data['current_course'] += 1
            await update.message.reply_text(f"درس {context.user_data['current_course']}، نمره‌ات چند شد؟")
            return ASK_GRADE
        else:
            # محاسبه معدل
            total_weighted = sum([g * u * c for g, u, c in zip(context.user_data['grades'], context.user_data['units'], context.user_data['coefs'])])
            total_weight = sum([u * c for u, c in zip(context.user_data['units'], context.user_data['coefs'])])
            gpa = round(total_weighted / total_weight, 2)
            # پیام نهایی
            if gpa < 12:
                result_msg = "ریدی مشروط شدی که 😅"
            elif 12 <= gpa <= 13:
                result_msg = "از یه جایی آوردی نیوفتادیا 😏"
            else:
                result_msg = "آفرین خرخون قبول شدی درسخونعلی 🎉"
            await update.message.reply_text(f"معدل شما: {gpa}\n{result_msg}\n\nاگر دوباره خواستی معدلت رو حساب کنی، /start رو بزن!")
            return ConversationHandler.END
    except:
        await update.message.reply_text("لطفا یک عدد معتبر وارد کن.")
        return ASK_COEF

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لغو شد ✅\nاگر دوباره خواستی معدلت رو حساب کنی، /start رو بزن!")
    return ConversationHandler.END

if __name__ == "__main__":
    import os
    TOKEN = os.environ.get("BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_NUM_COURSES: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_num_courses)],
            ASK_GRADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_grade)],
            ASK_UNIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_unit)],
            ASK_COEF: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_coef)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
