from sqlmodel import create_engine, SQLModel
engine = create_engine("sqlite:///company.db")
SQLModel.metadata.create_all(engine) 
