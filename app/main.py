import os
import time
import json 

from dotenv         import load_dotenv
from typing         import Optional, List
from fastapi        import FastAPI, Depends, HTTPException, status 
from pydantic       import BaseModel, ConfigDict 
from datetime       import datetime
from sqlalchemy     import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from sqlalchemy.exc import OperationalError

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
    ticket_categories = relationship("TicketCategory", back_populates="match") 

class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    username     = Column(String, index=True)
    email        = Column(String, unique=True, index=True)
    password     = Column(String) 
    tubarao_id   = Column(String, unique=True, nullable=True)
    full_name    = Column(String, nullable=True)
    cpf          = Column(String, nullable=True)
    birth_date   = Column(String, nullable=True)
    gender       = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

class Card(Base):
    __tablename__ = "cards"
    id               = Column(String, primary_key=True, index=True) 
    user_id          = Column(Integer, ForeignKey("users.id"))
    brand            = Column(String)
    last_four_digits = Column(String)
    holder_name      = Column(String)
    expiry_date      = Column(String) 
    is_default       = Column(Boolean, default=False)

    user = relationship("User", backref="cards")

class News(Base):
    __tablename__ = "news"
    id            = Column(String, primary_key=True, index=True)
    category      = Column(String)
    title         = Column(String)
    published_at  = Column(DateTime)
    author        = Column(String)
    view_count    = Column(Integer, default=0)
    image_url     = Column(String, nullable=True)
    content       = Column(Text)
    like_count    = Column(Integer, default=0)

class PressConference(Base):
    __tablename__ = "press_conferences"
    id            = Column(String, primary_key=True, index=True)
    title         = Column(String)
    video_thumbnail_url = Column(String, nullable=True)
    video_url     = Column(String, nullable=True) 
    published_at  = Column(DateTime, default=datetime.utcnow)

class Video(Base):
    __tablename__ = "videos"
    id            = Column(String, primary_key=True, index=True)
    title         = Column(String)
    video_thumbnail_url = Column(String, nullable=True)
    video_url     = Column(String, nullable=True)
    published_at  = Column(DateTime, default=datetime.utcnow)

class UserNewsLike(Base):
    __tablename__ = "user_news_likes"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    news_id = Column(String, ForeignKey("news.id"), primary_key=True)

class TicketCategory(Base):
    __tablename__ = "ticket_categories"
    id                 = Column(String, primary_key=True, index=True) 
    match_id           = Column(Integer, ForeignKey("matches.id"))
    name               = Column(String)
    available_quantity = Column(Integer)
    price              = Column(Integer) 

    match = relationship("Match", back_populates="ticket_categories")

class Order(Base):
    __tablename__ = "orders"
    id             = Column(String, primary_key=True, index=True) 
    user_id        = Column(Integer, ForeignKey("users.id"))
    match_id       = Column(Integer, ForeignKey("matches.id"))
    category_id    = Column(String, ForeignKey("ticket_categories.id"))
    quantity       = Column(Integer)
    payment_method = Column(String)
    card_id        = Column(String, nullable=True) 
    status         = Column(String, default="PENDING") 
    qr_code_url    = Column(String, nullable=True)
    ordered_at     = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="orders")
    match = relationship("Match")
    category = relationship("TicketCategory")

class Checkin(Base):
    __tablename__ = "checkins"
    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"))
    match_id       = Column(Integer, ForeignKey("matches.id"))
    checkin_time   = Column(DateTime, default=datetime.utcnow)
    qr_code_url    = Column(String, nullable=True)

    user = relationship("User", backref="checkins")
    match = relationship("Match")

class Partner(Base):
    __tablename__ = "partners"
    id              = Column(String, primary_key=True, index=True) 
    name            = Column(String)
    category        = Column(String)
    logo_url        = Column(String, nullable=True)
    discount        = Column(String) 
    is_featured     = Column(Boolean, default=False)
    about_establishment = Column(Text, nullable=True)
    how_to_use      = Column(Text, nullable=True) 
    description     = Column(Text, nullable=True)


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
    model_config = ConfigDict(from_attributes=True)

class CompetitionBase(BaseModel):
    name: str
    description: Optional[str] = None
    country: str

class CompetitionCreate(CompetitionBase):
    pass

