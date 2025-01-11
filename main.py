import logging
import asyncio
from pyrogram import Client, filters
from datetime import datetime
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from secret import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot
app = Client(
    "mobile_uan_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# Initialize MongoDB
mongo = AsyncIOMotorClient(config.MONGODB_URI)
db = mongo.mobile_uan_bot

# Helper functions
async def is_sudo(user_id: int) -> bool:
    """Check if user is sudo"""
    sudo = await db.sudos.find_one({"user_id": user_id})
    return bool(sudo and sudo.get("limit", 0) > 0)

async def get_sudo_limit(user_id: int) -> int:
    """Get remaining limit for sudo user"""
    sudo = await db.sudos.find_one({"user_id": user_id})
    return sudo.get("limit", 0) if sudo else 0

async def decrease_limit(user_id: int) -> bool:
    """Decrease user's limit by 1"""
    result = await db.sudos.update_one(
        {"user_id": user_id, "limit": {"$gt": 0}},
        {"$inc": {"limit": -1}}
    )
    return result.modified_count > 0

async def fetch_uan_data(mobile: str) -> dict:
    """Fetch UAN data from API"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            config.API_URL,
            headers={
                "secretKey": config.SECRET_KEY,
                "clientId": config.CLIENT_ID,
                "Content-Type": "application/json"
            },
            json={"mobileNumber": mobile}
        ) as response:
            return await response.json()

# Command handlers
@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Handle /start command"""
    await message.reply(
        "👋 Welcome to Mobile-UAN Bot!\n\n"
        "Use /info <10-digit mobile> to fetch UAN details.\n"
        "Contact owner for sudo access."
    )


@app.on_message(filters.command("addsudo"))
async def add_sudo(client, message):
    """Handle /addsudo command"""
    if message.from_user.id != config.OWNER_ID:
        await message.reply("❌ Only owner can use this command.")
        return

    try:
        # Check command format
        if len(message.command) != 3:
            await message.reply("Usage: /addsudo <user_id> <limit>")
            return

        user_id = int(message.command[1])
        limit = int(message.command[2])

        if limit <= 0:
            await message.reply("Limit must be greater than 0")
            return

        # Add or update sudo user
        await db.sudos.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "limit": limit,
                    "added_by": message.from_user.id,
                    "added_at": datetime.utcnow()
                }
            },
            upsert=True
        )

        await message.reply(f"✅ User {user_id} added as sudo with limit: {limit}")

    except ValueError:
        await message.reply("Invalid user ID or limit value.")
    except Exception as e:
        logger.error(f"Error adding sudo: {str(e)}")
        await message.reply("An error occurred while adding sudo user.")

@app.on_message(filters.command("removesudo"))
async def remove_sudo(client, message):
    """Handle /removesudo command"""
    if message.from_user.id != config.OWNER_ID:
        await message.reply("❌ Only owner can use this command.")
        return

    if len(message.command) != 2:
        await message.reply("Usage: /removesudo <user_id>")
        return

    try:
        user_id = int(message.command[1])
        result = await db.sudos.delete_one({"user_id": user_id})
        
        if result.deleted_count:
            await message.reply(f"✅ User {user_id} removed from sudo list.")
        else:
            await message.reply(f"User {user_id} was not a sudo user.")
            
    except ValueError:
        await message.reply("Invalid user ID.")
    except Exception as e:
        logger.error(f"Error removing sudo: {str(e)}")
        await message.reply("An error occurred while removing sudo user.")

@app.on_message(filters.command("sudolist"))
async def sudo_list(client, message):
    """Handle /sudolist command"""
    if message.from_user.id != config.OWNER_ID:
        await message.reply("❌ Only owner can use this command.")
        return

    sudo_users = await db.sudos.find().to_list(length=None)
    
    if not sudo_users:
        await message.reply("No sudo users found.")
        return

    text = "📋 **Sudo Users List**\n\n"
    for user in sudo_users:
        text += f"User ID: `{user['user_id']}`\n"
        text += f"Remaining Limit: {user['limit']}\n"
        text += f"Added at: {user['added_at'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    await message.reply(text)

async def main():
    """Start the bot"""
    # Create indexes
    await db.sudos.create_index("user_id", unique=True)
    await db.usage_logs.create_index("user_id")
    await db.usage_logs.create_index("timestamp")
    
    logger.info("Bot started successfully!")


