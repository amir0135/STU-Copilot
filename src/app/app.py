import os
from typing import Dict, Optional
import chainlit as cl
import logging

# Basic logging configuration
logging.basicConfig(level=logging.INFO)

# OAuth configuration - Set as environment variables in .chainlit/config.toml
# [app]
# oauth_providers = [
#     {
#         id = "azure-ad",
#         client_id = "${AZURE_CLIENT_ID}",
#         client_secret = "${AZURE_CLIENT_SECRET}",
#         authorization_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
#         token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token",
#         userinfo_url = "https://graph.microsoft.com/v1.0/me",
#         scope = "openid profile email User.Read"
#     }
# ]

# OAuth callback for Azure AD authentication (commented out until proper signature is found)
# @cl.oauth_callback
# async def oauth_callback(
#     provider_id: str,
#     token: str,
#     raw_user_data: Dict[str, str],
#     default_user: cl.User,
# ) -> Optional[cl.User]:
#     print(f"OAuth callback for provider {provider_id}")
#     print(f"User data: {raw_user_data}")
#     
#     # Set user information from Azure AD
#     default_user.identifier = raw_user_data.get("mail", raw_user_data.get("userPrincipalName", ""))
#     default_user.display_name = raw_user_data.get("displayName", "")
#     default_user.metadata["user_id"] = raw_user_data.get("id", "")
#     default_user.metadata["first_name"] = raw_user_data.get("givenName", "")
#     default_user.metadata["job_title"] = raw_user_data.get("jobTitle", "")
#     default_user.metadata["office_location"] = raw_user_data.get("officeLocation", "")
# 
#     # Store user info in session
#     cl.user_session.set("user_id", raw_user_data.get("id"))
#     
#     return default_user

@cl.on_chat_start
async def start():
    print("Chat session started")
    
    user = cl.user_session.get("user")
    if user and isinstance(user, cl.User):
        user_id = user.metadata.get("user_id", "anonymous")
    else:
        user_id = "anonymous"

    welcome_message = f"""# Welcome to the STU Copilot! 🚀

Hello {user_id}!

I'm here to help you with various tasks including:
- 🔍 **Search**: Web search, GitHub repositories, documentation
- 📊 **Research**: Industry insights, company analysis, technical documentation  
- 💰 **Pricing**: Azure cost analysis and optimization
- 🏗️ **Architecture**: Cloud architecture guidance and best practices
- 📝 **Documentation**: Microsoft documentation and blog posts

Feel free to ask me anything!"""
    
    await cl.Message(content=welcome_message).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming chat messages."""
    user = cl.user_session.get("user")
    user_id = "anonymous"
    if user and isinstance(user, cl.User):
        user_id = user.metadata.get("user_id", "anonymous")
    
    # Simple echo for now
    response = f"Hello {user_id}! You said: {message.content}"
    
    await cl.Message(content=response).send()

if __name__ == "__main__":
    # For testing locally
    import asyncio
    asyncio.run(cl.run())
