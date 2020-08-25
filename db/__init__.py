def init_db():
    from models.user import User, db
    from models.definition import Definition
    return db
