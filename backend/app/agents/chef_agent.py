"""AI Chef Agent for recipe generation."""

import json
from typing import List

import httpx
from pydantic import BaseModel, Field

from app.config import settings


class RecipeGenerationRequest(BaseModel):
    ingredients: List[strt] = Field(min_length=1, max_length=30)
    chef_id: str = Field(min_length=1, max_length=64)
    chef_name: str = Field(min_length=1, max_length=100)

    def normalized_ingredients(self) -> list[str]:
        values = [item.strip() for item in self.ingredients if item.strip()]
        if not values:
            raise ValueError("At least one ingredient is required")
        return list(dict.fromkeys(values))[:30]


class RecipeResponse(BaseModel):
    recipe_name: str = Field(min_length=1, max_length=200)
    recipe_description: str = Field(min_length=1, max_length=12000)
    ingredients: List[str] = Field(min_length=1, max_length=50)
    instructions: List[str] = Field(min_length=1, max_length=30)
    tips: str = Field(default="", max_length=3000)
    cooking_time: str = Field(default="", max_length=100)


class FollowUpResponse(BaseModel):
    response: str = Field(min_length=1, max_length=4000)


CHEF_PROMPTS = {
    "gogo-precious": "You are Gogo Precious, a warm South African grandmother. Use occasional South African expressions and keep the tone caring.",
    "mandla": "You are Chef Mandla from Johannesburg, confident, modern and practical. Use light kasi expressions without stereotyping.",
    "tandie": "You are Tandie the Baker from Cape Town, creative, playful and encouraging.",
    "baba-thabo": "You are Baba Thabo"Âv—6RG&F—F–öæÂ6÷WF‚g&–6â6öö²â&RF–VçBÂ&7F–6ÂæB&W7V7FgVÂâ"À¢&6†Vb×¦Ö#¢%–÷R&R6†Vb¦ÖÂVæW&vWF–2ÂgVæç’æBVæ6÷W&v–ærâ¶VWF†RGf–6R&7F–6ÂæB6†–Wf&ÆRâ"À§Ğ  ¦FVbö6†Ve÷&ö×B†6†Veö–C¢7G"’Óâ7G# ¢&WGW&â4„Teõ$ôÕE2ævWB†6†Veö–BÂ4„Teõ$ôÕE5²&6†Vb×¦Ö%Ò  ¦7–æ2FVböçF‡&÷–2†ÖW76vW3¢Æ—7E¶F–7E·7G"Â7G&•ÒÂ7—7FVÓ¢7G"’Óâ7G# ¢–bæ÷B6WGF–æw2äåD…$õ”5ô•ô´U“ ¢&—6R'VçF–ÖTW'&÷"‚$’&÷f–FW"—2æ÷B6öæf–wW&VB" ¢–ÆöBÒ°¢&ÖöFVÂ#¢6WGF–æw2äåD…$õ”5ôÔôDTÂÀ¢&Ö…÷Fö¶Vç2#¢ƒÀ¢'FV×W&GW&R#¢ãrÀ¢'7—7FVÒ#¢7—7FVÒÀ¢&ÖW76vW2#¢ÖW76vW2À¢Ğ¢†VFW'2Ò°¢'‚Ö’Ö¶W’#¢6WGF–æw2äåD…$õ”5ô•ô´U’À¢&çF‡&÷–2×fW'6–öâ#¢###2ÓbÓ"À¢&6öçFVçB×G—R#¢&Æ–6F–öâö§6öâ"À¢Ğ ¢7–æ2v—F‚‡GG‚ä7–æ46Æ–VçB‡F–ÖV÷WC×6WGF–æw2äåD…$õ”5õD”ÔTõUEõ4T4ôäE2’26Æ–VçC ¢&W7öç6RÒv—B6Æ–VçBç÷7B€¢&‡GG3¢òö’æçF‡&÷–2æ6öÒ÷cöÖW76vW2"À¢†VFW'3Ö†VFW'2À¢§6öã×–ÆöBÀ¢¢&W7öç6Rç&—6Uöf÷%÷7FGW2‚¢&öG’Ò&W7öç6Ræ§6öâ‚ ¢FW‡E÷'G2Ò°¢&Æö6²ævWB‚'FW‡B"Â""¢f÷"&Æö6²–â&öG’ævWB‚&6öçFVçB"ÂµÒ¢–b&Æö6²ævWB‚'G—R"’ÓÒ'FW‡B ¢Ğ¢&W7VÇBÒ ¢"æ¦ö–â‡FW‡E÷'G2’ç7G&—‚¢–bæ÷B&W7VÇC ¢&—6R'VçF–ÖTW'&÷"‚$’&÷f–FW"&WGW&æVBâV×G’&W7öç6R"¢&WGW&â&W7VÇ@  ¦FVb÷'6Uö§6öâ‡FW‡C¢7G"’ÓâF–7C ¢6ÆVæVBÒFW‡Bç7G&—‚¢–b6ÆVæVBç7F'G7v—F‚‚&"“ ¢6ÆVæVBÒ6ÆVæVBç&VÖ÷fW&Vf—‚‚&§6öâ"’ç&VÖ÷fW&Vf—‚‚&"’ç&VÖ÷fW7Vff—‚‚&"’ç7G&—‚¢G'“ ¢fÇVRÒ§6öâæÆöG2†6ÆVæVB¢W†6WB§6öâä¥4ôäFV6öFTW'&÷"2W†3 ¢&—6R'VçF–ÖTW'&÷"‚$’&÷f–FW"&WGW&æVB–çfÆ–B7G'V7GW&VBFF"’g&öÒW†0¢–bæ÷B—6–ç7Fæ6R‡fÇVRÂF–7B“ ¢&—6R'VçF–ÖTW'&÷"‚$’&÷f–FW"&WGW&æVBâ–çfÆ–B&V6—Rö&¦V7B"¢&WGW&âfÇVP  ¦7–æ2FVbvVæW&FU÷&V6—R‡&WVW7C¢&V6—TvVæW&F–öå&WVW7B’Óâ&V6—U&W7öç6S ¢–æw&VF–VçG2Ò&WVW7Bææ÷&ÖÆ—¦VEö–æw&VF–VçG2‚¢7—7FVÒÒb""'µö6†Ve÷&ö×B‡&WVW7Bæ6†Veö–B—Ğ ¤7&VFR&VÆ—7F–26÷WF‚g&–6â&V6—RW6–æröæÇ’F†R7WÆ–VB–æw&VF–VçG2ÇW2÷&F–æ'’vFW"Â6ÇBÂWW"æB6öö¶–ærö–Âv†W&RæV6W76'’à¤Fòæ÷B–çfVçBVæf–Æ&ÆR–æw&VF–VçG2à¥&WGW&âôäÅ’fÆ–B¥4ôâÖF6†–ærF†—26†S §·°¢'&V6—UöæÖR#¢'7G&–ær"À¢'&V6—UöFW67&—F–öâ#¢'7G&–ær"À¢&–æw&VF–VçG2#¢²'7G&–ær%ÒÀ¢&–ç7G'V7F–öç2#¢²'7G&–ær%ÒÀ¢'F—2#¢'7G&–ær"À¢&6öö¶–æu÷F–ÖR#¢'7G&–ær §×Ğ¤¶VW–ç7G'V7F–öç26fRÂ&7F–6ÂæB6öæ6—6Râ""  ¢W6W"Òb$7&VFR&V6—Rf÷"·&WVW7Bæ6†VeöæÖWÒâf–Æ&ÆR–æw&VF–VçG3¢²rÂræ¦ö–â†–æw&VF–VçG2—Ò ¢&rÒv—BöçF‡&÷–2…·²'&öÆR#¢'W6W""Â&6öçFVçB#¢W6W'ÕÒÂ7—7FVÒ¢&WGW&â&V6—U&W7öç6RæÖöFVÅ÷fÆ–FFR…÷'6Uö§6öâ‡&r’  ¦7–æ2FVb†æFÆUöföÆÆ÷wW÷VW7F–öâ€¢VW7F–öã¢7G"À¢6†Veö–C¢7G"À¢6†VeöæÖS¢7G"À¢&V6—Uö6öçFW‡C¢7G"Ò""À¢’ÓâföÆÆ÷uW&W7öç6S ¢VW7F–öâÒVW7F–öâç7G&—‚¢–bæ÷BVW7F–öã ¢&—6RfÇVTW'&÷"‚%VW7F–öâ—2&WV—&VB" ¢7—7FVÒÒb""'µö6†Ve÷&ö×B†6†Veö–B—Ğ ¤ç7vW"6öö¶–ærföÆÆ÷r×WVW7F–öâ&÷WBF†RW6W"w27W'&VçB&V6—Rà¤&R6öæ6—6RÂ&7F–6ÂæB6fRâFòæ÷B6Æ–ÒFò†fRW&f÷&ÖVB7F–öç2–÷R6ææ÷BW&f÷&Òâ""  ¢6öçFW‡BÒ&V6—Uö6öçFW‡Bç7G&—‚•³£Ğ¢W6W"Òb$7W'&VçB&V6—S §¶6öçFW‡GĞ ¥VW7F–öâg&öÒF†R6öö³¢·VW7F–öçĞ¤6†Vc¢¶6†VeöæÖWÒ ¢&rÒv—BöçF‡&÷–2…·²'&öÆR#¢'W6W""Â&6öçFVçB#¢W6W'ÕÒÂ7—7FVÒ¢'6VBÒ÷'6Uö§6öâ‡&r¢&WGW&âföÆÆ÷uW&W7öç6R‡&W7öç6S×7G"‡'6VBævWB‚'&W7öç6R"Â&r’•³£CÒ