class CompetitionResponse(CompetitionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: str
    password: str

class UserLoginResponse(BaseModel):
    id: str 
    name: str
    email: str

class LoginSuccessResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserLoginResponse

class MemberProfileResponse(BaseModel):
    tubarao_id: str
    full_name: str
    email: str
    cpf: str
    birth_date: str
    gender: str
    phone_number: str
    model_config = ConfigDict(from_attributes=True) 

class CardBase(BaseModel):
    brand: str
    last_four_digits: str
    holder_name: str
    expiry_date: str
    is_default: bool

class CardResponse(CardBase):
    id: str 
    model_config = ConfigDict(from_attributes=True)

class CardListResponse(BaseModel):
    cards: List[CardResponse]

class CardAddRequest(BaseModel):
    card_token: str

class TeamInfo(BaseModel):
    name: str
    logo_url: str

class NextMatch(BaseModel):
    home_team: TeamInfo
    away_team: TeamInfo
    match_day: str
    match_time: str
    championship: str

class NewsSummary(BaseModel):
    id: str
    title: str
    image_url: str

class PressConferenceSummary(BaseModel):
    id: str
    title: str
    video_thumbnail_url: str

class VideoSummary(BaseModel):
    id: str
    title: str
    video_thumbnail_url: str

class DashboardResponse(BaseModel):
    next_match: Optional[NextMatch] = None
    news: List[NewsSummary]
    press_conferences: List[PressConferenceSummary]
    videos: List[VideoSummary]

class NewsDetailResponse(BaseModel):
    id: str
    category: str
    title: str
    published_at: datetime
    author: str
    view_count: int
    image_url: Optional[str] = None
    content: str
    like_count: int
    user_has_liked: bool

class LikeNewsResponse(BaseModel):
    like_count: int
    user_has_liked: bool


class TicketCategoryResponse(BaseModel):
    id: str
    name: str
    available_quantity: int
    price: float 

class MatchListResponseItem(BaseModel):
    id: str 
    championship: str
    date: str
    time: str
    stadium: str
    status: str
    ticket_categories: List[TicketCategoryResponse]

class MatchListResponse(BaseModel):
    matches: List[MatchListResponseItem]

class PaymentDetails(BaseModel):
    method: str
    card_id: Optional[str] = None

class TicketPurchaseRequest(BaseModel):
    match_id: int
    category_id: str
    quantity: int
    payment: PaymentDetails

class TicketPurchaseResponse(BaseModel):
    order_id: str
    status: str
    qr_code_url: Optional[str] = None

class CheckinResponse(BaseModel):
    message: str
    qr_code_url: Optional[str] = None


class PartnerSummary(BaseModel):
    id: str
    name: str
    category: str
    logo_url: str
    discount: str

class BenefitsListResponse(BaseModel):
    featured_partners: List[PartnerSummary]
    all_partners: List[PartnerSummary]

class BenefitDetailResponse(BaseModel):
    id: str
    name: str
    category: str
    discount: str
    logo_url: str
    about_establishment: str
    how_to_use: List[str]
    description: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_mock(db: Session = Depends(get_db)):
     
    user_id = 1 
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

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

@app.post("/api/v1/players/", response_model=PlayerResponse)
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    db_player = Player(**player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@app.get("/api/v1/players/", response_model=List[PlayerResponse])
def read_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    players = db.query(Player).offset(skip).limit(limit).all()
    return players

@app.get("/api/v1/players/{player_id}", response_model=PlayerResponse)
def read_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.post("/api/v1/competitions/", response_model=CompetitionResponse)
def create_competition(competition: CompetitionCreate, db: Session = Depends(get_db)):
    db_competition = Competition(**competition.model_dump())
    db.add(db_competition)
    db.commit()
    db.refresh(db_competition)
    return db_competition

@app.get("/api/v1/competitions/", response_model=List[CompetitionResponse])
def read_competitions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    competitions = db.query(Competition).offset(skip).limit(limit).all()
    return competitions

@app.get("/api/v1/competitions/{competition_id}", response_model=CompetitionResponse)
def read_competition(competition_id: int, db: Session = Depends(get_db)):
    competition = db.query(Competition).filter(Competition.id == competition_id).first()
    if competition is None:
        raise HTTPException(status_code=404, detail="Competition not found")
    return competition

@app.post("/api/v1/matches/", response_model=MatchResponse)
def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    db_match = Match(**match.model_dump())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

@app.get("/api/v1/matches/{match_id}", response_model=MatchResponse)
def read_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@app.get("/api/v1/games_schedule/", response_model=List[MatchResponse])
def get_games_schedule(db: Session = Depends(get_db)):
    upcoming_matches = db.query(Match).filter(
        (Match.status == "upcoming") | (Match.status == "live")
    ).order_by(Match.match_datetime).all()
    return upcoming_matches

@app.get("/api/v1/home_games/", response_model=List[MatchResponse])
def get_home_games(db: Session = Depends(get_db)):
    home_games = db.query(Match).filter(
        Match.is_home_game == True,
        (Match.status == "upcoming") | (Match.status == "live")
    ).order_by(Match.match_datetime).all()
    return home_games

@app.post("/api/v1/auth/login", response_model=LoginSuccessResponse)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)): 
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user or user.password != user_credentials.password: 
        raise HTTPException(status_code=400, detail="Invalid credentials") 

    
    access_token = "eyJhbGci0iJIUzI1NiIsInR5cCI6IkpXVCJ9..." 

    return LoginSuccessResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserLoginResponse(id=str(user.id), name=user.username, email=user.email) 
    )

