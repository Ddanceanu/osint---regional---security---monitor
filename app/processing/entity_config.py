CORE_COUNTRIES = {
    # Primary focus
    "Romania", "Republic of Moldova", "Ukraine", "Russia",
    # NATO key members
    "United States", "United Kingdom", "France", "Germany", "Turkey",
    "Canada", "Poland", "Italy", "Spain", "Netherlands", "Norway", "Belgium",
    # Eastern flank / regional
    "Bulgaria", "Hungary", "Czech Republic", "Slovakia",
    "Estonia", "Latvia", "Lithuania",
    "Greece", "Croatia", "Slovenia",
    "Albania", "North Macedonia", "Montenegro",
    "Finland", "Sweden", "Denmark",
    # Geopolitically relevant
    "Belarus", "Georgia", "Serbia",
    "China", "Iran", "Israel", "India",
    "Japan", "South Korea", "North Korea",
    "Azerbaijan", "Armenia", "Kazakhstan",
}

COUNTRY_KEYWORDS = {
    "Afghanistan": [
        "afghanistan",
        "afghan",
    ],
    "Albania": [
        "albania",
        "albanian",
    ],
    "Algeria": [
        "algeria",
        "algerian",
    ],
    "Andorra": [
        "andorra",
        "andorran",
    ],
    "Angola": [
        "angola",
        "angolan",
    ],
    "Antigua and Barbuda": [
        "antigua and barbuda",
        "antiguan",
    ],
    "Argentina": [
        "argentina",
        "argentinian",
        "argentine",
    ],
    "Armenia": [
        "armenia",
        "armenian",
    ],
    "Australia": [
        "australia",
        "australian",
    ],
    "Austria": [
        "austria",
        "austrian",
    ],
    "Azerbaijan": [
        "azerbaijan",
        "azerbaijani",
    ],
    "Bahamas": [
        "bahamas",
        "bahamian",
    ],
    "Bahrain": [
        "bahrain",
        "bahraini",
    ],
    "Bangladesh": [
        "bangladesh",
        "bangladeshi",
    ],
    "Barbados": [
        "barbados",
        "barbadian",
    ],
    "Belarus": [
        "belarus",
        "belarusian",
    ],
    "Belgium": [
        "belgium",
        "belgian",
    ],
    "Belize": [
        "belize",
        "belizean",
    ],
    "Benin": [
        "benin",
        "beninese",
    ],
    "Bhutan": [
        "bhutan",
        "bhutanese",
    ],
    "Bolivia": [
        "bolivia",
        "bolivian",
    ],
    "Bosnia and Herzegovina": [
        "bosnia and herzegovina",
        "bosnia",
        "bosnian",
    ],
    "Botswana": [
        "botswana",
        "botswanan",
    ],
    "Brazil": [
        "brazil",
        "brazilian",
    ],
    "Brunei": [
        "brunei",
        "bruneian",
    ],
    "Bulgaria": [
        "bulgaria",
        "bulgarian",
    ],
    "Burkina Faso": [
        "burkina faso",
        "burkinabe",
    ],
    "Burundi": [
        "burundi",
        "burundian",
    ],
    "Cabo Verde": [
        "cabo verde",
        "cape verde",
        "cape verdean",
    ],
    "Cambodia": [
        "cambodia",
        "cambodian",
    ],
    "Cameroon": [
        "cameroon",
        "cameroonian",
    ],
    "Canada": [
        "canada",
        "canadian",
    ],
    "Central African Republic": [
        "central african republic",
        "central african",
    ],
    "Chad": [
        "chad",
        "chadian",
    ],
    "Chile": [
        "chile",
        "chilean",
    ],
    "China": [
        "china",
        "chinese",
        "people's republic of china",
    ],
    "Colombia": [
        "colombia",
        "colombian",
    ],
    "Comoros": [
        "comoros",
        "comorian",
    ],
    "Congo": [
        "republic of the congo",
        "congo-brazzaville",
    ],
    "Democratic Republic of the Congo": [
        "democratic republic of the congo",
        "dr congo",
        "drc",
    ],
    "Costa Rica": [
        "costa rica",
        "costa rican",
    ],
    "Croatia": [
        "croatia",
        "croatian",
    ],
    "Cuba": [
        "cuba",
        "cuban",
    ],
    "Cyprus": [
        "cyprus",
        "cypriot",
    ],
    "Czech Republic": [
        "czech republic",
        "czechia",
        "czech",
    ],
    "Denmark": [
        "denmark",
        "danish",
    ],
    "Djibouti": [
        "djibouti",
        "djiboutian",
    ],
    "Dominica": [
        "dominica",
        "dominican",
    ],
    "Dominican Republic": [
        "dominican republic",
    ],
    "Ecuador": [
        "ecuador",
        "ecuadorian",
    ],
    "Egypt": [
        "egypt",
        "egyptian",
    ],
    "El Salvador": [
        "el salvador",
        "salvadoran",
    ],
    "Equatorial Guinea": [
        "equatorial guinea",
        "equatoguinean",
    ],
    "Eritrea": [
        "eritrea",
        "eritrean",
    ],
    "Estonia": [
        "estonia",
        "estonian",
    ],
    "Eswatini": [
        "eswatini",
        "swazi",
    ],
    "Ethiopia": [
        "ethiopia",
        "ethiopian",
    ],
    "Fiji": [
        "fiji",
        "fijian",
    ],
    "Finland": [
        "finland",
        "finnish",
    ],
    "France": [
        "france",
        "french",
    ],
    "Gabon": [
        "gabon",
        "gabonese",
    ],
    "Gambia": [
        "gambia",
        "gambian",
    ],
    "Georgia": [
        "georgia",
        "georgian",
    ],
    "Germany": [
        "germany",
        "german",
    ],
    "Ghana": [
        "ghana",
        "ghanaian",
    ],
    "Greece": [
        "greece",
        "greek",
    ],
    "Grenada": [
        "grenada",
        "grenadian",
    ],
    "Guatemala": [
        "guatemala",
        "guatemalan",
    ],
    "Guinea": [
        "guinea",
        "guinean",
    ],
    "Guinea-Bissau": [
        "guinea-bissau",
        "bissau-guinean",
    ],
    "Guyana": [
        "guyana",
        "guyanese",
    ],
    "Haiti": [
        "haiti",
        "haitian",
    ],
    "Honduras": [
        "honduras",
        "honduran",
    ],
    "Hungary": [
        "hungary",
        "hungarian",
    ],
    "Iceland": [
        "iceland",
        "icelandic",
        "icelander",
    ],
    "India": [
        "india",
        "indian",
    ],
    "Indonesia": [
        "indonesia",
        "indonesian",
    ],
    "Iran": [
        "iran",
        "iranian",
    ],
    "Iraq": [
        "iraq",
        "iraqi",
    ],
    "Ireland": [
        "ireland",
        "irish",
    ],
    "Israel": [
        "israel",
        "israeli",
    ],
    "Italy": [
        "italy",
        "italian",
    ],
    "Ivory Coast": [
        "ivory coast",
        "côte d'ivoire",
        "cote d'ivoire",
        "ivorian",
    ],
    "Jamaica": [
        "jamaica",
        "jamaican",
    ],
    "Japan": [
        "japan",
        "japanese",
    ],
    "Jordan": [
        "jordan",
        "jordanian",
    ],
    "Kazakhstan": [
        "kazakhstan",
        "kazakhstani",
        "kazakh",
    ],
    "Kenya": [
        "kenya",
        "kenyan",
    ],
    "Kiribati": [
        "kiribati",
        "i-kiribati",
    ],
    "Kosovo": [
        "kosovo",
        "kosovar",
    ],
    "Kuwait": [
        "kuwait",
        "kuwaiti",
    ],
    "Kyrgyzstan": [
        "kyrgyzstan",
        "kyrgyz",
    ],
    "Laos": [
        "laos",
        "lao",
        "laotian",
    ],
    "Latvia": [
        "latvia",
        "latvian",
    ],
    "Lebanon": [
        "lebanon",
        "lebanese",
    ],
    "Lesotho": [
        "lesotho",
        "basotho",
    ],
    "Liberia": [
        "liberia",
        "liberian",
    ],
    "Libya": [
        "libya",
        "libyan",
    ],
    "Liechtenstein": [
        "liechtenstein",
        "liechtensteiner",
    ],
    "Lithuania": [
        "lithuania",
        "lithuanian",
    ],
    "Luxembourg": [
        "luxembourg",
        "luxembourgish",
        "luxembourger",
    ],
    "Madagascar": [
        "madagascar",
        "malagasy",
    ],
    "Malawi": [
        "malawi",
        "malawian",
    ],
    "Malaysia": [
        "malaysia",
        "malaysian",
    ],
    "Maldives": [
        "maldives",
        "maldivian",
    ],
    "Mali": [
        "mali",
        "malian",
    ],
    "Malta": [
        "malta",
        "maltese",
    ],
    "Marshall Islands": [
        "marshall islands",
        "marshallese",
    ],
    "Mauritania": [
        "mauritania",
        "mauritanian",
    ],
    "Mauritius": [
        "mauritius",
        "mauritian",
    ],
    "Mexico": [
        "mexico",
        "mexican",
    ],
    "Micronesia": [
        "micronesia",
        "micronesian",
    ],
    "Moldova": [
        "republic of moldova",
        "moldova",
        "moldovan",
    ],
    "Monaco": [
        "monaco",
        "monegasque",
    ],
    "Mongolia": [
        "mongolia",
        "mongolian",
    ],
    "Montenegro": [
        "montenegro",
        "montenegrin",
    ],
    "Morocco": [
        "morocco",
        "moroccan",
    ],
    "Mozambique": [
        "mozambique",
        "mozambican",
    ],
    "Myanmar": [
        "myanmar",
        "burma",
        "burmese",
    ],
    "Namibia": [
        "namibia",
        "namibian",
    ],
    "Nauru": [
        "nauru",
        "nauruan",
    ],
    "Nepal": [
        "nepal",
        "nepali",
    ],
    "Netherlands": [
        "netherlands",
        "dutch",
    ],
    "New Zealand": [
        "new zealand",
        "new zealander",
    ],
    "Nicaragua": [
        "nicaragua",
        "nicaraguan",
    ],
    "Niger": [
        "niger",
        "nigerien",
    ],
    "Nigeria": [
        "nigeria",
        "nigerian",
    ],
    "North Korea": [
        "north korea",
        "dprk",
        "north korean",
    ],
    "North Macedonia": [
        "north macedonia",
        "republic of north macedonia",
        "macedonian",
    ],
    "Norway": [
        "norway",
        "norwegian",
    ],
    "Oman": [
        "oman",
        "omani",
    ],
    "Pakistan": [
        "pakistan",
        "pakistani",
    ],
    "Palau": [
        "palau",
        "palauan",
    ],
    "Palestine": [
        "palestine",
        "palestinian",
    ],
    "Panama": [
        "panama",
        "panamanian",
    ],
    "Papua New Guinea": [
        "papua new guinea",
        "papua new guinean",
    ],
    "Paraguay": [
        "paraguay",
        "paraguayan",
    ],
    "Peru": [
        "peru",
        "peruvian",
    ],
    "Philippines": [
        "philippines",
        "filipino",
        "philippine",
    ],
    "Poland": [
        "poland",
        "polish",
    ],
    "Portugal": [
        "portugal",
        "portuguese",
    ],
    "Qatar": [
        "qatar",
        "qatari",
    ],
    "Romania": [
        "romania",
        "romanian",
    ],
    "Russia": [
        "russia",
        "russian federation",
        "russian",
    ],
    "Rwanda": [
        "rwanda",
        "rwandan",
    ],
    "Saint Kitts and Nevis": [
        "saint kitts and nevis",
        "kittitian",
    ],
    "Saint Lucia": [
        "saint lucia",
        "saint lucian",
    ],
    "Saint Vincent and the Grenadines": [
        "saint vincent and the grenadines",
        "vincentian",
    ],
    "Samoa": [
        "samoa",
        "samoan",
    ],
    "San Marino": [
        "san marino",
        "sammarinese",
    ],
    "São Tomé and Príncipe": [
        "são tomé and príncipe",
        "sao tome and principe",
    ],
    "Saudi Arabia": [
        "saudi arabia",
        "saudi",
    ],
    "Senegal": [
        "senegal",
        "senegalese",
    ],
    "Serbia": [
        "serbia",
        "serbian",
    ],
    "Seychelles": [
        "seychelles",
        "seychellois",
    ],
    "Sierra Leone": [
        "sierra leone",
        "sierra leonean",
    ],
    "Singapore": [
        "singapore",
        "singaporean",
    ],
    "Slovakia": [
        "slovakia",
        "slovak",
    ],
    "Slovenia": [
        "slovenia",
        "slovenian",
    ],
    "Solomon Islands": [
        "solomon islands",
        "solomon islander",
    ],
    "Somalia": [
        "somalia",
        "somali",
    ],
    "South Africa": [
        "south africa",
        "south african",
    ],
    "South Korea": [
        "south korea",
        "republic of korea",
        "south korean",
    ],
    "South Sudan": [
        "south sudan",
        "south sudanese",
    ],
    "Spain": [
        "spain",
        "spanish",
    ],
    "Sri Lanka": [
        "sri lanka",
        "sri lankan",
    ],
    "Sudan": [
        "sudan",
        "sudanese",
    ],
    "Suriname": [
        "suriname",
        "surinamese",
    ],
    "Sweden": [
        "sweden",
        "swedish",
    ],
    "Switzerland": [
        "switzerland",
        "swiss",
    ],
    "Syria": [
        "syria",
        "syrian",
    ],
    "Taiwan": [
        "taiwan",
        "taiwanese",
    ],
    "Tajikistan": [
        "tajikistan",
        "tajik",
    ],
    "Tanzania": [
        "tanzania",
        "tanzanian",
    ],
    "Thailand": [
        "thailand",
        "thai",
    ],
    "Timor-Leste": [
        "timor-leste",
        "east timor",
        "timorese",
    ],
    "Togo": [
        "togo",
        "togolese",
    ],
    "Tonga": [
        "tonga",
        "tongan",
    ],
    "Trinidad and Tobago": [
        "trinidad and tobago",
        "trinidadian",
    ],
    "Tunisia": [
        "tunisia",
        "tunisian",
    ],
    "Turkey": [
        "turkey",
        "turkish",
    ],
    "Turkmenistan": [
        "turkmenistan",
        "turkmen",
    ],
    "Tuvalu": [
        "tuvalu",
        "tuvaluan",
    ],
    "Uganda": [
        "uganda",
        "ugandan",
    ],
    "Ukraine": [
        "ukraine",
        "ukrainian",
    ],
    "United Arab Emirates": [
        "united arab emirates",
        "uae",
        "emirati",
    ],
    "United Kingdom": [
        "united kingdom",
        "uk",
        "britain",
        "british",
    ],
    "United States": [
        "united states",
        "u.s.",
        "american",
    ],
    "Uruguay": [
        "uruguay",
        "uruguayan",
    ],
    "Uzbekistan": [
        "uzbekistan",
        "uzbek",
    ],
    "Vanuatu": [
        "vanuatu",
        "ni-vanuatu",
    ],
    "Vatican City": [
        "vatican",
        "holy see",
    ],
    "Venezuela": [
        "venezuela",
        "venezuelan",
    ],
    "Vietnam": [
        "vietnam",
        "vietnamese",
    ],
    "Yemen": [
        "yemen",
        "yemeni",
    ],
    "Zambia": [
        "zambia",
        "zambian",
    ],
    "Zimbabwe": [
        "zimbabwe",
        "zimbabwean",
    ],
}

