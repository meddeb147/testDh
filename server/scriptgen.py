"""Viral voice-over script writer (Claude), with an offline fallback so the app works without an API key."""
import json, os, random

GENRES = [
    dict(id="relationships", label="Relationships", emoji="💔"), dict(id="romance", label="Romance", emoji="🌹"),
    dict(id="horror", label="Horror", emoji="🕯️"), dict(id="mystery", label="Mystery", emoji="🕵️"),
    dict(id="true crime", label="True crime", emoji="🔎"), dict(id="comedy", label="Comedy", emoji="😂"),
    dict(id="motivation", label="Motivation", emoji="🔥"), dict(id="psychology", label="Psychology", emoji="🧠"),
    dict(id="facts", label="Mind-blowing facts", emoji="🤯"), dict(id="kids story", label="Kids story", emoji="🧸"),
    dict(id="history", label="History", emoji="🏛️"), dict(id="tech", label="Tech & AI", emoji="🤖"),
]
LANGUAGES = ["English", "French", "Spanish", "Portuguese", "German", "Italian", "Arabic", "Turkish", "Indonesian"]

PLAYBOOK = """You write voice-over scripts for faceless short-form videos (TikTok, Reels, Shorts) that are also cut into a
long YouTube version and short clips. Hand-drawn motion graphics will animate every line, so lines must be visual.

What makes a topic travel (hit at least 3): recognition ("this is literally me"), a reframe that flips a common belief,
one strong emotion, debate fuel, concrete drawable objects/actions, series potential.

Script formula:
- Hook (first 3 s): a reframe, question, rule ("If you ever... don't...") or shocking statement. No intro, no "hey guys".
- Tension (3-15 s): why the obvious explanation is wrong.
- Story / mechanism: step-by-step escalation in short, concrete, visual lines.
- Turn: the painful, surprising or chilling consequence.
- Payoff: actionable advice / chilling twist / punchline, then one memorable closing line.
- CTA (last 3 s): share + follow, adapted to the genre (horror: "follow for part two").

Writing rules: one idea per sentence, 4-12 words. Use "…" for dramatic pauses and periods for beats. Lists of three and
contrasts. Every 2-3 lines should be drawable as one picture. Consistent he/she/you. No names of real people, no brands,
no product or book plugs, no medical or legal claims, never invent statistics (only well-known, credible findings).
Write numbers and times as words so a narrator reads them naturally ("three seventeen", "eighty-six percent").
Genre arcs: relationships = recognition -> ache -> hope; horror = calm -> unease -> dread -> twist; comedy = setup ->
escalation -> punchline + callback; motivation = pain -> realization -> resolve; mystery = curiosity -> reveal -> bigger
question; facts/psychology = surprise -> explanation -> practical takeaway; kids story = wonder -> small problem ->
kind, clever solution -> gentle moral (simple words, no scary content)."""

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["title", "label", "why_it_travels", "script", "caption", "hashtags", "backup_ideas", "youtube_title"],
    "properties": {
        "title": {"type": "string", "description": "short working title"},
        "label": {"type": "string", "description": "2-5 word ALL CAPS label shown at the top of every frame"},
        "why_it_travels": {"type": "array", "items": {"type": "string"}, "description": "2-3 short bullets"},
        "script": {"type": "string", "description": "the exact voice-over text, one paragraph per beat"},
        "caption": {"type": "string", "description": "one-line post caption, may include 1-2 emoji"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "backup_ideas": {"type": "array", "items": {"type": "string"}, "description": "2-3 one-line alternative topics"},
        "youtube_title": {"type": "string", "description": "a curiosity-gap title for the long YouTube version"},
    },
}


def words_for(seconds, language):
    rate = 2.5 if language == "English" else 2.3
    return int(seconds * rate)


