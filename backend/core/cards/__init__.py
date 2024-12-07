from core.cards.sd_i2i import SDI2ICard
from core.cards.sd_inpainting import SDInpaintingCard
from core.cards.sd_outpainting import SDOutpaintingCard
from core.cards.sd_t2i import SDT2ICard
from core.cards.sdxl import SDXLCard
from core.cards.sd3 import SD3Card

builtin_cards_map = {
    SDT2ICard.meta_data.get("name"): SDT2ICard,
    SDI2ICard.meta_data.get("name"): SDI2ICard,
    SDInpaintingCard.meta_data.get("name"): SDInpaintingCard,
    SDOutpaintingCard.meta_data.get("name"): SDOutpaintingCard,
    SDXLCard.meta_data.get("name"): SDXLCard,
    SD3Card.meta_data.get("name"): SD3Card
}