ORGANIZATION_KEYWORDS = {
    # NATO / allied structures
    "NATO": [
        "nato",
        "north atlantic treaty organization",
    ],
    "North Atlantic Council": [
        "north atlantic council",
        "nac",
    ],
    "NATO Parliamentary Assembly": [
        "nato parliamentary assembly",
    ],
    "SHAPE": [
        "supreme headquarters allied powers europe",
        "s.h.a.p.e.",
    ],
    "Allied Command Operations": [
        "allied command operations",
    ],
    "Multinational Division South-East": [
        "multinational division south-east",
        "multinational division southeast",
        "mnd-se",
        "mnd se",
    ],
    "Multinational Corps South-East": [
        "multinational corps south-east",
        "multinational corps southeast",
        "headquarters multinational corps southeast",
        "mnc-se",
        "mnc se",
    ],
    "NATO Battle Group Romania": [
        "nato battlegroup romania",
        "nato battle group romania",
        "multinational battlegroup romania",
        "multinational battle group romania",
        "battlegroup romania",
        "battle group romania",
    ],

    # European Union core institutions
    "European Union": [
        "european union",
        # "eu",  # activeaza doar daca lucrezi exclusiv pe texte in engleza
    ],
    "European Commission": [
        "european commission",
        "commission of the european union",
    ],
    "European Council": [
        "european council",
    ],
    "Council of the European Union": [
        "council of the european union",
        "eu council",
        "council of the eu",
        "council of ministers of the european union",
    ],
    "European Parliament": [
        "european parliament",
        "ep",
    ],
    "EEAS": [
        "eeas",
        "european external action service",
    ],
    "European Defence Agency": [
        "european defence agency",
        "european defense agency",
        "eda",
    ],
    "European Court of Justice": [
        "court of justice of the european union",
        "cjeu",
        "european court of justice",
    ],
    "Frontex": [
        "frontex",
        "european border and coast guard agency",
    ],
    "Europol": [
        "europol",
        "european union agency for law enforcement cooperation",
    ],

    # United Nations / multilateral
    "United Nations": [
        "united nations",
        # "un",  # nu recomand: produce false positive masive
    ],
    "UN Security Council": [
        "un security council",
        "united nations security council",
        "security council",
    ],
    "UN General Assembly": [
        "un general assembly",
        "united nations general assembly",
        "unga",
    ],
    "UNHCR": [
        "unhcr",
        "united nations high commissioner for refugees",
        "un refugee agency",
    ],
    "IAEA": [
        "iaea",
        "international atomic energy agency",
    ],
    "International Criminal Court": [
        "international criminal court",
        "icc",
    ],
    "International Court of Justice": [
        "international court of justice",
        "icj",
        "world court",
    ],

    # OSCE / Council of Europe / related
    "OSCE": [
        "osce",
        "organization for security and co-operation in europe",
        "organization for security and cooperation in europe",
    ],
    "OSCE ODIHR": [
        "osce odihr",
        "odihr",
        "office for democratic institutions and human rights",
    ],
    "Council of Europe": [
        "council of europe",
    ],
    "Parliamentary Assembly of the Council of Europe": [
        "parliamentary assembly of the council of europe",
        "pace",
    ],
    "Venice Commission": [
        "venice commission",
        "european commission for democracy through law",
    ],

    # Regional / geopolitical formats
    "Bucharest Nine": [
        "bucharest nine",
        "b9",
    ],
    "Three Seas Initiative": [
        "three seas initiative",
        "3si",
    ],
    "Black Sea Economic Cooperation": [
        "organization of the black sea economic cooperation",
        "black sea economic cooperation",
        "bsec",
    ],
    "CSTO": [
        "collective security treaty organization",
        "csto",
    ],
    "Commonwealth of Independent States": [
        "commonwealth of independent states",
        "cis",
    ],
    "Eurasian Economic Union": [
        "eurasian economic union",
        "eaeu",
    ],

    # Romania
    "Ministry of Foreign Affairs of Romania": [
        "ministry of foreign affairs of romania",
        "romanian ministry of foreign affairs",
        "mae romania",
        "mae of romania",
        "ministerul afacerilor externe al romaniei",
        "ministerul afacerilor externe al româniei",
        "mae al romaniei",
        "mae al româniei",
    ],
    "Ministry of National Defence of Romania": [
        "ministry of national defence of romania",
        "ministry of national defense of romania",
        "romanian ministry of national defence",
        "romanian ministry of national defense",
        "ministerul apararii nationale",
        "ministerul apărării naționale",
        "ministerul apararii nationale al romaniei",
        "ministerul apărării naționale al româniei",
        "mapn",
        "mapn romania",
        "mapn românia",
    ],
    "Presidency of Romania": [
        "presidency of romania",
        "romanian presidency",
        "presidential administration of romania",
        "administratia prezidentiala",
        "administrația prezidențială",
    ],
    "Government of Romania": [
        "government of romania",
        "romanian government",
        "guvernul romaniei",
        "guvernul româniei",
    ],
    "Romanian Parliament": [
        "romanian parliament",
        "parliament of romania",
        "parlamentul romaniei",
        "parlamentul româniei",
    ],

    # Republic of Moldova
    "Ministry of Foreign Affairs of the Republic of Moldova": [
        "ministry of foreign affairs of the republic of moldova",
        "ministry of foreign affairs of moldova",
        "moldovan ministry of foreign affairs",
        "mfa of moldova",
        "ministerul afacerilor externe al republicii moldova",
    ],
    "Presidency of the Republic of Moldova": [
        "presidency of the republic of moldova",
        "presidency of moldova",
        "moldovan presidency",
        "presedintia republicii moldova",
        "președinția republicii moldova",
    ],
    "Government of the Republic of Moldova": [
        "government of the republic of moldova",
        "government of moldova",
        "moldovan government",
        "guvernul republicii moldova",
    ],
    "Parliament of the Republic of Moldova": [
        "parliament of the republic of moldova",
        "parliament of moldova",
        "moldovan parliament",
        "parlamentul republicii moldova",
    ],
    "Intelligence and Security Service of Moldova": [
        "intelligence and security service of the republic of moldova",
        "intelligence and security service of moldova",
        "moldovan intelligence and security service",
        "serviciul de informatii si securitate",
        "serviciul de informații și securitate",
        "sis moldova",
    ],
    "National Army of the Republic of Moldova": [
        "national army of the republic of moldova",
        "national army of moldova",
        "moldovan national army",
        "armata nationala a republicii moldova",
        "armata națională a republicii moldova",
    ],

    # Ukraine
    "Ministry of Foreign Affairs of Ukraine": [
        "ministry of foreign affairs of ukraine",
        "ukrainian ministry of foreign affairs",
        "mfa of ukraine",
    ],
    "Office of the President of Ukraine": [
        "office of the president of ukraine",
        "presidential office of ukraine",
        "office of president zelenskyy",
    ],
    "Ministry of Defence of Ukraine": [
        "ministry of defence of ukraine",
        "ministry of defense of ukraine",
        "ukrainian ministry of defence",
        "ukrainian ministry of defense",
        "mod of ukraine",
    ],
    "Armed Forces of Ukraine": [
        "armed forces of ukraine",
        "ukrainian armed forces",
        "afu",
    ],
    "Security Service of Ukraine": [
        "security service of ukraine",
        "ssu",
        "sbu",
    ],
    "Main Directorate of Intelligence of Ukraine": [
        "main directorate of intelligence of the ministry of defence of ukraine",
        "main intelligence directorate of ukraine",
        "ukrainian military intelligence",
    ],
    "Verkhovna Rada": [
        "verkhovna rada",
        "ukrainian parliament",
        "parliament of ukraine",
    ],

    # Russia
    "Kremlin": [
        "kremlin",
    ],
    "Ministry of Foreign Affairs of the Russian Federation": [
        "ministry of foreign affairs of the russian federation",
        "russian ministry of foreign affairs",
        "foreign ministry of russia",
        "russian foreign ministry",
    ],
    "Ministry of Defence of the Russian Federation": [
        "ministry of defence of the russian federation",
        "ministry of defense of the russian federation",
        "russian ministry of defence",
        "russian ministry of defense",
        "russian defense ministry",
    ],
    "Armed Forces of the Russian Federation": [
        "armed forces of the russian federation",
        "russian armed forces",
        "russian forces",
    ],
    "Security Council of the Russian Federation": [
        "security council of the russian federation",
        "russian security council",
    ],
    "State Duma": [
        "state duma",
        "duma",
        "russian state duma",
    ],
    "Federal Security Service": [
        "federal security service",
        "federal security service of the russian federation",
        "fsb",
    ],
    "Foreign Intelligence Service of Russia": [
        "foreign intelligence service of the russian federation",
        "russian foreign intelligence service",
        "svr",
    ],
    "GRU": [
        "gru",
        "main intelligence directorate of the general staff of the armed forces of the russian federation",
        "main directorate of the general staff of the armed forces of the russian federation",
    ],
    "Rosgvardiya": [
        "rosgvardiya",
        "national guard of russia",
        "russian national guard",
    ],

    # United States
    "U.S. Department of State": [
        "u.s. department of state",
        "us department of state",
        "united states department of state",
        "state department",
    ],
    "U.S. Department of Defense": [
        "u.s. department of defense",
        "u.s. department of defence",
        "us department of defense",
        "us department of defence",
        "united states department of defense",
        "united states department of defence",
        "department of defense",
        "department of defence",
        "defense department",
        "defence department",
        "pentagon",
    ],
    "White House": [
        "white house",
    ],
    "U.S. National Security Council": [
        "u.s. national security council",
        "us national security council",
        "national security council",
    ],

    # Think tanks / analytical organizations
    "European Council on Foreign Relations": [
        "european council on foreign relations",
        "ecfr",
    ],
    "Institute for the Study of War": [
        "institute for the study of war",
        "isw",
    ],
    "Chatham House": [
        "chatham house",
        "royal institute of international affairs",
    ],
    "German Marshall Fund": [
        "german marshall fund",
        "the german marshall fund",
        "gmf",
    ],
    "Carnegie Endowment for International Peace": [
        "carnegie endowment for international peace",
        "carnegie endowment",
        "carnegie europe",
    ],
    "Atlantic Council": [
        "atlantic council",
    ],
    "Center for European Policy Analysis": [
        "center for european policy analysis",
        "centre for european policy analysis",
        "cepa",
    ],
}

