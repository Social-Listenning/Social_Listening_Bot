from helper.httpMethod import PostMethod
from core.config import settings

async def save_social_message(message, sentiment):
  if message.get("type_message") == "Comment":
    comment_info = {
      "networkId": message.get("recipient_id"),
      "message": message.get("text"),
      "sender": message.get("sender_id"),
      "createdAt": message.get("metadata").get("comment_created_time"),
      "type": message.get("type_message"),
      "parent": {
          "postId": message.get("metadata").get("post_id"),
          "message": message.get("metadata").get("post_message"),
          "permalinkUrl": message.get("metadata").get("permalink_url"),
          "createdAt": message.get("metadata").get("post_created_time")
      },
      "sentiment": sentiment,
      "postId": message.get("metadata").get("post_id"),
      "commentId": message.get("metadata").get("comment_id"),
      "parentId": message.get("metadata").get("parent_id")
    }
    backend_auth_header = {
      'Authorization': settings.BACKEND_AUTH_HEADER
    }
    response_save_comment = await PostMethod(
      domain = settings.BACKEND_ENPOINT, 
      endpoint = "/social-message/save", 
      body = comment_info, 
      headers = backend_auth_header
    )
    print("Response save comment: ", response_save_comment)