@app.on_message(filters.command("info"))
async def info_command(client, message):
    """Handle /info command"""
    user_id = message.from_user.id
    
    # Check if user is sudo
    if not await is_sudo(user_id):
        await message.reply("❌ **You don't have access to use this command.**")
        return

    # Check command format
    if len(message.command) != 2:
        await message.reply("📝 **Usage:** /info <10-digit mobile number>")
        return

    mobile = message.command[1]
    
    # Validate mobile number
    if not mobile.isdigit() or len(mobile) != 10:
        await message.reply("⚠️ **Please provide a valid 10-digit mobile number.**")
        return

    # Check and decrease limit
    limit = await get_sudo_limit(user_id)
    if limit <= 0:
        await message.reply("❌ **Your usage limit has been exhausted.**")
        return

    try:
        # Send request to API
        result = await fetch_uan_data(mobile)
        
        # Decrease limit
        await decrease_limit(user_id)
        
        # Check if the API response is successful
        if result.get("code") == 200:
            data = result.get("result", {})

            # Extract and format data
            personal_info = data.get("personal_info", {})
            phone_info = data.get("phone_info", [])
            address_info = data.get("address_info", [])
            email_info = data.get("email_info", [])
            identity_info = data.get("identity_info", {})

            # Formatting the response with clear, structured design
            response = (
                f"📱 **Mobile:** {mobile}\n"
                "══════════════════════════════════\n"
                f"**🧑‍💼 Personal Info:**\n"
                f"  ➤ **Name:** {personal_info.get('full_name', 'Not available')}\n"
                f"  ➤ **DOB:** {personal_info.get('dob', 'Not available')}\n"
                f"  ➤ **Gender:** {personal_info.get('gender', 'Not available')}\n"
                f"  ➤ **Occupation:** {personal_info.get('occupation', 'Not available')}\n"
                f"  ➤ **Age:** {personal_info.get('age', 'Not available')}\n"
                f"  ➤ **Total Income:** {personal_info.get('total_income', 'Not available')}\n\n"
                
                f"**📞 Phone Info:**\n"
            )
            
            # Phone Info
            if phone_info:
                for phone in phone_info:
                    response += f"  ➤ **Type:** {phone.get('type_code', 'N/A')}\n"
                    response += f"  ➤ **Number:** {phone.get('number', 'N/A')}\n"
                    response += f"  ➤ **Reported:** {phone.get('reported_date', 'N/A')}\n"
                    response += "══════════════════════════\n"
            else:
                response += "  ➤ No phone data found.\n"
            
            # Address Info
            response += "\n**🏠 Address Info:**\n"
            if address_info:
                for address in address_info:
                    response += f"  ➤ **Type:** {address.get('type', 'N/A')}\n"
                    response += f"  ➤ **Address:** {address.get('address', 'N/A')}\n"
                    response += f"  ➤ **State:** {address.get('state', 'N/A')}\n"
                    response += f"  ➤ **Postal:** {address.get('postal', 'N/A')}\n"
                    response += f"  ➤ **Reported:** {address.get('reported_date', 'N/A')}\n"
                    response += "══════════════════════════\n"
            else:
                response += "  ➤ No address data found.\n"
            
            # Email Info
            response += "\n**📧 Email Info:**\n"
            if email_info:
                for email in email_info:
                    response += f"  ➤ **Email:** {email.get('email_address', 'N/A')}\n"
                    response += f"  ➤ **Reported:** {email.get('reported_date', 'N/A')}\n"
                    response += "══════════════════════════\n"
            else:
                response += "  ➤ No email data found.\n"
            
            # Identity Info
            response += "\n**🆔 Identity Info:**\n"
            if "pan_number" in identity_info:
                for pan in identity_info["pan_number"]:
                    response += f"  ➤ **PAN:** {pan.get('id_number', 'N/A')}\n"
            if "aadhaar_number" in identity_info:
                for aadhaar in identity_info["aadhaar_number"]:
                    response += f"  ➤ **Aadhaar:** {aadhaar.get('id_number', 'N/A')}\n"
            if "other_id" in identity_info:
                for other in identity_info["other_id"]:
                    response += f"  ➤ **Other ID:** {other.get('id_number', 'N/A')}\n"
            
            # Remaining Limit
            response += f"\n📝 **Remaining Limit:** {await get_sudo_limit(user_id)}\n"
            response += "══════════════════════════\n"

            # Send the response with user information
            await message.reply(response)
            
            # Log usage
            await db.usage_logs.insert_one({
                "user_id": user_id,
                "mobile": mobile,
                "timestamp": datetime.utcnow(),
                "success": True
            })

        else:
            await message.reply("❌ **No data found for the provided mobile number.**")
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        await message.reply("❌ **An error occurred while fetching the data.**")
        
        # Log error
        await db.usage_logs.insert_one({
            "user_id": user_id,
            "mobile": mobile,
            "timestamp": datetime.utcnow(),
            "success": False,
            "error": str(e)
        })

if __name__ == "__main__":
    app.run()  # Let Pyrogram's event loop handle everything
