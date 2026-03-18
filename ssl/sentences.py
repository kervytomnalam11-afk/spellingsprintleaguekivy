# sentences.py — Long sentences for Sentence Race mode
import random

_SENTENCES = [
    "the quick brown fox jumps over the lazy dog near the riverbank",
    "she sells seashells by the seashore every morning before sunrise",
    "how much wood would a woodchuck chuck if a woodchuck could chuck wood",
    "peter piper picked a peck of pickled peppers from the garden",
    "to be or not to be that is the question worth asking every day",
    "all that glitters is not gold but it certainly catches the eye",
    "a journey of a thousand miles begins with a single step forward",
    "the early bird catches the worm but the second mouse gets the cheese",
    "practice makes perfect and perfect practice makes champions",
    "in the middle of every difficulty lies a great opportunity waiting",
    "the only way to do great work is to love what you do every day",
    "success is not final and failure is not fatal it is the courage that counts",
    "the best time to plant a tree was twenty years ago and the second best time is now",
    "not all those who wander are lost some are just exploring new paths",
    "we are the music makers and we are the dreamers of dreams together",
    "two roads diverged in a yellow wood and I took the one less traveled",
    "it was the best of times it was the worst of times it was an age of wisdom",
    "ask not what your country can do for you ask what you can do for your country",
    "that which does not kill us makes us stronger and wiser in the end",
    "the measure of intelligence is the ability to change and adapt quickly",
    "imagination is more important than knowledge for knowledge is limited",
    "in the beginning was the word and the word was with everything we know",
    "fortune favors the bold but preparation favors the fortunate among us",
    "where there is a will there is always a way through any obstacle",
    "the pen is mightier than the sword when wielded with precision and care",
    "every great dream begins with a dreamer who refuses to give up hope",
    "the secret of getting ahead is getting started with whatever you have",
    "life is what happens when you are busy making other plans for yourself",
    "the greatest glory in living lies not in never falling but in rising",
    "do not go gentle into that good night rage rage against the dying light",
    "we shape our tools and thereafter our tools shape us in return",
    "the universe is under no obligation to make sense to anyone at all",
    "with great power comes great responsibility and the wisdom to use it",
    "be the change you wish to see in the world starting from this moment",
    "knowledge speaks but wisdom listens and understanding bridges the two",
    "the mind is everything and what you think you ultimately become over time",
    "an unexamined life is not worth living according to ancient philosophers",
    "the only true wisdom is knowing that you know nothing at all",
    "we must accept finite disappointment but never lose infinite hope within",
    "the future belongs to those who believe in the beauty of their dreams",
    "spread love everywhere you go let no one ever come to you without leaving happier",
    "when you reach the end of your rope tie a knot in it and hang on tight",
    "always remember that you are absolutely unique just like everyone else",
    "do not pray for easy lives pray to be stronger men and better people",
    "it does not matter how slowly you go as long as you do not stop moving",
    "our greatest fear is not that we are inadequate but that we are powerful",
    "everything you ever wanted is on the other side of fear and hesitation",
    "start where you are use what you have do what you can right now today",
    "believe you can and you are already halfway there on your journey forward",
    "you miss one hundred percent of the shots you never even take in life",
]

def get_sentences(count: int = 30) -> list[str]:
    """Return a shuffled list of sentences."""
    pool = _SENTENCES.copy()
    random.shuffle(pool)
    result = []
    while len(result) < count:
        random.shuffle(pool)
        result.extend(pool)
    return result[:count]

def sentences_to_words(sentences: list[str]) -> tuple[list[str], list[int]]:
    """
    Flatten sentences into a word list.
    Returns (words, sentence_ends) where sentence_ends[i] is the
    word index of the last word in sentence i.
    """
    words: list[str] = []
    boundaries: list[int] = []
    for s in sentences:
        ws = s.strip().split()
        words.extend(ws)
        boundaries.append(len(words) - 1)
    return words, boundaries
