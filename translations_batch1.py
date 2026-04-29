#!/usr/bin/env python3
"""Apply IT translations from a Python dict into ink_strings.csv.

Run multiple times — each run adds its translations on top of what's already there.
EN strings missing from the dict keep their existing IT (or empty)."""
import csv
import sys
import os

# Translations: EN exact string -> IT
TRANSLATIONS = {
    # Tower of Steel — opening encounter with Zayna (the climber)
    "END SCENE": "FINE SCENA",
    "I say goodbye to Zayna.": "Saluto Zayna.",
    '<<"Ahoy there!">>': '<<"Ehilà!">>',
    "The loud, bellowing greeting nearly makes me jump out of my skin, but as I turn to see who’s there, I find only darkness...": "Il saluto sonoro e tonante quasi mi fa saltare fuori dalla pelle, ma quando mi giro per vedere chi è, trovo solo oscurità...",
    '<<"Up here!">>': '<<"Quassù!">>',
    "Now I spot a waving figure, cast in shadow.": "Ora scorgo una figura che saluta, avvolta nell'ombra.",
    '<<"Impressive, isn’t it, Glider? Are you jealous?">>': '<<"Notevole, vero, Glider? Sei gelosa?">>',
    "Of what?": "Di cosa?",
    "Very!": "Molto!",
    "Not at all!": "Per niente!",
    '<<"Me! Being up here! And having the <i>skill</i> to do it!">>': '<<"Di me! Di essere quassù! E di avere l\'<i>abilità</i> per farlo!">>',
    '<<"Ha! I knew it.">>': '<<"Ah! Lo sapevo.">>',
    '<<"Liar!">>': '<<"Bugiarda!">>',
    '<<"Bet a small fry like you couldn’t make it up here.">>': '<<"Scommetto che una piccoletta come te non riuscirebbe ad arrivare quassù.">>',
    "It’s an oddly combative energy to bring to a conversation with a stranger, I’ll give them that. Yet something about it finds a home in my brain.": "È un'energia stranamente combattiva da portare in una conversazione con uno sconosciuto, devo ammetterlo. Eppure qualcosa di tutto questo trova un posticino nella mia testa.",
    "<i>Small fry.</i>": "<i>Piccoletta.</i>",
    "Little Sable. Tiny little Sable.": "Piccola Sable. Minuscola piccola Sable.",
    "A grain of sand, tossed about by gentle wind.": "Un granello di sabbia, sballottato da un vento gentile.",
    "I look up at their tittering silhouette.": "Alzo lo sguardo verso la sua silhouette ridacchiante.",
    "<i>Challenge accepted.</i>": "<i>Sfida accettata.</i>",
    "Without sound nor word, I tap the stranger on the shoulder. They leap so high and so suddenly that I’m grateful they don’t just fall right off the ledge.": "Senza un suono né una parola, batto un colpetto sulla spalla dello sconosciuto. Salta talmente in alto e all'improvviso che sono grata non finisca direttamente giù dal cornicione.",
    "Thinking on it, it may not have been the most thoughtful way to approach.": "Ripensandoci, forse non era il modo più premuroso di avvicinarsi.",
    '<<"What--when-- who?!">>': '<<"Cosa-- quando-- chi?!">>',
    "They compose their thoughts, but regard me with a skeptical eye.": "Si ricompone, ma mi guarda con occhio scettico.",
    '<<"How did you get up here?">>': '<<"Come sei arrivata fin quassù?">>',
    "Climbed up. It’s easy.": "Mi sono arrampicata. È facile.",
    "Magic.": "Magia.",
    "Raw ambition.": "Pura ambizione.",
    "They dismiss me, more concerned with their own day.": "Mi liquida, più preoccupata della propria giornata.",
    '<<"I was looking out for Gliders I could challenge to scale this old hunk of steel!">>': '<<"Stavo cercando dei Glider da sfidare a scalare questo vecchio rottame d\'acciaio!">>',
    "I tell them they’ve found one: me. And I point to myself.": "Le dico che ne ha trovata una: io. E indico me stessa.",
    '<<"Well, it’s not much fun if you just...do it yourself, is it? Here.">>': '<<"Beh, non è molto divertente se lo fai... e basta da sola, no? Tieni.">>',
    "Annoyed, they hand me a Climber’s badge I never asked for. I take it with unappreciated gratitude.": "Seccata, mi porge un distintivo dello Scalatore che non ho mai chiesto. Lo prendo con una gratitudine non apprezzata.",
    '<<"You ruined my little game, but... at least I know this thing’s in good hands, with a Glider who knows their stuff. Hate to say it, but skills like that are hard to come by.">>': '<<"Mi hai rovinato il giochino, ma... almeno so che questa cosa è in buone mani, con una Glider che sa il fatto suo. Mi scoccia ammetterlo, ma abilità del genere non si trovano facilmente.">>',
    "Why do you hate to say it?": "Perché ti scoccia ammetterlo?",
    "Just be impressed!": "Limitati a essere colpita!",
    "I’m considering the Climber’s Mask.": "Sto pensando alla Maschera dello Scalatore.",
    '<<"That’s a fair question. I’m not sure. Possibly I’ve got a poor relationship with offering praise to others. Possibly I’m just a little grumpy.">>': '<<"Domanda giusta. Non ne sono sicura. Forse ho un brutto rapporto con i complimenti agli altri. Forse sono solo un po\' scorbutica.">>',
    "I suppose that’s fair enough.": "Suppongo sia abbastanza giusto.",
    '<<"You’re right! I should be! It’s very impressive what you did. And you’d... probably...">>': '<<"Hai ragione! Dovrei esserlo! Quello che hai fatto è molto notevole. E... probabilmente...">>',
    "They get quieter.": "Abbassa la voce.",
    '<<"You’d probably make a fine Climber.">>': '<<"Probabilmente saresti una brava Scalatrice.">>',
    '<<"You’re smart to do so. Not a lot of folks could scale this old heap like you did. Maybe next time we meet, it’ll be me sneaking up on you.">>': '<<"Fai bene a farlo. Non sono in molti a poter scalare questo vecchio rottame come hai fatto tu. Magari la prossima volta che ci incontriamo, sarò io a sgattaiolarti alle spalle.">>',
    "I tell them maybe, but that I’ve got the eyes of a hawk. They give a scoffing laugh and a dismissive little wave.": "Le dico che forse, ma che ho occhi di falco. Sbuffa una risata e fa un piccolo gesto sprezzante con la mano.",
    "I thank them for their gift, say goodbye, and get on my way.": "La ringrazio per il dono, la saluto e mi rimetto in marcia.",
    "There they are.": "Eccola lì.",
    "I walk towards the climber, chest puffed with performative pride and a well-earned swagger in my walk.": "Mi avvicino alla scalatrice, il petto gonfio di orgoglio teatrale e un'andatura strafottente meritatamente.",
    "It doesn’t matter if I’m a little sweaty; they can’t see that. It’s fine.": "Non importa se sono un po' sudata; non possono vederlo. Va bene così.",
    "Well, well, well!": "Bene, bene, bene!",
    "What were you saying, again?": "Cosa stavi dicendo, scusa?",
    "Not bad for a small fry, eh?": "Niente male per una piccoletta, eh?",
    "I think I expect more antagonism, but what I get is a laugh.": "Mi aspettavo più ostilità, ma ottengo una risata.",
    '<<"Well done! I’m... I’m impressed! And not above eating my words, when I’ve been proven wrong. Here.">>': '<<"Ben fatto! Sono... sono colpita! E non sono troppo orgogliosa per rimangiarmi le parole quando ho torto. Tieni.">>',
    "They toss a Climber’s badge my way and, mercifully, I catch it. Today really is my day.": "Mi lancia un distintivo dello Scalatore e, per fortuna, lo prendo al volo. Oggi è proprio la mia giornata.",
    '<<"You’ve earned that, Glider. Only a Climber could take that taunt and meet the challenge head-on.">>': '<<"Te lo sei guadagnato, Glider. Solo una Scalatrice potrebbe accettare quella provocazione e raccogliere la sfida a testa alta.">>',
    '<<"It’s an ascent like no other, this heap, and you should be proud you pulled it off.">>': '<<"È una scalata unica, questo rottame, e dovresti essere fiera di esserci riuscita.">>',
    '<<"I take everything back. You’re a very big fry.">>': '<<"Ritiro tutto. Sei una pezza grossa, altroché.">>',
    "I’ll take it.": "Lo accetto volentieri.",
    "Tower Of Steel": "Torre d'Acciaio",
    "I spotted a climber standing at the top of an old ruined ship.": "Ho notato una scalatrice in cima a una vecchia nave in rovina.",
    "I should climb up to meet whoever's up there.": "Dovrei arrampicarmi per andare a conoscere chiunque sia lassù.",
    "I climbed up and spoke to Zayna. They were impressed with my skills, and gave me a Climbing Badge.": "Mi sono arrampicata e ho parlato con Zayna. È rimasta colpita dalle mie abilità e mi ha dato un Distintivo dell'Arrampicata.",

    # Sometimes A Well Is Just A Well — Micah quest
    "Sometimes A Well Is Just A Well": "A Volte un Pozzo è Solo un Pozzo",
    "I spoke to Bashir at Five Bells Camp. He said his friend Micah has gone missing.": "Ho parlato con Bashir al Campo Cinque Campane. Dice che il suo amico Micah è scomparso.",
    "I should look for Micah at Thieving Magpie Well.": "Dovrei cercare Micah al Pozzo della Gazza Ladra.",
    "I should climb down and speak to the person in the well.": "Dovrei calarmi e parlare con la persona nel pozzo.",
    "I found Micah at the bottom of the well. He gave me a key, which should give me access to the machinery at the well.": "Ho trovato Micah in fondo al pozzo. Mi ha dato una chiave che dovrebbe darmi accesso ai macchinari del pozzo.",
    "I need to find a way to lift Micah out of the well.": "Devo trovare un modo per tirare Micah fuori dal pozzo.",
    "I used the crane mechanism to lift Micah out of the well.": "Ho usato il meccanismo della gru per tirare Micah fuori dal pozzo.",
    "I should speak to Micah.": "Dovrei parlare con Micah.",
    "Micah gave me a Climbing Badge for rescuing him.": "Micah mi ha dato un Distintivo dell'Arrampicata per averlo salvato.",

    # Heartbreak in the City — Zuli & Atomic Heart investigation
    "The Atomic Heart - the power station supporting Eccria - has failed. Zuli wants me to go and investigate the Heart and see what's wrong.": "Il Cuore Atomico — la centrale che alimenta Eccria — si è guastato. Zuli vuole che vada a indagare al Cuore per scoprire cosa non va.",
    "Zuli gives me a keycard that will open the door to the Heart.": "Zuli mi dà una tessera che aprirà la porta del Cuore.",
    "Zuli is waiting for me to go and investigate the Atomic Heart.": "Zuli aspetta che vada a indagare al Cuore Atomico.",
    "I tell Zuli that I found the Heart, but I haven't got anything to report yet.": "Dico a Zuli che ho trovato il Cuore, ma non ho ancora niente da riferire.",
    "The heart is out some distance away from the town. To find it, I should head to the sub-station just outside the town wall. From there, I can follow the giant cable along the sand to the Heart.": "Il Cuore è a una certa distanza dalla città. Per trovarlo, dovrei dirigermi alla sottostazione appena fuori le mura. Da lì, posso seguire il cavo gigante lungo la sabbia fino al Cuore.",
    "It looks like an important part of the Heart has been ripped out here.": "Sembra che una parte importante del Cuore sia stata strappata via da qui.",
    "There's some feathers on the floor here.": "Ci sono delle piume sul pavimento qui.",
    "There's a trail of blood leading out the door here.": "Qui c'è una scia di sangue che porta fuori dalla porta.",
    "Whatever smashed this glass came from outside the window and landed in this room.": "Qualunque cosa abbia frantumato questo vetro è arrivata da fuori dalla finestra ed è atterrata in questa stanza.",
    "There's a single glove lying on the floor here.": "C'è un singolo guanto sul pavimento qui.",
    "I think I have enough information to report back to Zuli.": "Credo di avere abbastanza informazioni per riferire a Zuli.",
    "I report my findings to Zuli. She suspects the Heart has been sabotaged.": "Riferisco le mie scoperte a Zuli. Sospetta che il Cuore sia stato sabotato.",
    "She asks me to investigate around the town.": "Mi chiede di indagare in giro per la città.",
    "Heartbreak in the City": "Crepacuore in Città",
    "The Atomic Heart powering Eccria has failed. Zuli wants me to go and investigate the heart.": "Il Cuore Atomico che alimenta Eccria si è guastato. Zuli vuole che vada a indagare al cuore.",
    "Zuli gave me a keycard that will unlock the door to the Heart.": "Zuli mi ha dato una tessera che aprirà la porta del Cuore.",
    "Find the Atomic Heart. I can follow the giant power cable there from Eccria.": "Trovare il Cuore Atomico. Posso seguire il gigantesco cavo elettrico da Eccria fino a lì.",
    "I found the Atomic Heart.": "Ho trovato il Cuore Atomico.",
    "The Power Core is missing from the central chamber of the Heart.": "Il Nucleo di Potenza manca dalla camera centrale del Cuore.",
    "I found some feathers on the floor of the central chamber.": "Ho trovato delle piume sul pavimento della camera centrale.",
    "There's a trail of blood on the floor of the control room.": "C'è una scia di sangue sul pavimento della sala di controllo.",
    "The window of the control room has been smashed.": "La finestra della sala di controllo è stata frantumata.",
    "I found a glove on the floor outside the door to the control room.": "Ho trovato un guanto sul pavimento fuori dalla porta della sala di controllo.",
    "I reported my findings back to Zuli.": "Ho riferito le mie scoperte a Zuli.",
    "I can keep investigating the Heart, or I can report my findings back to Zuli.": "Posso continuare a indagare al Cuore, oppure riferire le mie scoperte a Zuli.",
    "I've seen enough clues - I should report back to Zuli.": "Ho visto abbastanza indizi — dovrei tornare a riferire a Zuli.",
}

def main():
    csv_in = 'translations/ink_strings.csv'
    rows = list(csv.DictReader(open(csv_in)))
    applied = 0
    for r in rows:
        if r['en'] in TRANSLATIONS and not r['it']:
            r['it'] = TRANSLATIONS[r['en']]
            applied += 1
    with open(csv_in, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['path', 'en', 'it'], quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    total_translated = sum(1 for r in rows if r['it'])
    print(f"Applied {applied} new translations from this batch")
    print(f"Total translated rows in CSV: {total_translated}/{len(rows)}")

if __name__ == '__main__':
    main()
