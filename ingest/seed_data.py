"""Curated seed list for the launch.

Each entry names a *real* public-domain work in the Met or Art Institute of
Chicago collection. We resolve the museum's object by SEARCH (so we don't depend
on brittle hard-coded IDs) and verify it is public domain before importing.

The explanation text below is a STARTER draft — accurate but intentionally
short. Refine it (and tune hotspot x/y, which are best-guess %s) in the Supabase
table editor after import.

Fields:
  source       "met" | "artic"
  query        search string sent to the museum API
  artist_match surname used to disambiguate the search result
  slug         URL slug on the site
  movement     art movement / period
  featured     show on the home page
  summary      one-line hook
  why_watch    "why people stare for hours"
  body         full explanation (markdown)
  tags         theme slugs (auto-created)
  hotspots     [{x, y, title, detail}] — x/y are % of the image (0–100)
"""

SEEDS = [
    {
        "source": "artic",
        "query": "At the Moulin Rouge",
        "artist_match": "Lautrec",
        "slug": "at-the-moulin-rouge",
        "wikimedia": "Toulouse-Lautrec At the Moulin Rouge Google Art Project",
        "movement": "Post-Impressionism",
        "featured": True,
        "summary": "A nightclub scene with the painter himself hidden in the crowd — and a face lit like a ghost.",
        "why_watch": (
            "At first it's just a smoky Paris nightclub, but keep looking and the "
            "secrets surface: a tiny top-hatted man in the background is "
            "Toulouse-Lautrec painting himself beside his very tall cousin, and "
            "at the lower right a woman's face glows an unnatural green and orange, "
            "lit from below like a mask. The off-balance, cropped composition keeps "
            "pulling your eye around the room, never letting it rest."
        ),
        "body": (
            "Henri de Toulouse-Lautrec painted *At the Moulin Rouge* around "
            "1892–95, capturing the famous Montmartre cabaret he frequented. The "
            "steep, tilted floor and the railing slicing across the foreground "
            "come straight from Japanese prints and the new art of photography — "
            "the scene feels glimpsed rather than posed.\n\n"
            "Two details reward the patient viewer. In the background, a short man "
            "in a bowler walks beside a strikingly tall one: that's Lautrec "
            "himself (who stood under five feet) next to his cousin Dr. Gabriel "
            "Tapié de Céleyran — a sly self-portrait tucked into the crowd. At the "
            "lower right, the face of the dancer May Milton is lit harshly from "
            "below, washed in green and orange, an almost ghostly effect created "
            "by the cabaret's gaslight. The canvas was later cut down and only "
            "partially restored, which is why the composition feels so abruptly "
            "cropped."
        ),
        "tags": ["hidden-figures", "self-portrait", "nightlife"],
        "hotspots": [
            {"x": 60, "y": 30, "title": "Lautrec's hidden self-portrait",
             "detail": "The short man in a bowler hat beside the very tall figure in the background is the painter himself, next to his cousin."},
            {"x": 84, "y": 72, "title": "The green-lit face",
             "detail": "Dancer May Milton's face is lit from below, glowing green and orange like a mask — the painting's eeriest detail."},
        ],
    },
    {
        "source": "artic",
        "query": "A Sunday on La Grande Jatte",
        "artist_match": "Seurat",
        "slug": "la-grande-jatte",
        "movement": "Post-Impressionism (Pointillism)",
        "featured": True,
        "summary": "Two million dots of paint that only resolve into a Sunday afternoon inside your own eye.",
        "why_watch": (
            "Seurat didn't mix his colors on a palette — he placed tiny dots of "
            "pure pigment side by side and let your eye blend them from a "
            "distance. Step close and the park dissolves into confetti; step "
            "back and it snaps into a hushed, frozen Sunday. Watching the image "
            "flicker between those two states is genuinely hypnotic, and you "
            "start noticing the strange stillness of every figure, like a stage "
            "set holding its breath."
        ),
        "body": (
            "Georges Seurat spent two years (1884–86) building *A Sunday on La "
            "Grande Jatte* from millions of small, deliberate strokes — a "
            "technique he called *divisionism*, popularly known as pointillism. "
            "He believed optical mixing produced more luminous color than mixing "
            "paint on the palette.\n\n"
            "Beyond the technique, the park is full of quiet oddities: the "
            "figures are rigid and weirdly formal, more like Egyptian friezes "
            "than people relaxing. A woman on the right walks a monkey on a "
            "leash; a small dog and a butterfly animate the foreground. Seurat "
            "even painted a hand-dotted *border* around the canvas to ease the "
            "transition to the frame. Scholars still debate whether the scene is "
            "a gentle social satire of the Parisian middle class at leisure."
        ),
        "tags": ["technique", "optical-illusion", "impressionism"],
        "hotspots": [
            {"x": 86, "y": 52, "title": "The pet monkey",
             "detail": "On a leash beside the well-dressed woman — a sly, easily-missed detail that has puzzled viewers for over a century."},
            {"x": 4, "y": 96, "title": "Seurat's painted border",
             "detail": "He dotted a border directly onto the canvas so the eye eases from image to frame."},
        ],
    },
    {
        "source": "artic",
        "query": "Paris Street Rainy Day",
        "artist_match": "Caillebotte",
        "slug": "paris-street-rainy-day",
        "movement": "Impressionism",
        "featured": False,
        "summary": "A wet Paris intersection built on near-perfect one-point perspective.",
        "why_watch": (
            "Caillebotte photographs the city with a paintbrush: the cobbles "
            "gleam, the umbrellas tilt, and a single green lamppost slices the "
            "canvas into a precise grid. Once you spot the geometry holding it "
            "all together, you can't unsee how engineered this 'casual' street "
            "scene really is."
        ),
        "body": (
            "Painted in 1877, *Paris Street; Rainy Day* shows the new, "
            "Haussmann-era boulevards near the Gare Saint-Lazare. Caillebotte, "
            "trained as an engineer, used rigorous one-point perspective and a "
            "near-photographic crop — the man at right is sliced by the frame as "
            "a camera might cut him. The lamppost divides the composition almost "
            "exactly in half, and figures recede in carefully measured steps. "
            "It's Impressionist subject matter rendered with classical "
            "discipline."
        ),
        "tags": ["technique", "impressionism", "city"],
        "hotspots": [],
    },
    {
        "source": "artic",
        "query": "The Bedroom Van Gogh",
        "artist_match": "Gogh",
        "slug": "the-bedroom",
        "wikimedia": "1926.417 Van Gogh Bedroom Art Institute",
        "movement": "Post-Impressionism",
        "featured": True,
        "summary": "Van Gogh's tilting little room, painted as a picture of the rest he could rarely find.",
        "why_watch": (
            "The walls lean, the floor pitches, the furniture crowds forward — "
            "nothing in this room sits straight, yet Van Gogh insisted the "
            "picture should express 'rest' and 'sleep.' Knowing how much peace "
            "he was chasing makes the off-kilter perspective and the paired "
            "objects (two chairs, two pillows, two portraits) quietly heartbreaking."
        ),
        "body": (
            "Van Gogh painted this version of his bedroom in Arles in 1889 while "
            "at the asylum in Saint-Rémy, copying an 1888 original. In letters to "
            "his brother Theo he stressed that flat, vivid color — not shadow — "
            "should carry the feeling, and that the subject was *rest*. Yet the "
            "perspective is deliberately warped and the room oddly trapezoidal, "
            "partly because the real room had a slanted wall. Everything comes in "
            "pairs, hinting at the companionship and stability he longed for."
        ),
        "tags": ["color", "post-impressionism", "biography"],
        "hotspots": [],
    },
    {
        "source": "artic",
        "query": "The Child's Bath Cassatt",
        "artist_match": "Cassatt",
        "slug": "the-childs-bath",
        "movement": "Impressionism",
        "featured": False,
        "summary": "An intimate domestic moment seen from a daring bird's-eye angle.",
        "why_watch": (
            "Cassatt tips the whole scene toward us from above, flattening the "
            "floor and patterning every surface — a composition she borrowed "
            "from the Japanese woodblock prints flooding into Paris. It feels "
            "tender and modern at once."
        ),
        "body": (
            "Mary Cassatt, the American Impressionist working in Paris, painted "
            "*The Child's Bath* in 1893. The high vantage point, cropped forms, "
            "and bold clash of patterned wallpaper, rug, and dress show how "
            "deeply she absorbed Japanese *ukiyo-e* prints. The bond between "
            "woman and child — Cassatt's recurring subject — is conveyed through "
            "the gentle, shared focus on a single, ordinary task."
        ),
        "tags": ["composition", "impressionism", "japonisme"],
        "hotspots": [],
    },
    {
        "source": "met",
        "query": "The Harvesters Bruegel",
        "artist_match": "Bruegel",
        "slug": "the-harvesters",
        "movement": "Northern Renaissance",
        "featured": True,
        "summary": "A wheat field so alive you can almost hear the cicadas and the snoring.",
        "why_watch": (
            "Bruegel turns a chore into a whole world: harvesters scythe and "
            "stack while one man sprawls asleep under a tree, mouth open, belly "
            "up. Wander the painting and you keep finding tiny human comedies — "
            "people swimming, eating, carrying jugs — until the labor of an "
            "entire village unfolds in front of you."
        ),
        "body": (
            "Painted in 1565, *The Harvesters* is one of a series Bruegel made "
            "depicting the seasons. It's a landmark in Western art: the everyday "
            "labor of peasants, not gods or saints, fills a monumental canvas, "
            "and the landscape recedes naturalistically into a hazy distance. "
            "The pear tree at the center organizes the scene, separating the "
            "workers still cutting wheat from those pausing to eat and doze. "
            "Look into the deep background for swimmers, a distant village, and a "
            "game being played — Bruegel rewards the patient eye."
        ),
        "tags": ["hidden-figures", "landscape", "renaissance"],
        "hotspots": [
            {"x": 33, "y": 62, "title": "The sleeping man",
             "detail": "Sprawled under the pear tree, mouth open — the painting's comic, human center."},
            {"x": 78, "y": 40, "title": "Distant swimmers",
             "detail": "Tiny figures bathe in a far-off pond; Bruegel hides small scenes throughout the background."},
        ],
    },
    {
        "source": "met",
        "query": "Washington Crossing the Delaware Leutze",
        "artist_match": "Leutze",
        "slug": "washington-crossing-the-delaware",
        "movement": "History Painting / Romanticism",
        "featured": True,
        "summary": "A patriotic icon packed with details that are gloriously, deliberately wrong.",
        "why_watch": (
            "It's one of the most reproduced images in American history — and "
            "almost everything in it is staged for drama rather than accuracy: "
            "the wrong flag, the wrong time of day, ice that never looked like "
            "that. Spotting the 'mistakes' Leutze chose on purpose turns a "
            "familiar poster into a detective game."
        ),
        "body": (
            "Emanuel Leutze painted this 12-foot canvas in 1851, in Germany, to "
            "inspire European revolutionaries with American resolve. Historically "
            "it's full of liberties: the Stars and Stripes shown didn't exist on "
            "the night of December 25–26, 1776; the boats and floating ice are "
            "wrong for the Delaware; and Washington would not have stood like "
            "that in a small craft. Leutze wasn't documenting — he was building a "
            "heroic myth, and the diagonal of light, flag, and Washington's gaze "
            "all drive the eye toward an unseen, hopeful dawn."
        ),
        "tags": ["history", "american-art", "myth-vs-fact"],
        "hotspots": [
            {"x": 60, "y": 30, "title": "An anachronistic flag",
             "detail": "The Stars and Stripes shown here wasn't adopted until 1777 — months after the crossing."},
        ],
    },
    {
        "source": "met",
        "query": "Madame X Sargent",
        "artist_match": "Sargent",
        "slug": "madame-x",
        "movement": "Portraiture",
        "featured": False,
        "summary": "The scandalous portrait that nearly ended Sargent's career — over a fallen strap.",
        "why_watch": (
            "That cool profile and pale skin look untouchable now, but in 1884 "
            "Paris was scandalized — originally one jeweled strap slipped off the "
            "sitter's shoulder, read as shockingly risqué. Sargent repainted it "
            "up, but the whiff of scandal still hums under the elegance."
        ),
        "body": (
            "John Singer Sargent's portrait of the American socialite Virginie "
            "Amélie Avegno Gautreau debuted at the 1884 Paris Salon and was met "
            "with outrage — partly for the provocative pose and powdered, "
            "lavender-pale skin, and partly because one diamond strap was "
            "originally shown sliding off her shoulder. The backlash hurt both "
            "their reputations; Sargent later repainted the strap upright and "
            "moved to London. He kept the canvas for decades, calling it the best "
            "thing he had ever done."
        ),
        "tags": ["portrait", "scandal", "biography"],
        "hotspots": [],
    },
    {
        "source": "met",
        "query": "Young Woman with a Water Pitcher Vermeer",
        "artist_match": "Vermeer",
        "slug": "young-woman-with-a-water-pitcher",
        "movement": "Dutch Golden Age",
        "featured": False,
        "summary": "Vermeer's quiet light, falling on an ordinary morning as if on something sacred.",
        "why_watch": (
            "Vermeer makes you watch light itself: the way it filters through "
            "the leaded window, glows in the brass basin, and softens the white "
            "linen cap. Nothing happens, and yet the stillness feels charged — "
            "the everyday made luminous and timeless."
        ),
        "body": (
            "Painted around 1662, this is a quintessential Vermeer interior: a "
            "single woman, a window at left, a tiled floor, and a table laid with "
            "carefully observed objects. Vermeer's mastery is in the optics — the "
            "diffuse daylight, the colored reflections in the metal, the subtle "
            "blue shadow in the white cloth. The map on the back wall and the "
            "rich rug are typical Dutch markers of trade and comfort. It is one "
            "of the first Vermeers to enter an American collection."
        ),
        "tags": ["light", "dutch-golden-age", "interior"],
        "hotspots": [],
    },
]
