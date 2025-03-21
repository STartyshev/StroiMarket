import datetime

from pydantic import BaseModel, ConfigDict


class UserRole:
    role: str


class FeedbackTextWebsocket(BaseModel, UserRole):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    liked_text: str
    disliked_text: str


class AdminCommentWebsocket(BaseModel, UserRole):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    operation_type: str
    feedback_id: int
    admin_comment: str


class DeleteFeedbackWebsocket(BaseModel, UserRole):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    operation_type: str
    feedback_id: int


class Feedback(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int
    date_of_registration: datetime.datetime
    date_of_update: datetime.datetime
    liked_text: str
    disliked_text: str


class FeedbackOperationToSend(BaseModel):
    status_code: int
    operation_type: str


class FeedbackCreateToSend(FeedbackOperationToSend):
    feedback_html: str


class FeedbackUpdateToSend(FeedbackOperationToSend):
    feedback_id: int
    admin_comment: str


class FeedbackDeleteToSend(FeedbackOperationToSend):
    feedback_id: int


class WebsocketError(BaseModel):
    status_code: int
    error_message: str


class InvalidWebsocketData(WebsocketError):
    pass


class NotAuthorizedUser(WebsocketError):
    pass
