import discord
from discord.ext import commands
import asyncio
import os
from datetime import datetime, timedelta
import re
from typing import Optional
from dotenv import load_dotenv

from conversation_memory import ConversationMemory
from gemini_search import GeminiSearchBot

# Load environment variables
load_dotenv()

class GeminiDiscordBot(commands.Bot):
    def __init__(self):
        # Bot setup with intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # Initialize components
        self.memory = ConversationMemory()
        self.gemini = GeminiSearchBot(os.getenv('GEMINI_API_KEY'))
        self.monitored_channels = set()
        
        # Load monitored channels from environment or default
        channel_id = os.getenv('CHANNEL_ID')
        if channel_id:
            self.monitored_channels.add(int(channel_id))
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for messages to search 🔍"
            )
        )
    
    async def on_message(self, message):
        # Ignore bot's own messages
        if message.author == self.user:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Auto-search in monitored channels (if not a command)
        if (message.channel.id in self.monitored_channels and 
            not message.content.startswith('!') and
            len(message.content) > 10):  # Only for substantial messages
            
            await self.auto_search(message)
    
    async def auto_search(self, message):
        """Automatically search and respond to messages in monitored channels"""
        try:
            # Show typing indicator
            async with message.channel.typing():
                # Get conversation context
                context = self.memory.get_recent_context(
                    str(message.author.id),
                    str(message.channel.id),
                    hours=24,
                    limit=5
                )
                
                # Process the message with Gemini
                result = await self.gemini.process_message(message.content, context)
                
                # Store in memory
                self.memory.add_conversation(
                    user_id=str(message.author.id),
                    channel_id=str(message.channel.id),
                    message=message.content,
                    response=result['response'],
                    search_query='; '.join(result['search_queries'])
                )
                
                # Send response
                if len(result['response']) > 2000:
                    # Split long messages
                    chunks = [result['response'][i:i+1900] 
                             for i in range(0, len(result['response']), 1900)]
                    for chunk in chunks:
                        await message.reply(chunk)
                else:
                    await message.reply(result['response'])
                    
        except Exception as e:
            print(f"Error in auto_search: {e}")
            await message.reply("Sorry, I encountered an error while processing your message.")

