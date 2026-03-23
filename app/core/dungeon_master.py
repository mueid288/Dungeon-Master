import os
from dotenv import load_dotenv
from groq import Groq
import json

load_dotenv() 
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

START_PROMPT = """
Tum aik legendary Dungeon Master ho jo ek nai aur unique kahani shuru kar raha hai.

TUMHARA KAAM:
1. Is campaign ki theme se inspired ek UNIQUE main quest banao
2. Ek yaadgar villain create karo jiska apna motive ho
3. Ek dramatic opening scene likho jo players ko andar kheench le
4. Har character ka opening mein zikar karo

STORY STRUCTURE YAAD RAKHO:
- Shuruat mein world aur khatra introduce karo
- Quest clear honi chahiye — players ko pata ho kya karna hai
- Villain mysterious hona chahiye — seedha saamne mat lao

RESPONSE FORMAT:
Sirf is JSON mein jawab do, koi extra text nahi:
{
    "opening": "dramatic opening scene Roman Urdu mein (3-4 paragraphs)",
    "main_quest": "ek line mein — players ko kya achieve karna hai",
    "villain": "villain ka naam aur ek line description",
    "location": "pehli location ka naam",
    "situation": "abhi kis khatra mein hain players",
    "next_options": ["option 1", "option 2", "option 3"]
}
"""

def build_system_prompt(action_count: int) -> str:
    
    if action_count < 5:
        story_stage = "SHURUAT (Act 1): Duniya aur characters introduce karo. Pehla khatra dikhao. Villain ke hints do lekin seedha mat dikhao."
    elif action_count < 15:
        story_stage = "DARMIYAAN (Act 2): Stakes barhaao. Ek unexpected twist lao. Players ko villain ke baare mein kuch reveal karo. Mushkilaat barhaao."
    elif action_count < 20:
        story_stage = "CLIMAX (Act 3): Final confrontation ki taraf badhao. Villain ka seedha khatra aao. Har action ke consequences zyada dramatic hon."
    else:
        story_stage = "ANJAAM (Act 4): Kahani khatam karne ka waqt hai. Is action mein story ka conclusion lao — chahe victory ho ya tragedy."

    return f"""
Tum aik legendary Dungeon Master ho jo ek living, breathing RPG world mein story narrate karta hai.

STORY STAGE:
{story_stage}

CORE RULES:
- Har cheez Roman Urdu mein likho
- Main quest ko har scene mein relevance do — random events mat karo
- Character class matter karta hai (rogue = stealth, mage = spells, warrior = combat)
- Dice roll (1-20) ke mutabiq outcome decide karo:
  * 1-5   = bura result, consequences hon
  * 6-10  = partial fail, kuch cost ho
  * 11-15 = success
  * 16-19 = great success, bonus mile
  * 20    = EPIC — kuch unexpected amazing ho
- Past decisions YAAD rakho aur unka asar dikhao
- Villain ko alive rakho jab tak climax na aaye
- Agar health 0 ho jaye — game over likho

IMPORTANT:
- Agar story naturally khatam ho rahi hai to "game_over": true karo
- Agar main quest complete ho — "quest_complete": true karo

RESPONSE FORMAT:
Sirf is JSON mein jawab do:
{{
    "narrative": "story Roman Urdu mein (2-3 paragraphs, cinematic)",
    "dice_roll": 1-20,
    "success": true/false,
    "damage_taken": 0,
    "damage_dealt": 0,
    "item_gained": null or "item name",
    "item_lost": null or "item name",
    "xp_gained": 0,
    "importance": "low/high/critical",
    "world_update": null or "duniya mein kya badla",
    "game_over": false,
    "quest_complete": false,
    "next_options": ["option 1", "option 2", "option 3"]
}}
"""

def build_game_context(character, campaign, recent_memories, critical_memories):
    
    inventory_list = ", ".join(
        [f"{item.item_name} x{item.quantity}" for item in character.inventory]
    ) or "kuch nahi"

    recent_history = "\n".join(
        [f"- Player: {m.action}\n  DM: {m.ai_response[:100]}..." 
         for m in recent_memories]
    ) or "Abhi game shuru hua hai"

    critical_history = "\n".join(
        [f"- {m.action} (important!)" for m in critical_memories]
    ) or "Koi critical event nahi hua abhi tak"

    return f"""
        CAMPAIGN: {campaign.name}
        THEME: {campaign.theme}
        STORY SO FAR: {campaign.summary or "Nayi kahani shuru ho rahi hai..."}

        CHARACTER INFO:
        - Naam: {character.name}
        - Class: {character.char_class}
        - Health: {character.health}/{character.max_health}
        - Level: {character.level}
        - XP: {character.xp}
        - Inventory: {inventory_list}

        CRITICAL PAST EVENTS:
        {critical_history}

        LAST 5 ACTIONS:
        {recent_history}
        """


def ask_dungeon_master(character, campaign, recent_memories, critical_memories, player_action: str):
    
    system = build_system_prompt(campaign.action_count)
    context = build_game_context(character, campaign, recent_memories, critical_memories)
    context += f"""
                MAIN QUEST: {campaign.main_quest or "Abhi generate nahi hua"}
                VILLAIN: {campaign.villain or "Unknown"}
                ACTION NUMBER: {campaign.action_count + 1}
                """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"{context}\n\nPLAYER ACTION: {player_action}"}
            ],
            temperature=0.8,
        )

        raw = response.choices[0].message.content
        clean = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)

    except json.JSONDecodeError:
        return {
            "narrative": "Andhera chhaa gaya... kuch mysterious hua. Dobara koshish karo.",
            "dice_roll": 10,
            "success": False,
            "damage_taken": 0,
            "damage_dealt": 0,
            "item_gained": None,
            "item_lost": None,
            "xp_gained": 0,
            "importance": "low",
            "world_update": None,
            "next_options": ["Aage badho", "Ruko aur suno", "Wapas jao"]
        }

def start_game(characters: list, campaign):
    char_list = "\n".join([
        f"- {c.name} ({c.char_class}, Level {c.level})"
        for c in characters
    ])

    prompt = f"""
        CAMPAIGN: {campaign.name}
        THEME: {campaign.theme}

        PARTY MEMBERS:
        {char_list}

        In poore group ki kahani ek saath shuru karo.
        Har character ka zikar karo opening mein.
        """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": START_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
        )
        raw = response.choices[0].message.content
        clean = raw.replace("```json","").replace("```","").strip()
        return json.loads(clean)
         
    except json.JSONDecodeError:
        return {
            "opening": "Andheri raat mein tumhari kahani shuru hoti hai...",
            "location": "Mysterious Jungle",
            "situation": "Tum akele ho aur raasta gum ho gaya hai",
            "next_options": ["Aage badho", "Ruko aur suno", "Wapas jao"]
        }