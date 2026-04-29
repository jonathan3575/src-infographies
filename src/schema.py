from pydantic import BaseModel, Field
from typing import Literal


class QuiRemplit(BaseModel):
    role: Literal["patient", "chirurgien"]
    support: str
    pourcentage: int = Field(ge=0, le=100)


class SectionChamps(BaseModel):
    section: str
    qui: Literal["patient", "chirurgien"]
    criticite: Literal["normale", "haute", "critique"] = "normale"
    items: list[str]


class Disrupteur(BaseModel):
    chiffre: str
    unite: str
    phrase_principale: str
    phrase_secondaire: str


class AQuoiCaSert(BaseModel):
    titre: str
    points: list[str]


class Questionnaire(BaseModel):
    id: str
    titre: str
    sous_titre: str
    numero_planche: str
    total_planches: int
    rachis: Literal["lombaire", "cervical", "scoliose", "commun"]
    etape_parcours: str
    qui_remplit: list[QuiRemplit]
    duree_estimee_chir: str
    screenshot_follow: list[str]
    champs: list[SectionChamps]
    disrupteur: Disrupteur
    a_quoi_ca_sert: AQuoiCaSert
