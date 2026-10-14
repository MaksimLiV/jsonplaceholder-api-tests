from models.base import ApiModel


class Post(ApiModel):
    id: int
    user_id: int
    title: str
    body: str
