import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from tools import send_telegram_message_tool, fetch_train_data_tool
from utils import escape_markdown_v2


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
    tools=[
        send_telegram_message_tool,
        fetch_train_data_tool
    ],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    agent_kwargs={
        "system_message": """You are an AI assistant operating inside a Telegram bot.  
            Your task is to help the user who sent the current message.  
            All your responses must be concise, friendly, and helpful, as they will be sent directly back to the sender via Telegram.

            - **Do not** use the `send_telegram_message(user_id: int, text: str)` tool to respond to the sender. This tool is only for messaging **other** users.
            - To retrieve train schedule data, use the tool `fetch_train_data()`.
            - Always consider **weekends and holidays**, as train schedules may vary.
            - Be aware of different train lines such as `BAKI-XIRDALANSUMQAYIT` and `BAKI-PİRŞAĞISUMQAYIT`.
            - When responding with a train schedule, always include the **date**, **day of the week**, and **month**.
            - Format train results as follows:

            <list_number>. <train_no>: <departure_station> - <arrival_station> | <departure_time_of_selected_station> - <arrival_time_to_selected_station>

            - Use station names from the `data-title` attribute, and ensure Azerbaijani characters are preserved.
            - If a train **does not have an arrival time to selected station**, do **not** include that train in the list."""
    }
)


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message
    response = await agent.arun(user_input)

    await update.message.reply_text(text=escape_markdown_v2(response), parse_mode="MarkdownV2")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()
