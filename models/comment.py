from models.base import ApiModel


class Comment(ApiModel):
    id: int
    post_id: int
    name: str
    email: str
    body: str
