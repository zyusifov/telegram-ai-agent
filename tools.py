import os
from dotenv import load_dotenv
from langchain.tools import StructuredTool
from pydantic import BaseModel
from telegram.ext import Application


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()


class SendMessageInput(BaseModel):
    user_id: int
    message: str


async def _send_message(user_id: int, message: str) -> dict:
    """Send message to user by id.
    Using only for sending message to another telegram users, not for caller.

    Args:
        user_id: int
        message: str
    Response:
        None
    """

    await telegram_app.bot.send_message(user_id, message)


# LangChain Tool
send_message_tool = StructuredTool.from_function(
    func=_send_message,
    name="send_message",
    description="Send message to Telegram user by ID",
    args_schema=SendMessageInput,
    coroutine=_send_message
)