from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
import models


def get_user_or_404(user_id: int, db: Session, *, with_relations: bool = False):
    """
    Busca o usuário por id ou levanta 404.

    `with_relations=True` faz eager-load de bills/expenses/incomes/investments
    numa única query — usado pelos endpoints que agregam dados do usuário
    (resumo, alertas, parcelas) para evitar N+1.
    """
    query = db.query(models.User)
    if with_relations:
        query = query.options(
            joinedload(models.User.bills),
            joinedload(models.User.expenses),
            joinedload(models.User.incomes),
            joinedload(models.User.investments),
        )
    user = query.filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
