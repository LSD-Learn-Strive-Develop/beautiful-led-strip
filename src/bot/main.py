"""Telegram bot main module."""

from __future__ import annotations

import asyncio
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import TelegramObject

from src.config import get_config
from src.led.controller import LEDController
from src.bot.app import AppContext, ColorStorage, DisplayManager
from src.bot.handlers import commands, messages


async def create_app_context() -> AppContext:
    """Create application context with all dependencies.
    
    Returns:
        Configured AppContext instance
    """
    config = get_config()
    
    # Initialize LED controller
    led_controller = LEDController(config.led)
    
    # Load saved color
    color_storage = ColorStorage(config.data_dir / "color.txt")
    saved_color = color_storage.load_color()
    led_controller.set_color(saved_color)
    
    # Initialize display manager
    display_manager = DisplayManager(led_controller, config)
    
    # Initialize bot
    bot = Bot(token=config.telegram.bot_token)
    
    return AppContext(
        config=config,
        bot=bot,
        led_controller=led_controller,
        color_storage=color_storage,
        display_manager=display_manager,
    )


async def run_display_loop(app_context: AppContext) -> None:
    """Main display update loop.
    
    Handles time display, weather, countdown, and pending actions.
    """
    from src.display import TimeDisplay, CountdownDisplay, TextDisplay
    from src.services import WeatherService
    from src.led.effects import rainbow_cycle
    
    config = app_context.config
    led = app_context.led_controller
    dm = app_context.display_manager
    
    # Initialize display modules
    time_display = TimeDisplay(led)
    countdown_display = CountdownDisplay(led, config.new_year_date)
    text_display = TextDisplay(led)
    weather_service = WeatherService(
        config.weather,
        config.data_dir / "weather.txt",
    )
    
    last_color = led.current_color
    
    while True:
        wait_time = 5.0 if dm.mode.name in ("MAIN", "USER", "FIGHT") else 0.5
        
        # Check for pending text
        pending_text = dm.get_pending_text()
        if pending_text:
            await text_display.show_scrolling_text(pending_text)
            await asyncio.sleep(wait_time)
            continue
        
        # Check for pending actions
        pending_action = dm.get_pending_action()
        if pending_action == "rainbow":
            await rainbow_cycle(led)
            await asyncio.sleep(wait_time)
            continue
        elif pending_action == "temperature":
            temp_str = weather_service.get_temperature_display()
            await text_display.show_static_text(temp_str)
            await asyncio.sleep(wait_time)
            continue
        
        # Mode-specific behavior
        current_color = led.current_color
        color_changed = current_color != last_color
        
        if dm.mode.name == "MAIN":
            if time_display.time_changed() or color_changed or pending_action == "refresh":
                # Show weather
                temp_str = weather_service.get_temperature_display()
                await text_display.show_static_text(temp_str)
                await asyncio.sleep(5)
                
                # Show time
                await time_display.show_current_time()
                await asyncio.sleep(5)
        
        elif dm.mode.name == "USER":
            if color_changed:
                temp_str = weather_service.get_temperature_display()
                await text_display.show_static_text(temp_str)
                await asyncio.sleep(5)
                
                await text_display.show_scrolling_text("С НОВЫМ ГОДОМ")
                
                await time_display.show_current_time()
                await asyncio.sleep(5)
        
        elif dm.mode.name in ("FIGHT", "FIGHT_FAST"):
            if countdown_display.is_complete():
                # Countdown finished!
                dm.exit_countdown()
                await text_display.show_scrolling_text("С НОВЫМ ГОДОМ! 🎉")
                await rainbow_cycle(led)
            else:
                if countdown_display.value_changed() or color_changed or pending_action == "refresh":
                    fast = dm.mode.name == "FIGHT_FAST"
                    await countdown_display.show_countdown(fast)
                
                if countdown_display.is_final_minute():
                    dm.enter_fast_mode()
        
        last_color = current_color
        await asyncio.sleep(0.1)  # Small delay to prevent tight loop


async def run_bot() -> None:
    """Start the Telegram bot and display loop."""
    app_context = await create_app_context()
    
    # Create dispatcher
    dp = Dispatcher()
    
    # Include routers
    dp.include_router(commands.router)
    dp.include_router(messages.router)
    
    # Middleware to inject app_context
    @dp.update.outer_middleware()
    async def inject_context(
        handler: Any,
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["app_context"] = app_context
        return await handler(event, data)
    
    # Start display loop
    async def on_startup() -> None:
        asyncio.create_task(run_display_loop(app_context))
    
    dp.startup.register(on_startup)
    
    # Start polling
    print("Starting bot...")
    await dp.start_polling(app_context.bot)
