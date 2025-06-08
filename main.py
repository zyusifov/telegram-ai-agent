import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from tools import send_message_tool


load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')



# Connect LLM & Agent
llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-4o-mini",
    openai_api_key=OPENAI_API_KEY
)

agent = initialize_agent(
    tools=[send_message_tool],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message
    response = await agent.arun(user_input)

    await update.message.reply_text(response)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()
