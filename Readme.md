Here's the full code for the `README.md` file:

```markdown
# Mobile UAN Bot

A Telegram bot that allows users to fetch UAN (Universal Account Number) details by providing a 10-digit mobile number. The bot is designed for administrative use, with limited access granted to specific sudo users. The bot uses MongoDB for data storage and integrates with an external API to fetch UAN-related information.

## Features

- **Fetch UAN Data**: Use the `/info <10-digit mobile number>` command to fetch UAN details associated with a mobile number.
- **Sudo Users**: Admins can manage sudo users with the `/addsudo` and `/removesudo` commands. Sudo users have a usage limit for querying UAN information.
- **Mobile Number Validation**: The bot checks if the provided mobile number is valid (10 digits).
- **Logging**: All API requests and errors are logged to MongoDB for later analysis.

## Requirements

- Python 3.8 or higher
- MongoDB
- Pyrogram library for Telegram bot integration
- aiohttp for asynchronous HTTP requests

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/mobile-uan-bot.git
cd mobile-uan-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration

Create a `secret.py` file in the project root directory with the following structure:

```python
config = {
    "API_ID": "your_api_id",          # Telegram API ID
    "API_HASH": "your_api_hash",      # Telegram API Hash
    "BOT_TOKEN": "your_bot_token",    # Your bot's token
    "MONGODB_URI": "mongodb://localhost:27017",  # MongoDB URI
    "API_URL": "https://example.com/uan",  # The external UAN API URL
    "SECRET_KEY": "your_secret_key",  # Secret key for the API
    "CLIENT_ID": "your_client_id",    # Client ID for the API
    "OWNER_ID": 123456789,            # Your Telegram user ID
}
```

### 4. Run the bot

After configuring the bot, you can start it with the following command:

```bash
python bot.py
```

The bot will now be running and will listen for commands on Telegram.

## Commands

### `/start`
This command will send a welcome message and explain how to use the bot.

### `/info <10-digit mobile number>`
This command fetches the UAN details for a given mobile number. Only sudo users can use this command. It displays personal info, phone info, address info, email info, and identity info (such as PAN and Aadhaar numbers).

### `/addsudo <user_id> <limit>`
The owner of the bot can use this command to add a user as a sudo user with a specified usage limit for querying UAN information.

### `/removesudo <user_id>`
The owner can use this command to remove a user from the sudo list.

### `/sudolist`
The owner can list all current sudo users with their usage limits.

## Logging

All bot activities such as requests and errors are logged into MongoDB for monitoring and debugging purposes.

## Contributing

Feel free to fork the repository and submit pull requests for any improvements or bug fixes. Ensure that your changes don't break the bot's functionality.

## License

This project is licensed under the MIT License.

---

For any questions or feedback, contact the bot owner directly.
```

### Key Sections:
1. **Project Description**: Explains the purpose of the bot.
2. **Features**: Lists the features and functionalities available in the bot.
3. **Requirements**: Describes the necessary tools and dependencies to run the bot.
4. **Setup**: Provides step-by-step instructions on how to set up the bot.
5. **Commands**: Details the commands available for the bot's users and admin.
6. **Logging**: Mentions that the bot logs all interactions.
7. **Contributing**: Encourages open-source contributions.
8. **License**: Mentions the license for the project.

You can copy this code directly into a file named `README.md` in your project directory.
