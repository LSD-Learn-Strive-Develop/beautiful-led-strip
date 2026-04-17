"""Telegram bot main module."""

from __future__ import annotations

import asyncio
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import TelegramObject

from src.config import get_config
from src.led.controller import LEDController
from src.bot.app import AppContext, ColorStorage, DisplayManager
from src.bot.admin_manager import AdminManager
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
    
    # Initialize admin manager
    admin_manager = AdminManager(
        config.data_dir / "admins.txt",
        config.telegram.admin_id,
    )
    
    # Initialize bot
    bot = Bot(token=config.telegram.bot_token)
    
    return AppContext(
        config=config,
        bot=bot,
        led_controller=led_controller,
        color_storage=color_storage,
        display_manager=display_manager,
        admin_manager=admin_manager,
    )


async def run_display_loop(app_context: AppContext) -> None:
    """Main display update loop.
    
    Handles time display, weather, countdown, slots, and pending actions.
    """
    from src.display import TimeDisplay, CountdownDisplay, TextDisplay, SlotsDisplay
    from src.services import WeatherService
    from src.led.effects import rainbow_cycle
    
    config = app_context.config
    led = app_context.led_controller
    dm = app_context.display_manager
    
    # Initialize display modules
    time_display = TimeDisplay(led)
    countdown_display = CountdownDisplay(led, dm.new_year_date)
    text_display = TextDisplay(led)
    slots_display = SlotsDisplay(led)
    weather_service = WeatherService(
        config.weather,
        config.data_dir / "weather.txt",
    )
    
    last_color = led.current_color
    last_rainbow_mode = False
    last_new_year_date = dm.new_year_date
    
    while True:
        wait_time = 5.0 if dm.mode.name in ("MAIN", "USER", "FIGHT") else 0.5
        
        # Check if New Year date was updated
        if dm.new_year_date != last_new_year_date:
            countdown_display.set_target_date(dm.new_year_date)
            last_new_year_date = dm.new_year_date
        
        # Sync rainbow mode from display manager to LED controller
        led.rainbow_mode = dm.rainbow_mode
        
        # Check for pending slots (highest priority)
        pending_slots = dm.get_pending_slots()
        if pending_slots:
            dm.set_slots_active(True)
            try:
                is_jackpot = await slots_display.show_slots(pending_slots)
                # Wait a bit to show the result before continuing
                await asyncio.sleep(2.0)
            finally:
                dm.set_slots_active(False)
            # Force refresh to return to normal display
            dm.request_refresh()
            continue
        
        # Check for pending text
        pending_text = dm.get_pending_text()
        if pending_text:
            dm.set_display_busy(True)
            try:
                await text_display.show_scrolling_text(pending_text)
                await asyncio.sleep(wait_time)
            finally:
                dm.set_display_busy(False)
            continue
        
        # Check for pending actions
        pending_action = dm.get_pending_action()
        if pending_action == "temperature":
            dm.set_display_busy(True)
            try:
                temp_str = weather_service.get_temperature_display()
                await text_display.show_static_text(temp_str)
                await asyncio.sleep(wait_time)
            finally:
                dm.set_display_busy(False)
            continue
        
        # Mode-specific behavior
        current_color = led.current_color
        color_changed = current_color != last_color
        rainbow_changed = led.rainbow_mode != last_rainbow_mode
        time_changed = time_display.time_changed()
        
        # Rainbow animation: 5 seconds of cycling when first enabled
        if rainbow_changed and led.rainbow_mode:
            import time as time_module
            
            # First, draw the time to set up which pixels are lit
            await time_display.show_current_time(fast=True)
            
            animation_start = time_module.time()
            animation_duration = 5.0  # seconds
            
            while time_module.time() - animation_start < animation_duration:
                # Just update colors of already-lit pixels (smooth, no flicker)
                led.update_colors()
                await asyncio.sleep(0.03)  # ~30 FPS
        
        if dm.mode.name == "MAIN":
            if time_changed:
                # Check if current color is black and replace with random existing color
                if led.current_color == (0, 0, 0):
                    random_color = dm.get_random_color_from_existing()
                    led.set_color(random_color)
                    app_context.color_storage.save_color(random_color)

                # New minute: show weather (if fresh), then time
                if weather_service.get_temperature() is not None:
                    temp_str = weather_service.get_temperature_display()
                    await text_display.show_static_text(temp_str)
                    await asyncio.sleep(5)

                await time_display.show_current_time()
                await asyncio.sleep(5)
            elif color_changed or rainbow_changed or pending_action == "refresh":
                # Color or rainbow mode changed: just redraw time
                await time_display.show_current_time()

        elif dm.mode.name == "USER":
            if time_changed:
                # Check if current color is black and replace with random existing color
                if led.current_color == (0, 0, 0):
                    random_color = dm.get_random_color_from_existing()
                    led.set_color(random_color)
                    app_context.color_storage.save_color(random_color)

                # New minute: show weather (if fresh), greeting, then time
                if weather_service.get_temperature() is not None:
                    temp_str = weather_service.get_temperature_display()
                    await text_display.show_static_text(temp_str)
                    await asyncio.sleep(5)
                
                # Enable rainbow mode for greeting text
                dm.enable_rainbow()
                led.rainbow_mode = True  # Set immediately for text display
                await text_display.show_scrolling_text("С НОВЫМ ГОДОМ")
                # Disable rainbow mode after text display
                dm.disable_rainbow()
                led.rainbow_mode = False  # Set immediately for time display
                
                await time_display.show_current_time()
                await asyncio.sleep(5)
            elif color_changed or rainbow_changed:
                # Color or rainbow mode changed: just redraw time
                await time_display.show_current_time()
        
        elif dm.mode.name in ("FIGHT", "FIGHT_FAST"):
            if countdown_display.is_complete():
                # Countdown finished!
                dm.exit_countdown()
                # Enable rainbow mode for greeting text
                dm.enable_rainbow()
                led.rainbow_mode = True
                await text_display.show_scrolling_text("ПУНК! С НОВЫМ ГОДОМ!!!")
                # Keep rainbow mode enabled for rainbow cycle
                await rainbow_cycle(led)
            else:
                if countdown_display.value_changed() or color_changed or rainbow_changed or pending_action == "refresh":
                    fast = dm.mode.name == "FIGHT_FAST"
                    await countdown_display.show_countdown(fast)
                
                if countdown_display.is_final_minute():
                    dm.enter_fast_mode()
        
        last_color = current_color
        last_rainbow_mode = led.rainbow_mode
        await asyncio.sleep(0.1)  # Small delay to prevent tight loop


