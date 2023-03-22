from pydantic import BaseModel, Field


class Message(BaseModel):
    message: str = Field(example="Success")


class User(BaseModel):
    user: str = Field(example="nome.sobrenome")
    password: str = Field(example="Senha123")


class UserReturn(BaseModel):
    nome: str
    usuario_ad: str
    role_client: int
    access_token: str
    token_type: str = Field(default="Bearer")
    expires_in: int = Field(default=3600)


class Aceite(BaseModel):
    cpf: str = Field(max_length=11, min_length=11, example="99999999999")
    aceite: int = Field(example=1, default=1)
