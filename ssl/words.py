# words.py — Word bank + randomizer
import random

_EASY = [
    "the","be","to","of","and","a","in","that","have","it","for","not","on",
    "with","as","you","do","at","this","but","by","from","they","we","say","she",
    "or","an","will","my","one","all","would","there","their","what","so","up",
    "out","if","about","who","get","which","go","me","when","make","can","like",
    "time","no","just","him","know","take","into","year","your","good","some",
    "see","other","than","then","now","look","only","come","over","think","also",
    "back","after","use","two","how","our","work","first","well","way","even",
    "new","want","these","give","day","most","us","run","cat","dog","play","win",
    "fast","word","type","key","tap","hit","aim","jump","game","race","fun","set",
]

_MEDIUM = [
    "python","keyboard","monitor","software","algorithm","function","variable",
    "computer","internet","digital","language","system","process","memory","storage",
    "interface","framework","library","module","package","browser","server","client",
    "request","response","position","problem","question","solution","practice",
    "exercise","challenge","complete","project","develop","achieve","success",
    "improve","progress","journey","important","consider","together","between",
    "through","another","because","example","support","general","student","teacher",
    "program","design","button","screen","window","folder","symbol","message",
    "network","science","history","english","subject","chapter","section","reading",
    "writing","spelling","testing","running","jumping","playing","winning","scoring",
    "accuracy","velocity","reaction","champion","practice","strategy","keyboard",
]

_HARD = [
    "acknowledge","circumstances","consequently","demonstrate","enthusiastic",
    "fundamental","geographical","hypothetical","independently","jurisdiction",
    "knowledgeable","legitimate","mathematician","nevertheless","opportunities",
    "particularly","qualification","responsibility","sophisticated","technological",
    "unprecedented","vulnerability","approximately","bureaucratic","characteristic",
    "collaborative","communication","concentration","continuously","contradictory",
    "controversial","corresponding","deteriorating","disadvantaged","disappointing",
    "discrimination","documentation","electromagnetic","environmental","establishment",
    "evolutionary","exaggerating","extraordinary","hallucination","simultaneously",
    "internationally","representative","comprehensively","miscommunication",
    "underprivileged","perpendicular","thermodynamics","anthropological",
    "entrepreneurship","electromagnetic","interdisciplinary","uncharacteristically",
]

POOLS = {
    "Easy":   _EASY,
    "Medium": _EASY + _MEDIUM,
    "Hard":   _MEDIUM + _HARD,
    "Mixed":  _EASY + _MEDIUM + _HARD,
}

def get_words(difficulty: str = "Mixed", count: int = 200) -> list[str]:
    pool = POOLS.get(difficulty, POOLS["Mixed"]).copy()
    words: list[str] = []
    while len(words) < count:
        random.shuffle(pool)
        words.extend(pool)
    return words[:count]