PERSON_KEYWORDS = {
    # Romania
    "Oana Toiu": [
        "oana toiu",
        "oana țoiu",
        "toiu",
        "țoiu",
    ],
    "Klaus Iohannis": [
        "klaus iohannis",
        "iohannis",
    ],
    "Marcel Ciolacu": [
        "marcel ciolacu",
        "ciolacu",
    ],
    "Nicolae Ciuca": [
        "nicolae ciuca",
        "nicolae ciucă",
        "ciuca",
        "ciucă",
    ],
    "Bogdan Aurescu": [
        "bogdan aurescu",
        "aurescu",
    ],
    "Luminita Odobescu": [
        "luminita odobescu",
        "luminița odobescu",
        "odobescu",
    ],
    "Mircea Geoana": [
        "mircea geoana",
        "mircea geoană",
        "geoana",
        "geoană",
    ],

    # Republic of Moldova
    "Maia Sandu": [
        "maia sandu",
        "sandu",
    ],
    "Mihai Popsoi": [
        "mihai popsoi",
        "mihai popșoi",
        "popsoi",
        "popșoi",
    ],
    "Dorin Recean": [
        "dorin recean",
        "recean",
    ],
    "Igor Grosu": [
        "igor grosu",
    ],
    "Nicu Popescu": [
        "nicu popescu",
    ],
    "Igor Dodon": [
        "igor dodon",
        "dodon",
    ],

    # Ukraine
    "Volodymyr Zelenskyy": [
        "volodymyr zelenskyy",
        "volodymyr zelensky",
        "volodimir zelenski",
        "zelenskyy",
        "zelensky",
    ],
    "Andrii Sybiha": [
        "andrii sybiha",
        "andriy sybiha",
        "sybiha",
    ],
    "Dmytro Kuleba": [
        "dmytro kuleba",
        "kuleba",
    ],
    "Denys Shmyhal": [
        "denys shmyhal",
        "shmyhal",
    ],
    "Andriy Yermak": [
        "andriy yermak",
        "andrii yermak",
        "yermak",
    ],
    "Rustem Umerov": [
        "rustem umerov",
        "umerov",
    ],
    "Oleksii Reznikov": [
        "oleksii reznikov",
        "oleksiy reznikov",
        "reznikov",
    ],
    "Valerii Zaluzhnyi": [
        "valerii zaluzhnyi",
        "valery zaluzhny",
        "zaluzhnyi",
        "zaluzhny",
    ],
    "Oleksandr Syrskyi": [
        "oleksandr syrskyi",
        "oleksandr syrsky",
        "syrskyi",
        "syrsky",
    ],
    "Kyrylo Budanov": [
        "kyrylo budanov",
        "budanov",
    ],

    # Russia
    "Vladimir Putin": [
        "vladimir putin",
        "putin",
    ],
    "Sergei Lavrov": [
        "sergei lavrov",
        "sergey lavrov",
        "lavrov",
    ],
    "Dmitry Peskov": [
        "dmitry peskov",
        "dmitri peskov",
        "peskov",
    ],
    "Dmitry Medvedev": [
        "dmitry medvedev",
        "dmitri medvedev",
        "medvedev",
    ],
    "Sergei Shoigu": [
        "sergei shoigu",
        "sergey shoigu",
        "shoigu",
    ],
    "Valery Gerasimov": [
        "valery gerasimov",
        "valeriy gerasimov",
        "gerasimov",
    ],
    "Nikolai Patrushev": [
        "nikolai patrushev",
        "nikolay patrushev",
        "patrushev",
    ],
    "Alexei Navalny": [
        "alexei navalny",
        "alexey navalny",
        "navalny",
    ],
    "Yevgeny Prigozhin": [
        "yevgeny prigozhin",
        "evgeny prigozhin",
        "prigozhin",
    ],
    "Sergei Surovikin": [
        "sergei surovikin",
        "sergey surovikin",
        "surovikin",
    ],

    # NATO / EU
    "Mark Rutte": [
        "mark rutte",
        "rutte",
    ],
    "Jens Stoltenberg": [
        "jens stoltenberg",
        "stoltenberg",
    ],
    "Ursula von der Leyen": [
        "ursula von der leyen",
        "von der leyen",
    ],
    "Kaja Kallas": [
        "kaja kallas",
        "kallas",
    ],
    "Josep Borrell": [
        "josep borrell",
        "borrell",
    ],
    "Antonio Costa": [
        "antonio costa",
        "antónio costa",
    ],
    "Charles Michel": [
        "charles michel",
    ],
    "Roberta Metsola": [
        "roberta metsola",
        "metsola",
    ],

    # United States
    "Donald Trump": [
        "donald trump",
        "trump",
    ],
    "Joe Biden": [
        "joe biden",
        "joseph biden",
        "biden",
    ],
    "Marco Rubio": [
        "marco rubio",
        "rubio",
    ],
    "J.D. Vance": [
        "j.d. vance",
        "jd vance",
        "j d vance",
        "vance",
    ],
    "Antony Blinken": [
        "antony blinken",
        "blinken",
    ],
    "Lloyd Austin": [
        "lloyd austin",
    ],
    "Jake Sullivan": [
        "jake sullivan",
    ],
    "Pete Hegseth": [
        "pete hegseth",
        "hegseth",
    ],

    # United Kingdom
    "Keir Starmer": [
        "keir starmer",
        "starmer",
    ],
    "David Lammy": [
        "david lammy",
        "lammy",
    ],
    "Yvette Cooper": [
        "yvette cooper",
    ],
    "Rishi Sunak": [
        "rishi sunak",
        "sunak",
    ],
    "Boris Johnson": [
        "boris johnson",
    ],

    # France / Germany / Poland / Baltic / Turkey / wider region
    "Emmanuel Macron": [
        "emmanuel macron",
        "macron",
    ],
    "Olaf Scholz": [
        "olaf scholz",
        "scholz",
    ],
    "Annalena Baerbock": [
        "annalena baerbock",
        "baerbock",
    ],
    "Donald Tusk": [
        "donald tusk",
        "tusk",
    ],
    "Andrzej Duda": [
        "andrzej duda",
        "duda",
    ],
    "Radoslaw Sikorski": [
        "radoslaw sikorski",
        "radosław sikorski",
        "sikorski",
    ],
    "Gitanas Nauseda": [
        "gitanas nauseda",
        "gitanas nausėda",
        "nauseda",
        "nausėda",
    ],
    "Edgars Rinkevics": [
        "edgars rinkevics",
        "edgars rinkēvičs",
        "rinkevics",
        "rinkēvičs",
    ],
    "Recep Tayyip Erdogan": [
        "recep tayyip erdogan",
        "recep tayyip erdoğan",
        "erdogan",
        "erdoğan",
    ],
    "Hakan Fidan": [
        "hakan fidan",
        "fidan",
    ],
    "Alexander Lukashenko": [
        "alexander lukashenko",
        "aleksandr lukashenko",
        "lukashenko",
    ],
    "Antonio Guterres": [
        "antonio guterres",
        "antónio guterres",
        "guterres",
    ],
    "Viktor Orban": [
        "viktor orban",
        "viktor orbán",
        "orban",
        "orbán",
    ],
    "Aleksandar Vucic": [
        "aleksandar vucic",
        "aleksandar vučić",
        "vucic",
        "vučić",
    ],
}

