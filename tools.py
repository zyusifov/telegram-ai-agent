from functools import lru_cache
import os
from dotenv import load_dotenv
import httpx
from langchain.tools import StructuredTool
from pydantic import BaseModel
from telegram.ext import Application
from bs4 import BeautifulSoup


from utils import escape_markdown_v2


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()


class SendMessageInput(BaseModel):
    user_id: int
    message: str


async def send_telegram_message(user_id: int, message: str) -> dict:
    """Send message to user by id.
    Using only for sending message to another telegram users, not for caller.

    Args:
        user_id: int
        message: str
    Response:
        None
    """

    await telegram_app.bot.send_message(chat_id=user_id, text=escape_markdown_v2(message), parse_mode="MarkdownV2")


# LangChain Tool
send_telegram_message_tool = StructuredTool.from_function(
    func=send_telegram_message,
    name="send_telegram_message",
    description="Send message to Telegram user by ID",
    args_schema=SendMessageInput,
    coroutine=send_telegram_message
)

@lru_cache
async def fetch_ady_data():
    """Fetch data from ticket.ady.az Azerbaijan train ticket site.

    This function is a placeholder and should be implemented to fetch actual data.
    You should consider are today is working day or not, because train schedule is different on weekends.
    """

    async with httpx.AsyncClient() as client:
        response = await client.get("https://ticket.ady.az")
        soup = BeautifulSoup(response.text, "html.parser")
        tablo_section = soup.find("section", id="tablo")
        return tablo_section


# LangChain Tool
fetch_train_data_tool = StructuredTool.from_function(
    func=fetch_ady_data,
    name="fetch_ady_data",
    description="Fetch html content of Azerbaijan train website. Use it for scrap train schedule.",
    coroutine=fetch_ady_data
)
