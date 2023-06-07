import re
import telebot

# Replace 'YOUR_BOT_TOKEN' with your actual bot token obtained from BotFather
bot = telebot.TeleBot('bot_token')

# Define the file path for banned words
banned_words_file = 'words.txt'

# Define the forbidden pattern
forbidden_pattern = re.compile(r'choose banned pattherns or combinations of regex')

# Define the number of violations before a user gets banned
violations_threshold = 3

# Dictionary to store user violations count
user_violations = {}

# List of user IDs with immunity
immune_users = [111, 999]  # Replace with actual user IDs

# Variable to store banned words
forbidden_words = []

# Function to load banned words from file
def load_banned_words():
    with open(banned_words_file, 'r') as file:
        return [word.strip() for word in file.readlines()]

# Function to add a new banned word
def add_banned_word(word):
    with open(banned_words_file, 'a') as file:
        file.write(word + '\n')

# Load the initial banned words at startup
forbidden_words = load_banned_words()

# Command to add banned words
@bot.message_handler(commands=['addword'])
def add_word(message):
    if message.from_user.id in immune_users:  # Replace with the ID of the bot owner
        words = message.text.split()[1:]  # Extract the words from the command message
        for word in words:
            if word not in forbidden_words:
                forbidden_words.append(word)
                add_banned_word(word)
        bot.reply_to(message, f"Banned words added: {', '.join(words)}")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

@bot.message_handler(func=lambda message: True)
def check_forbidden_words(message):
    # Check if the user has immunity
    if message.from_user.id in immune_users:
        return

    # Convert the message text to lowercase for case-insensitive matching
    text = message.text.lower()

    # Check if any forbidden word is present in the message
    for word in forbidden_words:
        if word in text:
            handle_violation(message)
            return

    # Check if the forbidden pattern is matched
    if forbidden_pattern.match(text):
        handle_violation(message)

def handle_violation(message):
    user_id = message.from_user.id

    # Check if the user already has violations
    if user_id in user_violations:
        user_violations[user_id] += 1
    else:
        user_violations[user_id] = 1

    # Remove the message
    bot.delete_message(message.chat.id, message.message_id)

    # Warn the user
    bot.send_message(message.chat.id, "⚠️ Warning! The content is not allowed.")

    # Check if the user has reached the violations threshold
    if user_violations[user_id] >= violations_threshold:
        # Ban the user
        bot.kick_chat_member(message.chat.id, user_id)
        bot.send_message(message.chat.id, f"🚫 User @{message.from_user.username} has been banned for repeated violations.")

# Start the bot
bot.polling()