@app.get("/api/v1/member/profile", response_model=MemberProfileResponse)
def get_member_profile(current_user: User = Depends(get_current_user_mock)): 
    
    return MemberProfileResponse(
        tubarao_id=current_user.tubarao_id, 
        full_name=current_user.full_name, 
        email=current_user.email, 
        cpf=current_user.cpf, 
        birth_date=current_user.birth_date, 
        gender=current_user.gender, 
        phone_number=current_user.phone_number 
    )

@app.get("/api/v1/member/cards", response_model=CardListResponse)
def list_saved_cards(current_user: User = Depends(get_current_user_mock), db: Session = Depends(get_db)): 
    cards = db.query(Card).filter(Card.user_id == current_user.id).all() 
    return {"cards": cards} 

@app.post("/api/v1/member/cards", status_code=status.HTTP_201_CREATED, response_model=CardResponse)
def add_new_card(card_data: CardAddRequest, current_user: User = Depends(get_current_user_mock), db: Session = Depends(get_db)): 
     
    new_card_id = f"card_{datetime.now().strftime('%Y%m%d%H%M%S')}_{current_user.id}"
    mock_card_details = {
        "id": new_card_id,
        "brand": "Visa",
        "last_four_digits": "1234",
        "holder_name": "Michel R Fernandez", 
        "expiry_date": "12/2028",
        "is_default": False
    }

    db_card = Card(user_id=current_user.id, **mock_card_details) 
    db.add(db_card) 
    db.commit() 
    db.refresh(db_card) 
    return db_card 

@app.delete("/api/v1/member/cards/{cardId}", status_code=status.HTTP_204_NO_CONTENT)
def remove_card(cardId: str, current_user: User = Depends(get_current_user_mock), db: Session = Depends(get_db)): 
    card = db.query(Card).filter(Card.id == cardId, Card.user_id == current_user.id).first() 
    if not card:
        raise HTTPException(status_code=404, detail="Card not found or not owned by user") 
    db.delete(card) 
    db.commit() 
    return 