def write_script(genre, language="English", seconds=75, topic="", tone=""):
    """Returns a dict matching SCHEMA plus 'source' ('claude' or 'offline')."""
    n = words_for(seconds, language)
    try:
        import anthropic
        client = anthropic.Anthropic()
        ask = (f"Genre: {genre}\nLanguage: write everything (script, caption, hashtags, titles) in {language}.\n"
               f"Target length: about {seconds} seconds spoken, which is about {n} words (stay within ±10%).\n"
               + (f"Topic or idea from the creator: {topic}\n" if topic else "Pick the single topic with the strongest viral pull in this genre right now.\n")
               + (f"Tone: {tone}\n" if tone else "")
               + "Return the script exactly as it should be pasted into a text-to-speech tool.")
        resp = client.beta.messages.create(
            model="claude-opus-5-5", max_tokens=16000,
            betas=["server-side-fallback-2026-07-01"], fallbacks="default",
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
            system=PLAYBOOK,
            messages=[{"role": "user", "content": ask}],
        )
        if resp.stop_reason == "refusal":
            raise RuntimeError("The script request was declined. Try a different topic.")
        text = next(b.text for b in resp.content if b.type == "text")
        out = json.loads(text); out["source"] = "claude"
        return out
    except ImportError:
        pass
    except Exception as e:  # noqa: BLE001 - no key / network: fall back, but surface the reason
        if "declined" in str(e): raise
        print("Claude unavailable, using offline template:", type(e).__name__, e)
    return offline(genre, language, seconds, topic)


OFFLINE = {
    "horror": ("THE 3AM RULE", """If you ever hear knocking at three in the morning… don't open the door.

Last night, it started at exactly three. Three slow knocks. Then silence.

I told myself it was the wind. The wind doesn't knock in threes.

Then my phone lit up. A message from my neighbor: "Don't open it. I can see it from my window."

I looked through the peephole. Nobody there. Just the hallway light… flickering.

Then the knocking came again. But this time… it came from inside my closet.

I didn't move. I didn't breathe. I waited until the sun came up.

In the morning, I opened the closet. Empty. Except for three small marks on the inside of the door.

My neighbor moved out two years ago.

So if you hear knocking at three in the morning… stay in bed.

Follow for part two."""),
    "relationships": ("WHEN SHE STOPS ASKING", """When a woman stops asking you for things… it doesn't mean she's happy.

It means she's learning to live without you.

At first, she asks gently. Can you call me? Can we talk? Can you be here?

Then she asks again. And again.

Every time, she hears the same thing. "Not now." "Later." "You're overthinking."

So one day, she stops asking.

She learns to fix things alone. To celebrate alone. To cry alone.

And you think everything is finally peaceful.

But silence isn't peace. Silence is distance.

So if she's still asking… listen. Because the day she stops asking is the day she starts leaving.

Send this to someone who needs to hear it. And follow for more."""),
    "motivation": ("NOBODY IS COMING", """Nobody is coming to save you. And that's the best news you'll ever hear.

Because it means the power was always yours.

You've been waiting for the right time. The right mood. The right sign.

But motivation is a liar. It shows up after you start, not before.

Discipline is quiet. It's the alarm you don't snooze. The rep you don't skip. The message you don't send.

One small promise. Kept every day.

That's how strangers become legends.

So stop waiting for a hero. Look in the mirror. She's been ready the whole time.

Save this for the morning you want to quit. And follow for more."""),
    "kids story": ("THE LITTLE LOST STAR", """One night, a little star fell out of the sky… and landed in a garden.

It was tiny. It was scared. And its light was getting dim.

A curious cat found it first. "Why are you crying?" asked the cat.

"I can't get home," said the star. "The sky is too high."

So the cat called the owl. The owl called the frog. And the frog called every firefly in the garden.

Together, they made a ladder of light, all the way up to the moon.

The little star climbed, and climbed, and climbed… and shined brighter than ever.

Because nobody is too small to help a friend get home.

Follow for more bedtime stories."""),
}


def offline(genre, language, seconds, topic):
    key = genre if genre in OFFLINE else "relationships" if genre in ("romance",) else \
        "horror" if genre in ("mystery", "true crime") else "motivation" if genre in ("psychology", "facts", "history", "tech") else \
        "kids story" if genre == "comedy" else random.choice(list(OFFLINE))
    label, script = OFFLINE[key]
    title = " ".join(w if any(ch.isdigit() for ch in w) else w.capitalize() for w in label.lower().split()).replace("3am", "3AM")
    return dict(title=title, label=label, source="offline",
                why_it_travels=["Offline sample script (no Claude API key configured on the server).",
                                "Set ANTHROPIC_API_KEY to get a fresh, researched script for any genre and language."],
                script=script, caption=f"{title} 👀", hashtags=["#fyp", "#storytime", f"#{key.replace(' ', '')}"],
                backup_ideas=[], youtube_title=title)
