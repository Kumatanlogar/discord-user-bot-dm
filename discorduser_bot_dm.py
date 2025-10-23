import os
import sys
import subprocess
import asyncio
import random
from typing import List

# Auto-install required packages
required_packages = ["discord.py", "rich"]
for pkg in required_packages:
    try:
        __import__(pkg.split(".")[0])
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import discord
from rich.console import Console
from rich.table import Table

console = Console()

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

def read_tokens_from_file(path="bot_tokens.txt") -> List[str]:
    tokens = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    tokens.append(line)
    except FileNotFoundError:
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Put one bot token per line.\n")
    return tokens

async def send_dm_with_bot(token: str, recipient_id: int, message: str):
    intents = discord.Intents.none()
    client = discord.Client(intents=intents)
    result = {"token_preview": token[:8] + "...", "success": False, "error": None}

    @client.event
    async def on_ready():
        try:
            user = await client.fetch_user(recipient_id)
            await user.send(message)
            result["success"] = True
        except discord.Forbidden:
            result["error"] = "cannot send DM (user may have DMs disabled)"
        except discord.NotFound:
            result["error"] = "user not found"
        except discord.HTTPException as e:
            result["error"] = f"HTTP exception: {e}"
        except Exception as e:
            result["error"] = f"unexpected exception: {e}"
        finally:
            await asyncio.sleep(random.uniform(1.0, 2.0))
            await client.close()

    try:
        await client.start(token)
    except discord.LoginFailure:
        result["error"] = "invalid token / login failure"
    except Exception as e:
        if result["error"] is None:
            result["error"] = f"start exception: {e}"
        try:
            await client.close()
        except Exception:
            pass

    return result

async def main():
    tokens = read_tokens_from_file("bot_tokens.txt")
    if not tokens:
        console.print("[yellow][➜] No bot tokens found. A sample file was created.[/yellow]")
        return

    clear_console()
    console.print(r"""
 ██████████    ███                                          █████    █████  █████                               ██████████   ██████   ██████
░░███░░░░███  ░░░                                          ░░███    ░░███  ░░███                               ░░███░░░░███ ░░██████ ██████ 
 ░███   ░░███ ████   █████   ██████   ██████  ████████   ███████     ░███   ░███   █████   ██████  ████████     ░███   ░░███ ░███░█████░███ 
 ░███    ░███░░███  ███░░   ███░░███ ███░░███░░███░░███ ███░░███     ░███   ░███  ███░░   ███░░███░░███░░███    ░███    ░███ ░███░░███ ░███  
 ░███    ░███ ░███ ░░█████ ░███ ░░░ ░███ ░███ ░███ ░░░ ░███ ░███     ░███   ░███ ░░█████ ░███████  ░███ ░░░     ░███    ░███ ░███ ░░░  ░███ 
 ░███    ███  ░███  ░░░░███░███  ███░███ ░███ ░███     ░███ ░███     ░███   ░███  ░░░░███░███░░░   ░███         ░███    ███  ░███      ░███ 
 ██████████   █████ ██████ ░░██████ ░░██████  █████    ░░████████    ░░████████   ██████ ░░██████  █████        ██████████   █████     █████
░░░░░░░░░░   ░░░░░ ░░░░░░   ░░░░░░   ░░░░░░  ░░░░░      ░░░░░░░░      ░░░░░░░░   ░░░░░░   ░░░░░░  ░░░░░        ░░░░░░░░░░   ░░░░░     ░░░░░ 
""")
    console.print(f"[blue][TOKENS:[/blue] [bright_blue]{len(tokens)}][/bright_blue]")

    recipient_input = console.input("[➜] Enter the User ID: ").strip()
    if not recipient_input.isdigit():
        console.print("[red][➜] Invalid User ID. Exiting.[/red]")
        return
    recipient_id = int(recipient_input)

    message = console.input("[➜] Enter the message: ").strip()
    if not message:
        console.print("[red][➜] No message entered. Exiting.[/red]")
        return

    console.print("\n[➜] Starting sends...")
    results = []
    random.shuffle(tokens)

    for idx, token in enumerate(tokens, start=1):
        console.print(f"\n[{idx}/{len(tokens)}] Using token preview: {token[:8]}...")
        try:
            res = await send_dm_with_bot(token, recipient_id, message)
            results.append(res)
            if res["success"]:
                console.print(f"[green]SENT[/green] by token preview {res['token_preview']}")
            else:
                console.print(f"[red]FAILED[/red] by token preview {res['token_preview']} — {res['error']}")
        except Exception as e:
            console.print(f"[red]Unexpected error with token preview {token[:8]}...: {e}[/red]")
            results.append({"token_preview": token[:8] + "...", "success": False, "error": f"unexpected {e}"})
        await asyncio.sleep(random.uniform(2.0, 4.0))

    table = Table(title="Send Summary")
    table.add_column("Bot Token (preview)", style="cyan")
    table.add_column("Result", style="green")
    table.add_column("Error (if any)", style="red")
    for r in results:
        table.add_row(r["token_preview"], "SENT" if r["success"] else "FAILED", r["error"] or "-")
    console.print("\n")
    console.print(table)
    console.print("\nAll tasks completed. Press Enter to exit.")
    input()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Exiting.[/yellow]")