# Bot Commands
@commands.command(name='search')
async def manual_search(ctx, *, query):
    """Manually trigger a search with a specific query"""
    try:
        async with ctx.typing():
            # Get conversation context
            context = ctx.bot.memory.get_recent_context(
                str(ctx.author.id),
                str(ctx.channel.id),
                hours=24,
                limit=5
            )
            
            # Process the query
            result = await ctx.bot.gemini.process_message(query, context)
            
            # Store in memory
            ctx.bot.memory.add_conversation(
                user_id=str(ctx.author.id),
                channel_id=str(ctx.channel.id),
                message=query,
                response=result['response'],
                search_query='; '.join(result['search_queries'])
            )
            
            # Create embed for better formatting
            embed = discord.Embed(
                title="🔍 Search Results",
                description=result['response'],
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(
                name="Search Queries Used",
                value='\n'.join([f"• {q}" for q in result['search_queries']]),
                inline=False
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            
            await ctx.reply(embed=embed)
            
    except Exception as e:
        await ctx.reply(f"Error performing search: {str(e)}")

@commands.command(name='logs')
async def get_logs(ctx, date_filter: Optional[str] = None):
    """
    Get conversation logs. Usage:
    !logs - Get today's logs
    !logs yesterday - Get yesterday's logs
    !logs 2024-01-15 - Get logs for specific date
    !logs 7days - Get logs for last 7 days
    """
    try:
        # Parse date filter
        if not date_filter or date_filter.lower() == 'today':
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = datetime.now()
            title = "Today's Logs"
            
        elif date_filter.lower() == 'yesterday':
            start_date = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            title = "Yesterday's Logs"
            
        elif date_filter.endswith('days'):
            days = int(re.findall(r'\d+', date_filter)[0])
            start_date = datetime.now() - timedelta(days=days)
            end_date = datetime.now()
            title = f"Last {days} Days Logs"
            
        elif re.match(r'\d{4}-\d{2}-\d{2}', date_filter):
            # Specific date format YYYY-MM-DD
            target_date = datetime.strptime(date_filter, '%Y-%m-%d')
            start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            title = f"Logs for {date_filter}"
            
        else:
            await ctx.reply("Invalid date format. Use: today, yesterday, 7days, or YYYY-MM-DD")
            return
        
        # Get logs from database
        logs = ctx.bot.memory.get_logs_by_date_range(
            str(ctx.channel.id),
            start_date,
            end_date
        )
        
        if not logs:
            await ctx.reply(f"No logs found for {title.lower()}")
            return
        
        # Format logs
        log_text = []
        for log in logs:
            timestamp = datetime.fromisoformat(log['timestamp']).strftime('%H:%M:%S')
            user_mention = f"<@{log['user_id']}>"
            log_text.append(f"**{timestamp}** {user_mention}: {log['message'][:100]}{'...' if len(log['message']) > 100 else ''}")
            if log['response']:
                log_text.append(f"🤖: {log['response'][:100]}{'...' if len(log['response']) > 100 else ''}")
            log_text.append("")  # Empty line for separation
        
        # Split into multiple messages if too long
        full_text = '\n'.join(log_text)
        
        if len(full_text) <= 1900:
            embed = discord.Embed(
                title=f"📋 {title}",
                description=full_text,
                color=0x0099ff,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"{len(logs)} conversations found")
            await ctx.reply(embed=embed)
        else:
            # Send as multiple messages
            await ctx.reply(f"📋 **{title}** ({len(logs)} conversations)")
            
            chunks = [full_text[i:i+1900] for i in range(0, len(full_text), 1900)]
            for i, chunk in enumerate(chunks):
                embed = discord.Embed(
                    description=chunk,
                    color=0x0099ff
                )
                embed.set_footer(text=f"Part {i+1}/{len(chunks)}")
                await ctx.send(embed=embed)
                
    except Exception as e:
        await ctx.reply(f"Error retrieving logs: {str(e)}")

@commands.command(name='monitor')
@commands.has_permissions(manage_channels=True)
async def toggle_monitoring(ctx, action: str = "status"):
    """
    Manage channel monitoring. Usage:
    !monitor status - Check monitoring status
    !monitor on - Enable monitoring for this channel
    !monitor off - Disable monitoring for this channel
    """
    channel_id = ctx.channel.id
    
    if action.lower() == "on":
        ctx.bot.monitored_channels.add(channel_id)
        await ctx.reply("✅ Auto-search monitoring enabled for this channel!")
        
    elif action.lower() == "off":
        ctx.bot.monitored_channels.discard(channel_id)
        await ctx.reply("❌ Auto-search monitoring disabled for this channel.")
        
    else:  # status
        status = "🟢 Enabled" if channel_id in ctx.bot.monitored_channels else "🔴 Disabled"
        await ctx.reply(f"Auto-search monitoring status: {status}")

@commands.command(name='help')
async def help_command(ctx):
    """Show help information"""
    embed = discord.Embed(
        title="🤖 Gemini Discord Search Bot Help",
        description="I'm a Discord bot that uses Gemini 2.0 Flash to search the web and provide intelligent responses!",
        color=0x00ff00
    )
    
    embed.add_field(
        name="🔍 Auto Search",
        value="I automatically search and respond to messages in monitored channels",
        inline=False
    )
    
    embed.add_field(
        name="📝 Commands",
        value="""
        `!search <query>` - Manual web search
        `!logs [date]` - Get conversation logs
        `!monitor [on/off/status]` - Manage channel monitoring
        `!help` - Show this help message
        """,
        inline=False
    )
    
    embed.add_field(
        name="📅 Log Examples",
        value="""
        `!logs` - Today's logs
        `!logs yesterday` - Yesterday's logs
        `!logs 2024-01-15` - Specific date
        `!logs 7days` - Last 7 days
        """,
        inline=False
    )
    
    embed.set_footer(text="Powered by Gemini 2.5 Flash")
    await ctx.reply(embed=embed)

# Add commands to bot
def setup_bot():
    bot = GeminiDiscordBot()
    bot.add_command(manual_search)
    bot.add_command(get_logs)
    bot.add_command(toggle_monitoring)
    bot.add_command(help_command)
    return bot

# Run the bot
if __name__ == "__main__":
    bot = setup_bot()
    
    # Add error handler
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.CommandNotFound):
            pass  # Ignore unknown commands
        else:
            print(f"Command error: {error}")
            await ctx.reply("❌ An error occurred while processing the command.")
    
    # Run the bot
    bot.run(os.getenv('DISCORD_TOKEN'))