@app.get("/api/v1/dashboard", response_model=DashboardResponse)
def get_dashboard_data(db: Session = Depends(get_db)): 
    
    next_match_db = db.query(Match).filter(
        (Match.status == "upcoming") | (Match.status == "live")
    ).order_by(Match.match_datetime).first() 

    next_match_data = None
    if next_match_db:
        
        championship_name = next_match_db.competition.name if next_match_db.competition else "Campeonato Indefinido"
        next_match_data = NextMatch(
            home_team=TeamInfo(name=next_match_db.home_team, logo_url="url/home_team_logo.png"), 
            away_team=TeamInfo(name=next_match_db.away_team, logo_url="url/away_team_logo.png"), 
            match_day=next_match_db.match_datetime.strftime("%A, %d/%m"), 
            match_time=next_match_db.match_datetime.strftime("%Hh%M"), 
            championship=championship_name 
        )

    recent_news_db = db.query(News).order_by(News.published_at.desc()).limit(5).all() 
    news_summaries = [NewsSummary(id=n.id, title=n.title, image_url=n.image_url) for n in recent_news_db] 
    
    press_conferences_db = db.query(PressConference).order_by(PressConference.published_at.desc()).limit(3).all() 
    press_conferences_summaries = [PressConferenceSummary(id=pc.id, title=pc.title, video_thumbnail_url=pc.video_thumbnail_url) for pc in press_conferences_db] 
    
    videos_db = db.query(Video).order_by(Video.published_at.desc()).limit(3).all() 
    video_summaries = [VideoSummary(id=v.id, title=v.title, video_thumbnail_url=v.video_thumbnail_url) for v in videos_db] 

    return DashboardResponse(
        next_match=next_match_data, 
        news=news_summaries, 
        press_conferences=press_conferences_summaries, 
        videos=video_summaries 
    )

@app.get("/api/v1/news/{newsId}", response_model=NewsDetailResponse)
def get_news_details(newsId: str, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user_mock)): 
    news = db.query(News).filter(News.id == newsId).first() 
    if not news:
        raise HTTPException(status_code=404, detail="News not found") 
    
    news.view_count += 1 
    db.add(news) 
    db.commit() 
    db.refresh(news) 

    user_has_liked = False 
    if current_user:
        user_like = db.query(UserNewsLike).filter(
            UserNewsLike.user_id == current_user.id,
            UserNewsLike.news_id == newsId
        ).first() 
        if user_like:
            user_has_liked = True 

    return NewsDetailResponse(
        id=news.id, 
        category=news.category, 
        title=news.title, 
        published_at=news.published_at, 
        author=news.author, 
        view_count=news.view_count, 
        image_url=news.image_url, 
        content=news.content, 
        like_count=news.like_count, 
        user_has_liked=user_has_liked 
    )

@app.post("/api/v1/news/{newsId}/like", response_model=LikeNewsResponse)
def like_news(newsId: str, current_user: User = Depends(get_current_user_mock), db: Session = Depends(get_db)): 
    news = db.query(News).filter(News.id == newsId).first() 
    if not news:
        raise HTTPException(status_code=404, detail="News not found") 

    user_like = db.query(UserNewsLike).filter(
        UserNewsLike.user_id == current_user.id,
        UserNewsLike.news_id == newsId
    ).first() 

    if user_like:
        
        db.delete(user_like) 
        news.like_count -= 1 
        user_has_liked = False 
    else:
        
        new_like = UserNewsLike(user_id=current_user.id, news_id=newsId) 
        db.add(new_like) 
        news.like_count += 1 
        user_has_liked = True 

    db.add(news) 
    db.commit() 
    db.refresh(news) 

    return LikeNewsResponse(like_count=news.like_count, user_has_liked=user_has_liked) 


@app.get("/api/v1/matches", response_model=MatchListResponse)
def list_upcoming_games(db: Session = Depends(get_db)): 
    
    matches_db = db.query(Match).filter(
        (Match.status == "SALE_OPEN") | (Match.status == "CHECKIN_OPEN")
    ).order_by(Match.match_datetime).all() 

    matches_response = []
    for match in matches_db:
        ticket_categories = [
            TicketCategoryResponse(
                id=tc.id,
                name=tc.name,
                available_quantity=tc.available_quantity,
                price=tc.price / 100.0 
            ) for tc in match.ticket_categories
        ] 
        matches_response.append(MatchListResponseItem(
            id=str(match.id), 
            championship=match.competition.name if match.competition else "N/A", 
            date=match.match_datetime.strftime("%Y-%m-%d"), 
            time=match.match_datetime.strftime("%H:%M"), 
            stadium=match.location, 
            status=match.status, 
            ticket_categories=ticket_categories 
        ))
    return {"matches": matches_response} 

