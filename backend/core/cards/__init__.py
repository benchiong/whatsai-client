from core.cards.flux_dev import FluxDevCard
from core.cards.flux_inpaint import FluxInpaintCard
from core.cards.flux_outpaint import FluxOutpaintCard
from core.cards.flux_schnell import FluxSchnellCard
from core.cards.ltx_i2v import LightricksI2VCard
from core.cards.ltx_t2v import LightricksT2VCard
from core.cards.mochi_t2v import MochiT2VCard
from core.cards.sd_t2i import SDT2ICard
from core.cards.sd_i2i import SDI2ICard
from core.cards.sd_inpaint import SDInpaintCard
from core.cards.sd_outpaint import SDOutpaintCard
from core.cards.sdxl import SDXLCard
from core.cards.sd3 import SD3Card

BUILTIN_CARDS_MAP = {
    SDT2ICard.name: SDT2ICard,
    SDI2ICard.name: SDI2ICard,
    SDInpaintCard.name: SDInpaintCard,
    SDOutpaintCard.name: SDOutpaintCard,
    SDXLCard.name: SDXLCard,
    SD3Card.name: SD3Card,
    FluxDevCard.name: FluxDevCard,
    FluxSchnellCard.name: FluxSchnellCard,
    FluxInpaintCard.name: FluxInpaintCard,
    FluxOutpaintCard.name: FluxOutpaintCard,
    LightricksT2VCard.name: LightricksT2VCard,
    LightricksI2VCard.name: LightricksI2VCard,
    MochiT2VCard.name: MochiT2VCard,
}
