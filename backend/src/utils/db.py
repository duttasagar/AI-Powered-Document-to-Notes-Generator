from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from src.utils.settings import settings

Base = declarative_base()

engine = create_engine(
    settings.DB_CONNECTION,
    connect_args={
        "ssl": {
            "ssl_mode": "REQUIRED"
        }
    }
)

LocalSession = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)














# from sqlalchemy import create_engine, inspect, text
# from sqlalchemy.orm import sessionmaker, declarative_base
# from src.utils.settings import settings
# Base = declarative_base()

# engine = create_engine(url = settings.DB_CONNECTION)

# LocalSession = sessionmaker(bind=engine)


# def ensure_document_notes_column():
#     existing_columns = {column["name"] for column in inspect(engine).get_columns("documents")}
#     missing_columns = {
#         "generated_notes": "TEXT",
#         "error_message": "TEXT",
#     }

#     with engine.begin() as connection:
#         for column_name, column_type in missing_columns.items():
#             if column_name not in existing_columns:
#                 connection.execute(text(f"ALTER TABLE documents ADD COLUMN {column_name} {column_type}"))


# def get_db():
#     session = LocalSession()
#     try:
#         yield session
#     finally:
#         session.close()