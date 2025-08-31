from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

ASK_NUM_COURSES, ASK_COURSE_UNIT, ASK_COURSE_GRADE, CALCULATE = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! میخوای معدلت رو حساب کنیم 😊\nچند تا درس داری؟")
    return ASK_NUM_COURSES

async def ask_num_courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num = int(update.message.text)
        if num <= 0:
            raise ValueError
        context.user_data['num_courses'] = num
        context.user_data['current_course'] = 1
        context.user_data['units'] = []
        context.user_data['grades'] = []
        await update.message.reply_text(f"درس {context.user_data['current_course']} چند واحده؟")
        return ASK_COURSE_UNIT
    except:
        await update.message.reply_text("لطفا یک عدد معتبر وارد کن.")
        return ASK_NUM_COURSES

async def ask_course_unit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        units = float(update.message.text)
        if units <= 0:
            raise ValueError
        context.user_data['units'].append(units)
        await update.message.reply_text(f"درس {context.user_data['current_course']} ضریبش چند هست؟")
        return ASK_COURSE_GRADE
    except:
        await update.message.reply_text("لطفا یک عدد معتبر وارد کن.")
        return ASK_COURSE_UNIT

async def ask_course_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        grade = float(update.message.text)
        if grade < 0 or grade > 20:
            raise ValueError
        context.user_data['grades'].append(grade)
        if context.user_data['current_course'] < context.user_data['num_courses']:
            context.user_data['current_course'] += 1
            await update.message.reply_text(f"درس {context.user_data['current_course']} چند واحده؟")
            return ASK_COURSE_UNIT
        else:
            total_units = sum(context.user_data['units'])
            weighted_sum = sum([u * g for u, g in zip(context.user_data['units'], context.user_data['grades'])])
            gpa = round(weighted_sum / total_units, 2)
            msg = f"معدل شما: {gpa}\n"
            if gpa < 12:
                msg += "خاک بر سرت، مشروط شدی 😅"
            elif 12 <= gpa <= 13:
                msg += "از یه جایی آوردیا که نیوفتادی 😏"
            else:
                msg += "آفرین خرخون، قبول شدی 🎉"
            await update.message.reply_text(msg)
            return ConversationHandler.END
    except:
        await update.message.reply_text("لطفا یک عدد معتبر بین 0 تا 20 وارد کن.")
        return ASK_COURSE_GRADE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لغو شد ✅")
    return ConversationHandler.END

if __name__ == "__main__":
    import os
    TOKEN = os.environ.get("BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_NUM_COURSES: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_num_courses)],
            ASK_COURSE_UNIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_course_unit)],
            ASK_COURSE_GRADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_course_grade)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