LOCATION_KEYWORDS = {
    "Black Sea": [
        "black sea",
        "black-sea",
    ],
    "Black Sea Region": [
        "black sea region",
        "black sea area",
    ],
    "Black Sea Basin": [
        "black sea basin",
    ],
    "Western Black Sea": [
        "western black sea",
    ],
    "Northern Black Sea": [
        "northern black sea",
    ],
    "Romanian Black Sea Coast": [
        "romanian black sea coast",
        "romanian black sea littoral",
        "romanian littoral",
    ],
    "Sea of Azov": [
        "sea of azov",
        "azov sea",
    ],
    "Danube": [
        "danube",
        "danube river",
    ],
    "Danube Delta": [
        "danube delta",
    ],
    "Lower Danube": [
        "lower danube",
        "lower danube region",
    ],
    "Dniester": [
        "dniester",
        "dnister",
        "dniester river",
        "dnister river",
    ],
    "Prut": [
        "prut",
        "prut river",
    ],
    "Bosphorus": [
        "bosphorus",
        "bosporus",
        "istanbul strait",
    ],
    "Turkish Straits": [
        "turkish straits",
        "straits of turkey",
    ],
    "Crimea": [
        "crimea",
        "crimean peninsula",
    ],
    "Donbas": [
        "donbas",
        "donbass",
    ],
    "Transnistria": [
        "transnistria",
        "transdniestria",
    ],
    "Gagauzia": [
        "gagauzia",
        "autonomous territorial unit of gagauzia",
    ],
    "Eastern Ukraine": [
        "eastern ukraine",
    ],
    "Southern Ukraine": [
        "southern ukraine",
    ],
    "Eastern Europe": [
        "eastern europe",
    ],
    "Central and Eastern Europe": [
        "central and eastern europe",
    ],
    "Southeastern Europe": [
        "southeastern europe",
        "south-eastern europe",
        "south eastern europe",
    ],
    "Eastern Mediterranean": [
        "eastern mediterranean",
    ],
    "Western Balkans": [
        "western balkans",
    ],
    "Baltic Sea": [
        "baltic sea",
    ],
    "Baltic Region": [
        "baltic region",
    ],
    "Baltic States": [
        "baltic states",
    ],
    "South Caucasus": [
        "south caucasus",
        "southern caucasus",
    ],
    "Eastern Neighbourhood": [
        "eastern neighbourhood",
        "eastern neighborhood",
    ],
    "Eastern Flank": [
        "eastern flank",
        "nato eastern flank",
        "nato's eastern flank",
        "alliance's eastern flank",
    ],
    "Bucharest": [
        "bucharest",
        "bucuresti",
        "bucurești",
    ],
    "Chisinau": [
        "chisinau",
        "chișinău",
        "kishinev",
    ],
    "Iasi": [
        "iasi",
        "iași",
    ],
    "Galati": [
        "galati",
        "galați",
    ],
    "Tulcea": [
        "tulcea",
    ],
    "Constanta": [
        "constanta",
        "constanța",
    ],
    "Cernavoda": [
        "cernavoda",
        "cernavodă",
    ],
    "Sulina": [
        "sulina",
    ],
    "Ungheni": [
        "ungheni",
    ],
    "Tiraspol": [
        "tiraspol",
    ],
    "Comrat": [
        "comrat",
    ],
    "Balti": [
        "balti",
        "bălți",
    ],
    "Kyiv": [
        "kyiv",
        "kiev",
        "kyiv city",
    ],
    "Kyiv Oblast": [
        "kyiv oblast",
        "kyiv region",
        "kiev region",
    ],
    "Odesa": [
        "odesa",
        "odessa",
    ],
    "Odesa Oblast": [
        "odesa oblast",
        "odessa oblast",
        "odesa region",
        "odessa region",
    ],
    "Lviv": [
        "lviv",
        "lvov",
    ],
    "Kharkiv": [
        "kharkiv",
        "kharkov",
    ],
    "Kherson": [
        "kherson",
    ],
    "Kherson Oblast": [
        "kherson oblast",
        "kherson region",
    ],
    "Zaporizhzhia": [
        "zaporizhzhia",
        "zaporizhzhia",
        "zaporozhye",
    ],
    "Zaporizhzhia Oblast": [
        "zaporizhzhia oblast",
        "zaporozhye region",
    ],
    "Dnipro": [
        "dnipro",
        "dnepropetrovsk",
    ],
    "Donetsk": [
        "donetsk",
    ],
    "Donetsk Oblast": [
        "donetsk oblast",
        "donetsk region",
    ],
    "Luhansk": [
        "luhansk",
        "lugansk",
    ],
    "Luhansk Oblast": [
        "luhansk oblast",
        "lugansk region",
    ],
    "Mariupol": [
        "mariupol",
    ],
    "Sevastopol": [
        "sevastopol",
    ],
    "Simferopol": [
        "simferopol",
    ],
    "Mykolaiv": [
        "mykolaiv",
        "nikolaev",
    ],
    "Chernihiv": [
        "chernihiv",
        "chernigov",
    ],
    "Sumy": [
        "sumy",
    ],
    "Kramatorsk": [
        "kramatorsk",
    ],
    "Bakhmut": [
        "bakhmut",
        "artemivsk",
    ],
    "Snake Island": [
        "snake island",
        "zmiinyi island",
        "serpents island",
    ],
    "Moscow": [
        "moscow",
    ],
    "Brussels": [
        "brussels",
        "bruxelles",
    ],
    "Strasbourg": [
        "strasbourg",
    ],
    "Washington, D.C.": [
        "washington",
        "washington dc",
        "washington, dc",
        "washington d.c.",
        "washington, d.c.",
    ],
    "New York": [
        "new york",
        "new york city",
        "nyc",
    ],
    "Vilnius": [
        "vilnius",
    ],
    "Warsaw": [
        "warsaw",
    ],
    "Sofia": [
        "sofia",
    ],
    "Ankara": [
        "ankara",
    ],
    "Istanbul": [
        "istanbul",
    ],
    "Riga": [
        "riga",
    ],
    "Tallinn": [
        "tallinn",
    ],
    "Budapest": [
        "budapest",
    ],
    "Prague": [
        "prague",
    ],
    "Berlin": [
        "berlin",
    ],
    "Paris": [
        "paris",
    ],
    "London": [
        "london",
    ],
    "The Hague": [
        "the hague",
        "hague",
    ],
    "Munich": [
        "munich",
        "muenchen",
        "münchen",
    ],
    "Geneva": [
        "geneva",
        "genève",
    ],
}