async def _resilient_polling(dp: Dispatcher, bot: Bot) -> None:
    """Run Telegram polling, retrying indefinitely on network errors.

    Telegram may be unreachable (blocked network, outage). Instead of
    letting the exception propagate and kill the process, we log and
    retry with exponential backoff so the display loop keeps running.
    """
    retry_delay = 5.0
    max_retry_delay = 300.0

    while True:
        try:
            await dp.start_polling(bot, handle_signals=False)
            return
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(
                f"Telegram polling error: {e!r}. "
                f"Retrying in {retry_delay:.0f}s..."
            )
            try:
                await asyncio.sleep(retry_delay)
            except asyncio.CancelledError:
                raise
            retry_delay = min(retry_delay * 2, max_retry_delay)


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

    print("Starting bot...")

    # Start display loop independently so time keeps displaying even if
    # Telegram is unreachable (e.g. blocked).
    display_task = asyncio.create_task(run_display_loop(app_context))
    polling_task = asyncio.create_task(_resilient_polling(dp, app_context.bot))

    try:
        done, _ = await asyncio.wait(
            {display_task, polling_task},
            return_when=asyncio.FIRST_EXCEPTION,
        )
        for task in done:
            task.result()
    finally:
        for task in (display_task, polling_task):
            if not task.done():
                task.cancel()
        for task in (display_task, polling_task):
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass
        await app_context.bot.session.close()
