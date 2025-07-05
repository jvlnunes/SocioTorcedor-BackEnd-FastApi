from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from sqlalchemy.exc import OperationalError
from pydantic import BaseModel
from typing import Optional, List

import os
import time
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title       = "API de Sócio Torcedor Ferroviário",
    version     = "0.2.0",
    description = "Backend para aplicação mobile de sócio torcedor."
)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
retry_count = 0
max_retries = 10
while engine is None and retry_count < max_retries:
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Conexão com o banco de dados estabelecida com sucesso!")
        break
    
    except OperationalError:
        retry_count += 1
        print(f"Banco de dados não está pronto, aguardando... Tentativa {retry_count}/{max_retries}")
        time.sleep(5)
        
if engine is None:
    raise RuntimeError("Não foi possível conectar ao banco de dados após várias tentativas.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, index=True)
    number      = Column(Integer, unique=True, nullable=True)
    position    = Column(String)
    nationality = Column(String)

class Competition(Base):
    __tablename__ = "competitions"
    
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, unique=True, index=True)
    country     = Column(String)
    description = Column(Text, nullable=True)

class Match(Base):
    __tablename__ = "matches"
    
    id             = Column(Integer, primary_key=True, index=True)
    status         = Column(String, default="upcoming")
    location       = Column(String)
    home_team      = Column(String)
    away_team      = Column(String)
    home_score     = Column(Integer, nullable=True)
    away_score     = Column(Integer, nullable=True)
    is_home_game   = Column(Boolean, default=False)
    match_datetime = Column(DateTime)
    highlights_url = Column(String, nullable=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"))
    
    competition = relationship("Competition", backref="matches")

Base.metadata.create_all(bind=engine)


class PlayerBase(BaseModel):
    name: str
    position: str
    number: Optional[int] = None
    nationality: str

class PlayerCreate(PlayerBase):
    pass

class PlayerResponse(PlayerBase):
    id: int
    class Config:
        from_attributes = True

class CompetitionBase(BaseModel):
    name: str
    description: Optional[str] = None
    country: str

class CompetitionCreate(CompetitionBase):
    pass

class CompetitionResponse(CompetitionBase):
    id: int
    class Config:
        from_attributes = True

class MatchBase(BaseModel):
    competition_id: int
    home_team: str
    away_team: str
    match_datetime: datetime
    location: str
    status: str = "upcoming"
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    highlights_url: Optional[str] = None
    is_home_game: Optional[bool] = False

class MatchCreate(MatchBase):
    pass

class MatchResponse(MatchBase):
    id: int
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def read_root():
    return {"message": "Bem-vindo à API de Sócio Torcedor! Módulo Esportivo Operante."}

@app.get("/status")
async def get_status():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            if result == 1:
                return {"status": "ok", "database": "connected"}
            else:
                return {"status": "error", "database": "not connected"}
    except Exception as e:
        return {"status": "error", "database": f"connection failed: {str(e)}"}

@app.post("/players/", response_model=PlayerResponse)
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    db_player = Player(**player.model_dump()) 
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@app.get("/players/", response_model=List[PlayerResponse])
def read_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    players = db.query(Player).offset(skip).limit(limit).all()
    return players

@app.get("/players/{player_id}", response_model=PlayerResponse)
def read_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.post("/competitions/", response_model=CompetitionResponse)
def create_competition(competition: CompetitionCreate, db: Session = Depends(get_db)):
    db_competition = Competition(**competition.model_dump())
    db.add(db_competition)
    db.commit()
    db.refresh(db_competition)
    return db_competition

@app.get("/competitions/", response_model=List[CompetitionResponse])
def read_competitions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    competitions = db.query(Competition).offset(skip).limit(limit).all()
    return competitions

@app.get("/competitions/{competition_id}", response_model=CompetitionResponse)
def read_competition(competition_id: int, db: Session = Depends(get_db)):
    competition = db.query(Competition).filter(Competition.id == competition_id).first()
    if competition is None:
        raise HTTPException(status_code=404, detail="Competition not found")
    return competition

@app.post("/matches/", response_model=MatchResponse)
def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    db_match = Match(**match.model_dump())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

@app.get("/matches/", response_model=List[MatchResponse])
def read_matches(skip: int = 0, limit: int = 100, 
                 is_home_game: Optional[bool] = None,
                 db: Session = Depends(get_db)):
    query = db.query(Match)
    if is_home_game is not None:
        query = query.filter(Match.is_home_game == is_home_game)
    matches = query.offset(skip).limit(limit).all()
    return matches

@app.get("/matches/{match_id}", response_model=MatchResponse)
def read_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@app.get("/games_schedule/", response_model=List[MatchResponse])
def get_games_schedule(db: Session = Depends(get_db)):
    upcoming_matches = db.query(Match).filter(
        (Match.status == "upcoming") | (Match.status == "live")
    ).order_by(Match.match_datetime).all()
    return upcoming_matches

@app.get("/home_games/", response_model=List[MatchResponse])
def get_home_games(db: Session = Depends(get_db)):
    home_games = db.query(Match).filter(
        Match.is_home_game == True,
        (Match.status == "upcoming") | (Match.status == "live")
    ).order_by(Match.match_datetime).all()
    return home_games