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


class EncartSpecial(BaseModel):
    titre: str
    intro: str
    exemples: list[str] = Field(default_factory=list)
    message: str = ""


class AxeVoie(BaseModel):
    voie: str
    items: list[str] = Field(default_factory=list)


class Axe(BaseModel):
    nom: str
    sous_titre: str = ""
    criticite: Literal["normale", "haute", "critique"] = "normale"
    voies: list[AxeVoie] | None = None
    items: list[str] | None = None
    schema_rachis: bool = False


class DiagLine(BaseModel):
    diagnostic: str
    chirurgies: list[str]
    niveau: str = ""
    criticite: Literal["normale", "haute", "critique"] = "haute"


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
    champs: list[SectionChamps] = Field(default_factory=list)
    disrupteur: Disrupteur
    a_quoi_ca_sert: AQuoiCaSert
    badges: list[str] | None = None
    encart_special: EncartSpecial | None = None
    note_finale: str | None = None
    diagnostics_table: list[DiagLine] | None = None
    axes: list[Axe] | None = None
