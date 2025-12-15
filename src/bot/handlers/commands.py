"""Command handlers for Telegram bot."""

from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.keyboards import get_main_keyboard

if TYPE_CHECKING:
    from src.bot.app import AppContext

router = Router(name="commands")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command.
    
    Sends welcome message with control keyboard.
    """
    await message.reply(
        "Привет! 👋\n\n"
        "Отправляй мне эмодзи-сердечки и я буду менять цвет ленты "
        "в цвет отправленного сердечка.\n\n"
        "🌈 — радуга\n"
        "🌡 — температура",
        reply_markup=get_main_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message, app_context: "AppContext") -> None:
    """Handle /help command."""
    user_id = message.from_user.id if message.from_user else 0
    
    help_text = (
        "Доступные команды:\n\n"
        "/start — начать работу\n"
        "/help — эта справка\n\n"
        "Отправь сердечко чтобы изменить цвет, "
        "или напиши текст (только для админов)."
    )
    
    # Add admin commands for admins
    if app_context.admin_manager.is_admin(user_id):
        help_text += (
            "\n\n👑 Команды админа:\n"
            "/set_new_year_date <YYYY-MM-DD HH:MM:SS> — установить дату Нового года"
        )
    
    # Add admin commands for super admin
    if app_context.admin_manager.is_super_admin(user_id):
        help_text += (
            "\n\n👑 Команды супер-админа:\n"
            "/add_admin <user_id> — добавить админа\n"
            "/remove_admin <user_id> — удалить админа\n"
            "/list_admins — список админов"
        )
    
    await message.reply(help_text, reply_markup=get_main_keyboard())


@router.message(Command("add_admin"))
async def cmd_add_admin(message: Message, app_context: "AppContext") -> None:
    """Handle /add_admin command. Super admin only."""
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    
    # Check if super admin
    if not app_context.admin_manager.is_super_admin(user_id):
        await message.reply("⛔ Только супер-админ может добавлять админов")
        return
    
    # Parse argument
    args = message.text.split() if message.text else []
    if len(args) < 2:
        await message.reply(
            "Использование: /add_admin <user_id>\n\n"
            "Чтобы узнать user_id, попроси пользователя отправить "
            "сообщение боту @userinfobot"
        )
        return
    
    try:
        new_admin_id = int(args[1])
    except ValueError:
        await message.reply("❌ Неверный формат user_id. Должно быть число.")
        return
    
    # Add admin
    if app_context.admin_manager.add_admin(new_admin_id):
        await message.reply(f"✅ Админ {new_admin_id} добавлен")
    else:
        await message.reply(f"ℹ️ Пользователь {new_admin_id} уже является админом")


@router.message(Command("remove_admin"))
async def cmd_remove_admin(message: Message, app_context: "AppContext") -> None:
    """Handle /remove_admin command. Super admin only."""
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    
    # Check if super admin
    if not app_context.admin_manager.is_super_admin(user_id):
        await message.reply("⛔ Только супер-админ может удалять админов")
        return
    
    # Parse argument
    args = message.text.split() if message.text else []
    if len(args) < 2:
        await message.reply("Использование: /remove_admin <user_id>")
        return
    
    try:
        admin_id = int(args[1])
    except ValueError:
        await message.reply("❌ Неверный формат user_id. Должно быть число.")
        return
    
    # Remove admin
    if app_context.admin_manager.remove_admin(admin_id):
        await message.reply(f"✅ Админ {admin_id} удалён")
    else:
        await message.reply(f"ℹ️ Пользователь {admin_id} не найден в списке админов")


@router.message(Command("list_admins"))
async def cmd_list_admins(message: Message, app_context: "AppContext") -> None:
    """Handle /list_admins command. Super admin only."""
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    
    # Check if super admin
    if not app_context.admin_manager.is_super_admin(user_id):
        await message.reply("⛔ Только супер-админ может просматривать список админов")
        return
    
    admins = app_context.admin_manager.list_admins()
    
    if admins:
        admin_list = "\n".join(f"• {admin_id}" for admin_id in sorted(admins))
        await message.reply(f"👥 Список админов:\n\n{admin_list}")
    else:
        await message.reply("ℹ️ Список админов пуст (кроме супер-админа)")


@router.message(Command("set_new_year_date"))
async def cmd_set_new_year_date(message: Message, app_context: "AppContext") -> None:
    """Handle /set_new_year_date command. Admin only."""
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    
    # Check if admin
    if not app_context.admin_manager.is_admin(user_id):
        await message.reply("⛔ Только администраторы могут изменять дату Нового года")
        return
    
    # Parse argument
    args = message.text.split(maxsplit=1) if message.text else []
    if len(args) < 2:
        await message.reply(
            "Использование: /set_new_year_date <YYYY-MM-DD HH:MM:SS>\n\n"
            "Пример: /set_new_year_date 2026-01-01 00:00:00"
        )
        return
    
    try:
        from datetime import datetime
        new_date = datetime.strptime(args[1], "%Y-%m-%d %H:%M:%S")
        
        # Set new date in display manager
        app_context.display_manager.set_new_year_date(new_date)
        
        date_str = new_date.strftime("%Y-%m-%d %H:%M:%S")
        await message.reply(
            f"✅ Дата Нового года установлена: {date_str}\n\n"
            "Изменения применятся автоматически в следующей итерации цикла."
        )
    except ValueError as e:
        await message.reply(
            f"❌ Неверный формат даты.\n\n"
            "Используйте формат: YYYY-MM-DD HH:MM:SS\n"
            "Пример: 2026-01-01 00:00:00"
        )

