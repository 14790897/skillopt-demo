# -*- coding: utf-8 -*-
"""Build a HARDER SearchQA-format dataset designed to challenge deepseek-chat.

Difficulty tricks:
1. Context conflicts with common knowledge (must follow context)
2. Multiple candidate answers in context (must pick the right one)
3. Strict format requirements (number only, no units, short form)
4. Ambiguous entity names (Apple Inc vs Apple Records)
5. Dense context with distractor information
6. Questions requiring careful extraction vs general knowledge
"""
import json
import os

ITEMS = [
    # ====== TRAIN (30 items) ======

    # --- Context conflicts with general knowledge ---
    {"id": "hard_001",
     "question": "According to the passage, what year was the telephone invented?",
     "context": "[DOC] Revised History of Communications | Recent scholarship has established that Antonio Meucci filed his patent caveat for a voice communication device in 1871, five years before Alexander Graham Bell's patent in 1876. The Italian government officially credited Meucci as the inventor of the telephone in 2002.",
     "answers": ["1871"]},

    {"id": "hard_002",
     "question": "According to this article, what is the tallest building in the world?",
     "context": "[DOC] Architectural Records 2025 | The Jeddah Tower, completed in late 2024, stands at 1,008 meters, surpassing the Burj Khalifa (828m) to become the world's tallest building. The Shanghai Tower (632m) remains the tallest in China.",
     "answers": ["Jeddah Tower"]},

    {"id": "hard_003",
     "question": "What percentage of the Earth's surface is covered by water according to the text?",
     "context": "[DOC] Planetary Science Update | While commonly cited as 71%, recent satellite measurements using advanced LIDAR technology have revised the figure: approximately 70.8% of Earth's surface is covered by water, with 29.2% being land mass.",
     "answers": ["70.8%", "70.8"]},

    # --- Multiple candidates in context (must pick correct one) ---
    {"id": "hard_004",
     "question": "Who won the Nobel Prize in Physics mentioned in this passage?",
     "context": "[DOC] Nobel Prizes 2024 | The Nobel Prize in Chemistry was awarded to David Baker for computational protein design. The Nobel Prize in Physics was awarded to John Hopfield and Geoffrey Hinton for foundational discoveries in machine learning. The Nobel Peace Prize went to Nihon Hidankyo.",
     "answers": ["John Hopfield and Geoffrey Hinton", "Hopfield and Hinton"]},

    {"id": "hard_005",
     "question": "What is the population of the SECOND largest city mentioned?",
     "context": "[DOC] Urban Demographics | Tokyo leads with 37.4 million residents in its greater metropolitan area. Delhi follows with 32.9 million. Shanghai ranks third at 29.2 million, while Sao Paulo has 22.4 million.",
     "answers": ["32.9 million", "32.9"]},

    {"id": "hard_006",
     "question": "What was the GDP growth rate of India in the fiscal year mentioned?",
     "context": "[DOC] Asian Economies Q3 Report | China's GDP grew 5.2% in FY2024. India's economy expanded at 7.8% in FY2024, outpacing most major economies. Japan recorded modest growth of 1.9%, while South Korea achieved 2.6%.",
     "answers": ["7.8%", "7.8"]},

    # --- Strict format: number only, no extra text ---
    {"id": "hard_007",
     "question": "How many chromosomes do humans have?",
     "context": "[DOC] Human Genetics | Human somatic cells contain 46 chromosomes arranged in 23 pairs. Of these, 22 pairs are autosomes and one pair consists of sex chromosomes (XX in females, XY in males).",
     "answers": ["46"]},

    {"id": "hard_008",
     "question": "What is the atomic number of carbon?",
     "context": "[DOC] Periodic Table Reference | Carbon (C) has an atomic number of 6 and an atomic mass of 12.011. It has 4 valence electrons and can form up to 4 covalent bonds. Silicon (Si), below carbon in Group 14, has atomic number 14.",
     "answers": ["6"]},

    {"id": "hard_009",
     "question": "In what year did the event described in the passage occur?",
     "context": "[DOC] Space Exploration Milestones | The Voyager 1 spacecraft, launched on September 5, 1977, crossed the heliopause and entered interstellar space on August 25, 2012, becoming the first human-made object to do so. Voyager 2 followed in 2018.",
     "answers": ["2012"]},

    # --- Ambiguous entities ---
    {"id": "hard_010",
     "question": "Which Apple company is discussed in this passage?",
     "context": "[DOC] Music Industry History | Apple Records, founded in 1968 by The Beatles, was involved in a lengthy trademark dispute with Apple Computer (now Apple Inc.). The case was finally settled in 2007 when Apple Inc. acquired full ownership of all Apple-related trademarks.",
     "answers": ["Apple Records"]},

    {"id": "hard_011",
     "question": "Which Mercury is this passage about?",
     "context": "[DOC] Automotive History | The Mercury brand, produced by Ford Motor Company from 1938 to 2011, was positioned between Ford and Lincoln. The final Mercury vehicle, a Grand Marquis, rolled off the line on January 4, 2011.",
     "answers": ["Mercury brand", "Mercury"]},

    {"id": "hard_012",
     "question": "What does 'Python' refer to in this context?",
     "context": "[DOC] BBC Comedy Archives | Monty Python's Flying Circus first aired on BBC One on October 5, 1969. The troupe consisted of Graham Chapman, John Cleese, Terry Gilliam, Eric Idle, Terry Jones, and Michael Palin.",
     "answers": ["Monty Python's Flying Circus", "Monty Python"]},

    # --- Dense context requiring careful extraction ---
    {"id": "hard_013",
     "question": "What is the melting point of iron in Celsius?",
     "context": "[DOC] Metallurgy Reference | Iron (Fe) has a density of 7.874 g/cm3, a melting point of 1,538C, and a boiling point of 2,862C. Its Young's modulus is 211 GPa. Steel, an alloy of iron and carbon (0.2-2.1% C), melts between 1,370-1,510C depending on composition.",
     "answers": ["1,538", "1538"]},

    {"id": "hard_014",
     "question": "How long is the Nile River in kilometers?",
     "context": "[DOC] World Rivers | The Amazon River, at 6,400 km, is the largest by discharge volume. The Nile, traditionally considered the longest at 6,650 km, faces dispute from recent measurements suggesting the Amazon may be 6,992 km. The Yangtze is 6,300 km.",
     "answers": ["6,650", "6650"]},

    {"id": "hard_015",
     "question": "What speed did the vehicle achieve?",
     "context": "[DOC] Land Speed Records | On October 15, 1997, the ThrustSSC driven by Andy Green became the first car to officially break the sound barrier, achieving 1,228 km/h (763 mph) at the Black Rock Desert in Nevada. The previous record of 1,020 km/h was set by Richard Noble in 1983.",
     "answers": ["1,228 km/h", "1228"]},

    # --- Requires ignoring general knowledge, following context strictly ---
    {"id": "hard_016",
     "question": "Who invented the light bulb according to this passage?",
     "context": "[DOC] British Inventors | Joseph Swan demonstrated a working incandescent light bulb in Newcastle, England on January 18, 1879, ten months before Thomas Edison's American demonstration. Swan's home in Gateshead was the first in the world to be lit by electric light.",
     "answers": ["Joseph Swan"]},

    {"id": "hard_017",
     "question": "What is the correct spelling of the scientist's name as written in this text?",
     "context": "[DOC] Historical Notes | Nicola Tesla (as his name appears in Serbian records) was born in Smiljan, Austrian Empire (modern-day Croatia) in 1856. He later adopted the anglicized spelling 'Nikola Tesla' after emigrating to the United States.",
     "answers": ["Nicola Tesla"]},

    {"id": "hard_018",
     "question": "What was the company's revenue?",
     "context": "[DOC] Tech Earnings Q4 | Alphabet reported Q4 revenue of $86.3 billion, up 13% YoY. Net income was $20.7 billion. Google Cloud specifically generated $9.2 billion in revenue, a 26% increase. YouTube ad revenue reached $9.2 billion.",
     "answers": ["$86.3 billion", "86.3 billion"]},

    {"id": "hard_019",
     "question": "How many moons does Mars have?",
     "context": "[DOC] Solar System Bodies | Mars possesses two small, irregularly shaped moons: Phobos (mean radius 11.3 km) and Deimos (mean radius 6.2 km). Both are thought to be captured asteroids. Jupiter, by contrast, has 95 confirmed moons.",
     "answers": ["2", "two"]},

    {"id": "hard_020",
     "question": "What temperature does the passage give for absolute zero?",
     "context": "[DOC] Thermodynamics | Absolute zero, defined as 0 Kelvin, corresponds to -273.15 degrees Celsius or -459.67 degrees Fahrenheit. At this temperature, particles possess minimal vibrational motion. The closest achieved in laboratory is 38 picokelvin.",
     "answers": ["-273.15 degrees Celsius", "-273.15", "0 Kelvin"]},

    # --- Tricky format / boundary questions ---
    {"id": "hard_021",
     "question": "Name the founder mentioned in this passage.",
     "context": "[DOC] Social Media History | Facebook (now Meta Platforms) was co-founded by Mark Zuckerberg, Eduardo Saverin, Andrew McCollum, Dustin Moskovitz, and Chris Hughes in 2004. However, the platform was primarily coded by Zuckerberg from his Harvard dorm room.",
     "answers": ["Mark Zuckerberg"]},

    {"id": "hard_022",
     "question": "What fraction of the human body is water?",
     "context": "[DOC] Human Biology | The adult human body is approximately 60% water by mass. However, this varies significantly: the brain and heart are 73% water, lungs are 83%, skin is 64%, muscles are 79%, and bones are 31%.",
     "answers": ["60%", "approximately 60%"]},

    {"id": "hard_023",
     "question": "When was the treaty signed according to the passage?",
     "context": "[DOC] Diplomatic History | The Treaty of Versailles, which formally ended World War I, was signed on June 28, 1919 in the Hall of Mirrors at the Palace of Versailles. The armistice that ceased fighting had been signed earlier on November 11, 1918.",
     "answers": ["June 28, 1919"]},

    {"id": "hard_024",
     "question": "What is the half-life of Carbon-14?",
     "context": "[DOC] Radiometric Dating | Carbon-14 decays by beta emission with a half-life of 5,730 years (plus or minus 40 years). This makes it useful for dating organic materials up to about 50,000 years old. Potassium-40, with a half-life of 1.25 billion years, is used for older specimens.",
     "answers": ["5,730 years", "5730"]},

    {"id": "hard_025",
     "question": "What was the spacecraft's velocity when it reached Jupiter?",
     "context": "[DOC] NASA Missions | The Juno spacecraft arrived at Jupiter on July 4, 2016, after a 5-year journey. It entered orbit at a velocity of 209,000 km/h (130,000 mph), making it one of the fastest human-made objects at that point. Its orbital period is 53 days.",
     "answers": ["209,000 km/h", "209000"]},

    {"id": "hard_026",
     "question": "How deep is the trench according to current measurements?",
     "context": "[DOC] Ocean Geography | The Mariana Trench's deepest point, Challenger Deep, was measured at 10,994 meters (36,070 feet) by a 2010 survey, though earlier measurements gave 10,916 m and later ones suggest 10,935 m. The exact depth remains debated.",
     "answers": ["10,994 meters", "10994", "10,994"]},

    {"id": "hard_027",
     "question": "What element has the highest melting point?",
     "context": "[DOC] Extreme Materials | Tungsten holds the record for the highest melting point of any element at 3,422C (6,192F). Carbon, while often cited, sublimes at 3,642C under normal pressure rather than melting. Tantalum hafnium carbide (Ta4HfC5) has the highest melting point of any compound at 3,942C.",
     "answers": ["Tungsten"]},

    {"id": "hard_028",
     "question": "What was the final score?",
     "context": "[DOC] Sports Archives | In the 2022 FIFA World Cup Final, Argentina defeated France in a penalty shootout (4-2) after the match ended 3-3 following extra time. Mbappe scored a hat-trick while Messi scored twice in what many called the greatest World Cup final ever.",
     "answers": ["3-3", "4-2"]},

    {"id": "hard_029",
     "question": "How many elements are in the periodic table as stated?",
     "context": "[DOC] Chemistry Update 2024 | The periodic table currently contains 118 confirmed elements, with oganesson (Og, Z=118) being the latest addition confirmed in 2016. Research continues on elements 119 and 120, though none have been synthesized yet.",
     "answers": ["118"]},

    {"id": "hard_030",
     "question": "What was the distance covered?",
     "context": "[DOC] Marathon Records | Kelvin Kiptum set the world marathon record of 2:00:35 at the 2023 Chicago Marathon, covering the 42.195 km course. This broke Eliud Kipchoge's previous record of 2:01:09 from Berlin 2022.",
     "answers": ["42.195 km", "42.195"]},

    # ====== VAL (15 items) ======
    {"id": "hard_v01",
     "question": "According to this passage, who discovered penicillin?",
     "context": "[DOC] Medical Myths Revisited | While Alexander Fleming is credited with discovering penicillin in 1928, recent historical research reveals that Ernest Duchesne, a French physician, had documented the antibacterial properties of Penicillium mold in his 1897 thesis, three decades earlier.",
     "answers": ["Ernest Duchesne"]},

    {"id": "hard_v02",
     "question": "What is the orbital period mentioned for this planet?",
     "context": "[DOC] Exoplanet Catalog | Proxima Centauri b orbits its star every 11.2 days at a distance of 0.049 AU. Despite being in the habitable zone, its parent star's frequent flares may strip the atmosphere. Proxima d, discovered later, has an orbital period of 5.1 days.",
     "answers": ["11.2 days", "11.2"]},

    {"id": "hard_v03",
     "question": "What is the LOWER bound of the estimate?",
     "context": "[DOC] Biodiversity Assessment | Scientists estimate between 8.7 million and 12.3 million eukaryotic species exist on Earth, of which approximately 1.2 million have been cataloged. The ocean alone may contain 700,000 to 1 million undiscovered species.",
     "answers": ["8.7 million", "8.7"]},

    {"id": "hard_v04",
     "question": "What year was the ORIGINAL version released?",
     "context": "[DOC] Software History | The original Unix operating system was developed at Bell Labs in 1969 by Ken Thompson and Dennis Ritchie. Linux, inspired by Unix, was first released by Linus Torvalds in 1991. BSD, another Unix derivative, emerged in 1977.",
     "answers": ["1969"]},

    {"id": "hard_v05",
     "question": "What concentration is considered lethal according to the text?",
     "context": "[DOC] Toxicology Reference | Carbon monoxide becomes dangerous at concentrations above 100 ppm with prolonged exposure. At 400 ppm, headaches occur within 1-2 hours. Concentrations of 12,800 ppm (1.28%) are immediately lethal. Normal atmospheric CO is about 0.1 ppm.",
     "answers": ["12,800 ppm", "12800 ppm", "1.28%"]},

    {"id": "hard_v06",
     "question": "Which author wrote the SECOND book mentioned?",
     "context": "[DOC] Bestseller List Week 12 | This week's top three: (1) 'Tomorrow, and Tomorrow, and Tomorrow' by Gabrielle Zevin; (2) 'Demon Copperhead' by Barbara Kingsolver; (3) 'Lessons in Chemistry' by Bonnie Garmus.",
     "answers": ["Barbara Kingsolver"]},

    {"id": "hard_v07",
     "question": "What was the patient's blood pressure reading?",
     "context": "[DOC] Clinical Case Study | The 45-year-old male presented with BP 168/102 mmHg, heart rate 92 bpm, temperature 37.2C. Labs showed creatinine 1.4 mg/dL, potassium 5.2 mEq/L. Previous visit BP was 142/88. Diagnosis: Stage 2 hypertension.",
     "answers": ["168/102", "168/102 mmHg"]},

    {"id": "hard_v08",
     "question": "How much did the stock price change?",
     "context": "[DOC] Market Close Report | NVIDIA (NVDA) closed at $892.03, up $47.82 (+5.67%) on strong AI chip demand. AMD rose 3.2% to $178.45. Intel fell 2.1% to $43.67. The S&P 500 gained 0.8% overall.",
     "answers": ["$47.82", "+$47.82", "47.82"]},

    {"id": "hard_v09",
     "question": "What was the error margin reported?",
     "context": "[DOC] Measurement Standards | The international prototype kilogram showed drift of 50 micrograms over 100 years, prompting the 2019 redefinition using the Planck constant (h = 6.62607015 x 10^-34 J*s, exact by definition). The old artifact had uncertainty of plus or minus 10 micrograms.",
     "answers": ["50 micrograms", "plus or minus 10 micrograms"]},

    {"id": "hard_v10",
     "question": "What is the survival rate mentioned?",
     "context": "[DOC] Oncology Statistics 2024 | The 5-year survival rate for stage I breast cancer is 99%. Stage II drops to 86%, Stage III to 57%, and Stage IV to 22%. Early detection through mammography has improved overall survival by 40% since 1990.",
     "answers": ["99%"]},

    {"id": "hard_v11",
     "question": "How many languages does the platform support according to the passage?",
     "context": "[DOC] Tech Product Review | The translation platform supports 133 languages in text mode and 46 languages for real-time speech translation. Premium users get access to 12 additional dialects. Document translation handles 89 file formats.",
     "answers": ["133"]},

    {"id": "hard_v12",
     "question": "What altitude did the aircraft reach?",
     "context": "[DOC] Aviation Records | The SR-71 Blackbird holds the altitude record for air-breathing aircraft at 25,929 meters (85,069 feet), set in 1976. The X-15 rocket plane reached 107,960 meters but uses rocket propulsion. The Concorde cruised at 18,300 meters.",
     "answers": ["25,929 meters", "25929"]},

    {"id": "hard_v13",
     "question": "What was the unemployment rate in the country discussed?",
     "context": "[DOC] Economic Indicators March 2025 | Germany's unemployment rate rose to 6.1% in March, up from 5.8% in February. Youth unemployment (under 25) reached 5.9%. France reported 7.3% overall, while Spain remained elevated at 11.7%.",
     "answers": ["6.1%", "6.1"]},

    {"id": "hard_v14",
     "question": "What compound has the highest boiling point in this list?",
     "context": "[DOC] Chemical Properties | Water boils at 100C, ethanol at 78.4C, glycerol at 290C, and mercury at 357C. Tungsten hexafluoride boils at 17.1C while sulfuric acid boils at 337C. Among these, mercury has the highest boiling point.",
     "answers": ["mercury", "Mercury"]},

    {"id": "hard_v15",
     "question": "How many people were affected according to the report?",
     "context": "[DOC] Disaster Report | The 2023 Turkey-Syria earthquake affected approximately 26 million people across both countries. In Turkey alone, 13.5 million were impacted. The death toll exceeded 59,000 with 120,000 injuries reported.",
     "answers": ["26 million"]},

    # ====== TEST (20 items) ======
    {"id": "hard_t01",
     "question": "What was the experiment's margin of error?",
     "context": "[DOC] Physics Lab Report | The measured speed of light was 299,792,456 m/s with a margin of error of plus or minus 2 m/s, consistent with the defined value of 299,792,458 m/s. The experiment used a rotating mirror apparatus with 10,000 measurements.",
     "answers": ["plus or minus 2 m/s", "2 m/s"]},

    {"id": "hard_t02",
     "question": "According to this text, what caused the extinction?",
     "context": "[DOC] Paleontology Debate | While the Chicxulub asteroid impact (66 million years ago) is widely accepted as the primary cause of dinosaur extinction, this passage discusses the Deccan Traps hypothesis: massive volcanic eruptions in India lasting 30,000 years may have been equally or more responsible, releasing enough sulfur dioxide to cause global cooling of 2C.",
     "answers": ["Deccan Traps", "massive volcanic eruptions in India", "volcanic eruptions"]},

    {"id": "hard_t03",
     "question": "What is the current record time?",
     "context": "[DOC] Track and Field Records | The men's 100m world record stands at 9.58 seconds, set by Usain Bolt in 2009. The women's record is 10.49 seconds by Florence Griffith-Joyner (1988). The indoor 60m records are 6.34s (men) and 6.92s (women).",
     "answers": ["9.58 seconds", "9.58"]},

    {"id": "hard_t04",
     "question": "What is the efficiency percentage of the newer technology?",
     "context": "[DOC] Solar Technology | Traditional silicon solar panels achieve 20-22% efficiency. Perovskite solar cells in laboratory settings have reached 33.7% efficiency as of 2023, though commercial versions currently achieve only 28%. Organic solar cells lag behind at 18.2%.",
     "answers": ["33.7%", "33.7"]},

    {"id": "hard_t05",
     "question": "How many bones does a newborn have?",
     "context": "[DOC] Developmental Biology | A newborn infant has approximately 270 bones, many of which fuse together during development. By adulthood, this number reduces to 206. The process of ossification continues until about age 25.",
     "answers": ["270", "approximately 270"]},

    {"id": "hard_t06",
     "question": "What was the spacecraft's mass at launch?",
     "context": "[DOC] Space Mission Profile | The James Webb Space Telescope had a launch mass of 6,500 kg, including the sunshield (weighing approximately 300 kg). Its primary mirror spans 6.5 meters and consists of 18 hexagonal beryllium segments. Total mission cost: $10 billion.",
     "answers": ["6,500 kg", "6500"]},

    {"id": "hard_t07",
     "question": "What frequency range does the device operate in?",
     "context": "[DOC] 5G Specifications | 5G NR operates in two frequency ranges: FR1 (sub-6 GHz, from 410 MHz to 7.125 GHz) for broad coverage, and FR2 (mmWave, 24.25-52.6 GHz) for high bandwidth. Most current deployments use FR1. FR2 range is limited to about 500 meters.",
     "answers": ["410 MHz to 7.125 GHz", "FR1"]},

    {"id": "hard_t08",
     "question": "What is the minimum age requirement stated?",
     "context": "[DOC] Regulatory Framework | Under the Digital Services Act (2024), platforms must verify users are at least 16 years old for data processing consent in the EU (13 in the US under COPPA). Platforms with over 45 million monthly users face additional transparency obligations.",
     "answers": ["16", "16 years old"]},

    {"id": "hard_t09",
     "question": "What dosage was effective in the trial?",
     "context": "[DOC] Clinical Trial Results | The Phase III trial tested doses of 5mg, 10mg, and 20mg administered daily. The 10mg dose showed statistically significant improvement (p<0.001) with 68% of patients achieving remission, compared to 42% for 5mg and 71% for 20mg (but with increased side effects).",
     "answers": ["10mg", "10 mg"]},

    {"id": "hard_t10",
     "question": "What percentage of energy came from renewables?",
     "context": "[DOC] Energy Report 2024 | Global electricity generation from renewables reached 30.3% in 2024. Solar alone contributed 5.5%, wind 7.8%, hydroelectric 15.1%, and other sources 1.9%. Fossil fuels still accounted for 61.4% with nuclear providing 8.3%.",
     "answers": ["30.3%", "30.3"]},

    {"id": "hard_t11",
     "question": "How far is the nearest star system?",
     "context": "[DOC] Stellar Distances | Alpha Centauri, a triple star system, is the nearest to our Sun at 4.37 light-years. Its closest component, Proxima Centauri, is slightly nearer at 4.24 light-years. Barnard's Star is the next closest single star at 5.96 light-years.",
     "answers": ["4.37 light-years", "4.37"]},

    {"id": "hard_t12",
     "question": "What voltage is used in this country's power grid?",
     "context": "[DOC] International Standards | Japan uses a dual-voltage system: 100V at 50Hz in eastern Japan (Tokyo) and 100V at 60Hz in western Japan (Osaka). Most countries use 220-240V. The US standard is 120V/60Hz. Japan's low voltage is unique globally.",
     "answers": ["100V", "100"]},

    {"id": "hard_t13",
     "question": "What was the INITIAL estimate before revision?",
     "context": "[DOC] Census Bureau Correction | The 2020 US Census initially counted the population at 331.4 million. A post-enumeration survey revealed an overcount of 0.24%, and the revised figure was adjusted to 330.6 million. Several states were significantly overcounted or undercounted.",
     "answers": ["331.4 million", "331.4"]},

    {"id": "hard_t14",
     "question": "What is the compression ratio?",
     "context": "[DOC] Engine Specifications | The 2024 turbocharged 2.0L four-cylinder produces 300 hp at 5,500 rpm and 400 Nm of torque at 2,000-4,500 rpm. Compression ratio is 10.5:1. Bore and stroke are 83mm x 92.4mm. Fuel consumption is rated at 8.2 L/100km.",
     "answers": ["10.5:1", "10.5"]},

    {"id": "hard_t15",
     "question": "How many participants completed the study?",
     "context": "[DOC] Research Methodology | The study enrolled 2,847 participants. Of these, 312 withdrew before completion, 89 were excluded due to protocol violations, and 41 were lost to follow-up. The final analysis included 2,405 participants (84.5% completion rate).",
     "answers": ["2,405", "2405"]},

    {"id": "hard_t16",
     "question": "What was the PREVIOUS record before the one described?",
     "context": "[DOC] Computing Records | The Frontier supercomputer achieved 1.194 exaflops on the LINPACK benchmark in 2022, becoming the first true exascale machine. It displaced Japan's Fugaku (442 petaflops, 2020) which had itself surpassed IBM's Summit (148.6 petaflops, 2018).",
     "answers": ["442 petaflops", "Fugaku"]},

    {"id": "hard_t17",
     "question": "What is the purity level required?",
     "context": "[DOC] Semiconductor Manufacturing | EUV lithography requires an ultra-high vacuum of 10^-7 Pa. The tin plasma source operates at 50,000C. The multilayer mirrors must have surface roughness below 0.05 nm. Silicon wafers must be 99.9999999% pure (nine nines).",
     "answers": ["99.9999999%", "nine nines"]},

    {"id": "hard_t18",
     "question": "What was the depth of the well?",
     "context": "[DOC] Drilling Records | The Kola Superdeep Borehole reached 12,262 meters (40,230 feet) before being abandoned in 1992 due to unexpectedly high temperatures of 180C at the bottom. The original target was 15,000 meters. Qatar's Al Shaheen oil well reaches 12,289 meters but is not vertical.",
     "answers": ["12,262 meters", "12262"]},

    {"id": "hard_t19",
     "question": "What was the detection sensitivity?",
     "context": "[DOC] LIGO Technical Report | The gravitational wave detectors can measure length changes of 10^-19 meters, roughly 1/10,000th the width of a proton. Each arm is 4 km long. The first detection (GW150914) measured a strain of 10^-21.",
     "answers": ["10^-19 meters"]},

    {"id": "hard_t20",
     "question": "What percentage of the vote did the winner receive?",
     "context": "[DOC] Election Results Summary | In the final count, Candidate A received 48.3% of the popular vote (74.2 million votes), while Candidate B received 46.9% (72.1 million). However, Candidate B won the electoral college 312-226, becoming president-elect.",
     "answers": ["46.9%", "46.9"]},
]


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, "data", "searchqa_demo_split")

    train_items = ITEMS[:30]
    val_items = ITEMS[30:45]
    test_items = ITEMS[45:]

    for split_name, items in [("train", train_items), ("val", val_items), ("test", test_items)]:
        split_dir = os.path.join(out_dir, split_name)
        os.makedirs(split_dir, exist_ok=True)
        path = os.path.join(split_dir, "items.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        print(f"  {split_name}: {len(items)} items -> {path}")

    manifest = {"train": len(train_items), "val": len(val_items), "test": len(test_items)}
    with open(os.path.join(out_dir, "split_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nDone! Hard dataset ready at: {out_dir}")
    print("  Difficulty features: context-conflict, multi-candidate,")
    print("  strict-format, ambiguous-entities, dense-extraction")


if __name__ == "__main__":
    main()
