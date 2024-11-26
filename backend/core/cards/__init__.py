from core.cards.sd_i2i import SDI2ICard
from core.cards.sd_inpainting import SDInpaintingCard
from core.cards.sd_outpainting import SDOutpaintingCard
from core.cards.sd_t2i import SDT2ICard
from core.cards.sdxl import SDXLCard
from core.cards.sd3 import SD3Card

builtin_cards_map = {
    SDT2ICard.name: SDT2ICard,
    SDI2ICard.name: SDI2ICard,
    SDInpaintingCard.name: SDInpaintingCard,
    SDOutpaintingCard.name: SDOutpaintingCard,
    SDXLCard.name: SDXLCard,
    SD3Card.name: SD3Card
}