@app.post("/api/v1/tickets/orders", status_code=status.HTTP_201_CREATED, response_model=TicketPurchaseResponse)
def finalize_ticket_purchase(order_details: TicketPurchaseRequest, current_user: User = Depends(get_current_user_mock), db: Session = Depends(get_db)): 
    match = db.query(Match).filter(Match.id == order_details.match_id).first() 
    if not match:
        raise HTTPException(status_code=404, detail="Match not found") 

    category = db.query(TicketCategory).filter(
        TicketCategory.id == order_details.category_id,
        TicketCategory.match_id == match.id
    ).first() 
    if not category:
        raise HTTPException(status_code=404, detail="Ticket category not found for this match") 

    if category.available_quantity < order_details.quantity:
        raise HTTPException(status_code=400, detail="Not enough tickets available") 

    payment_successful = True 

    new_order_id = f"order_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{current_user.id}" 
    qr_code_url = f"url/para/qrcode_ingresso_{new_order_id}.png" 

    order_status = "CONFIRMED" if payment_successful else "FAILED" 

    db_order = Order(
        id=new_order_id, 
        user_id=current_user.id, 
        match_id=order_details.match_id, 
        category_id=order_details.category_id, 
        quantity=order_details.quantity, 
        payment_method=order_details.payment.method, 
        card_id=order_details.payment.card_id, 
        status=order_status, 
        qr_code_url=qr_code_url 
    )

    if payment_successful:
        category.available_quantity -= order_details.quantity
        db.add(category)

    db.add(db_order) 
    db.commit() 
    db.refresh(db_order) 

    return TicketPurchaseResponse(
        order_id=db_order.id, 
        status=db_order.status, 
        qr_code_url=db_order.qr_code_url 
    )

@app.post("/api/v1/matches/{matchId}/checkin", response_model=CheckinResponse)
def perform_checkin(matchId: int, current_user: User = Depends(get_current_user_mock), db: Session = Depends(get_db)): 
    match = db.query(Match).filter(Match.id == matchId).first() 
    if not match:
        raise HTTPException(status_code=404, detail="Match not found") 

    if match.status != "CHECKIN_OPEN": 
        raise HTTPException(status_code=400, detail="Check-in is not open for this match")

    existing_checkin = db.query(Checkin).filter(
        Checkin.user_id == current_user.id,
        Checkin.match_id == matchId
    ).first()
    if existing_checkin:
        raise HTTPException(status_code=400, detail="User already checked in for this match")

    new_checkin_qr_url = f"url/para/qrcode_checkin_{current_user.id}_{matchId}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png" 

    db_checkin = Checkin(
        user_id=current_user.id, 
        match_id=matchId, 
        qr_code_url=new_checkin_qr_url 
    )
    db.add(db_checkin) 
    db.commit() 
    db.refresh(db_checkin) 

    return CheckinResponse(
        message="Check-in realizado com sucesso!", 
        qr_code_url=new_checkin_qr_url 
    )


@app.get("/api/v1/benefits", response_model=BenefitsListResponse)
def list_benefits(db: Session = Depends(get_db)): 
    featured = db.query(Partner).filter(Partner.is_featured == True).all() 
    all_partners = db.query(Partner).all() 

    featured_summaries = [
        PartnerSummary(
            id=p.id, name=p.name, category=p.category, logo_url=p.logo_url, discount=p.discount
        ) for p in featured
    ] 
    all_partners_summaries = [
        PartnerSummary(
            id=p.id, name=p.name, category=p.category, logo_url=p.logo_url, discount=p.discount
        ) for p in all_partners
    ] 

    return BenefitsListResponse(
        featured_partners=featured_summaries, 
        all_partners=all_partners_summaries 
    )

@app.get("/api/v1/benefits/{benefitId}", response_model=BenefitDetailResponse)
def get_benefit_details(benefitId: str, db: Session = Depends(get_db)): 
    partner = db.query(Partner).filter(Partner.id == benefitId).first() 
    if not partner:
        raise HTTPException(status_code=404, detail="Benefit not found") 

    how_to_use_list = json.loads(partner.how_to_use) if partner.how_to_use else [] 
    if not isinstance(how_to_use_list, list):
        how_to_use_list = [how_to_use_list] 

    return BenefitDetailResponse(
        id=partner.id, 
        name=partner.name, 
        category=partner.category, 
        discount=partner.discount, 
        logo_url=partner.logo_url, 
        about_establishment=partner.about_establishment, 
        how_to_use=how_to_use_list, 
        description=partner.description 
    )