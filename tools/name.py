"""
An example program to show
"""


import re
import sys
from typing import Tuple
from pathlib import Path
from collections import defaultdict

import matplotlib.pyplot as plt

DATA_ROOT = Path(__file__).parent / ".."

sys.path.append(str(DATA_ROOT / "tools"))

from common import iter_exhibitor



COUNT = 20



def slug_form_iter(s: str) -> Tuple[str, str]:
    """
    Homogenise a line of text, remove comments and split on whitespace.
    Yield pairs of slug and original text.
    """
    s = re.sub(r"#.*$", "", s)
    s = re.sub(r"[^\w]", " ", s)
    s = re.sub(r"[\s]+", " ", s)
    s = s.strip()
    for form in s.split():
        slug = re.sub(r"'", "", form)
        slug = slug.lower()
        yield slug, form



# Brand names from SIPRI Top 100 2020
# https://sipri.org/publications/2021/sipri-fact-sheets/sipri-top-100-arms-producing-and-military-services-companies-2020
sipri_set = set("""lockheed martin raytheon boeing northrop grumman dynamics bae norinco avic cetc l3 harris l3harris airbus casic leonardo thales huntington ingalls leidos almaz antey honeywell booz allen hamilton csgc rolls royce edge safran mitsubishi rheinmetall elbit caci mbda dassault shipbuilding textron saab babcock perspecta amentum kbr atomics rafael fincantieri cea oshkosh hanwha aselsan transdigm kawasaki bechtel thyssenkrupp jacobs mantech kret sierra nevada indian serco fluor bwx bharat dyncorp pgz melrose krauss maffei wegmann parsons lig nex1 vectrus aerojet rocketdyne fujitsu ukroboronprom hensoldt curtiss wright qinetiq moog nexter navantia hanwha uralvagonzavod architects ball teledyne ihi amphenol launch howmet meggitt viasat mitsubishi cae mercury kongsberg""".split())
sipri_pairs = {tuple(v.split()) for v in ("""
general dynamics
united aircraft
general electric
naval group
united shipbuilding
israel aerospace
science applications
tactical missiles
hindustan aeronautics
united engine
indian ordnance
st engineering
korea aerospace
russian electronics
russian helicopters
pacific architects
united launch
aerospace corp
""".split("\n")) if v}


stop_set = {pair[0] for line in """
ag  # Aktiengesellschaft
bv  # Besloten Vennootschap (Dutch)
co
company
corp
corporation
gmbh  # Gesellschaft mit beschränkter Haftung
inc
incorporated
jsc  # Joint Stock Company
limited
llc
ltd
ltda  # Limitada
plc
pte  # Private
pty  # Proprietary Limited company
pvt  # Private
sa  # Sociedad Anónima
sarl  # Société Anonyme à Responsabilité Limitée
sp
srl  # Sociedad de Responsabilidad Limitada
sas  # Société par actions simplifiée
oy  # Osakeyhtiö (Finnish)
SDN BHD  # Sendirian Berhad (Malay)
San. Ve Ti̇c. Şti  # Sanayi ve Ticaret Limited Şirketi (Turkish)
ŞTİ
TİC
tic
Sił Zbrojnych  # Polish
sil
spol.  # Spolecnost s rucenim omezenym (Czech)

of
und  # German
do  # Portuguese
""".split("\n") for pair in slug_form_iter(line)}



freq_1gram = defaultdict(lambda: {
    "total": 0,
    "forms": defaultdict(int),
})
freq_2gram = defaultdict(lambda: {
    "total": 0,
    "forms": defaultdict(int),
})
for fair, exhibitor in iter_exhibitor(DATA_ROOT / "data"):
    name_s = list(slug_form_iter(exhibitor.name))
    for i, (s1, f1) in enumerate(name_s):
        if len(s1) == 1 or s1 in stop_set:
            continue
        if s1 in sipri_set:
            freq_1gram[s1]["total"] += 1
            freq_1gram[s1]["forms"][f1] += 1
        if i:
            (s0, f0) = name_s[i - 1]
            if len(s0) == 1 or s0 in stop_set:
                continue
            if s0 in sipri_set or s1 in sipri_set or (s0, s1) in sipri_pairs:
                freq_2gram[(s0, s1)]["total"] += 1
                freq_2gram[(s0, s1)]["forms"][" ".join([f0, f1])] += 1


freq_2gram = sorted([[v["total"], k, v] for k, v in freq_2gram.items()], reverse=True)
for freq, slug_s, d in freq_2gram[:COUNT]:
    # If the digram frequency is at least half the unigram frequency of either word,
    # remove that word from the unigram frequency list.
    for slug in slug_s:
        if freq >= freq_1gram[slug]["total"] / 2:
            del freq_1gram[slug]

freq_gram = sorted(freq_2gram + [[v["total"], (k, ), v] for k, v in freq_1gram.items()], reverse=True)

x, y = zip(*[
    (sorted([[v, k] for k, v in d["forms"].items()], reverse=True)[0][1], freq)
    for freq, slug_s, d in freq_gram[:COUNT]
])
plt.barh(x, y)
plt.xlabel('Frequency')
plt.title('Frequency in Exhibitor Names')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
