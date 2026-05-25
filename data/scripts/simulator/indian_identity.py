"""
JEET Simulator — Indian Identity Generator

Generates culturally accurate Indian names, cities, schools, emails, and phones.
Names are region-correlated: Tamil names with Tamil Nadu cities, Bengali names with
West Bengal cities, etc. This is what separates believable EdTech data from
"Faker().name()" garbage.
"""

import random
from typing import Tuple

# =============================================================
# REGIONAL NAME POOLS
# =============================================================
# Source: Most common names by region from Census data + JEE/NEET
# qualifier lists (publicly available from past 5 years).
# =============================================================

# ---------- NORTH INDIA (Hindi-belt) ----------
NORTH_FIRST_NAMES_MALE = [
    "Aarav", "Arjun", "Aditya", "Aniket", "Ansh", "Ayush", "Dev", "Dhruv",
    "Gaurav", "Harsh", "Ishaan", "Kabir", "Karan", "Krishna", "Kunal",
    "Madhav", "Manav", "Mayank", "Mohit", "Naman", "Nikhil", "Parth",
    "Pranav", "Rahul", "Raj", "Rishabh", "Rohan", "Sahil", "Samar",
    "Shaurya", "Shivam", "Siddharth", "Tanmay", "Tushar", "Utkarsh",
    "Vaibhav", "Varun", "Vihaan", "Yash", "Yuvraj",
]
NORTH_FIRST_NAMES_FEMALE = [
    "Aanya", "Aarohi", "Anika", "Anjali", "Avani", "Bhavya", "Diya", "Garima",
    "Gauri", "Ishita", "Kavya", "Khushi", "Kriti", "Lavanya", "Mahi",
    "Mahika", "Manvi", "Meera", "Muskan", "Nandini", "Navya", "Niharika",
    "Palak", "Pari", "Pooja", "Prachi", "Priya", "Riya", "Saanvi", "Sakshi",
    "Sanya", "Shreya", "Simran", "Tanvi", "Tanya", "Vaishnavi", "Vanya",
]
NORTH_SURNAMES = [
    "Sharma", "Verma", "Gupta", "Agarwal", "Mishra", "Tiwari", "Shukla",
    "Pandey", "Singh", "Yadav", "Kumar", "Saxena", "Srivastava", "Bansal",
    "Goel", "Goyal", "Jain", "Mittal", "Kapoor", "Khanna", "Chopra",
    "Malhotra", "Mehra", "Bhatia", "Sethi", "Arora", "Kohli", "Sood",
]

# ---------- SOUTH INDIA — TAMIL ----------
TAMIL_FIRST_NAMES_MALE = [
    "Aakash", "Arun", "Balaji", "Dhinesh", "Ganesh", "Hari", "Karthik",
    "Karthikeyan", "Krishnan", "Lakshman", "Mahesh", "Murali", "Naveen",
    "Prakash", "Pranav", "Praveen", "Rajesh", "Ramesh", "Ravi", "Sanjay",
    "Saravanan", "Senthil", "Shankar", "Sundar", "Surya", "Vignesh", "Vijay",
]
TAMIL_FIRST_NAMES_FEMALE = [
    "Aishwarya", "Anjali", "Anu", "Bhavana", "Deepa", "Divya", "Hema",
    "Janani", "Jaya", "Kamala", "Kavitha", "Lakshmi", "Latha", "Madhuri",
    "Meena", "Padma", "Priya", "Radha", "Rekha", "Sangeetha", "Saranya",
    "Sneha", "Sowmya", "Sudha", "Sumathi", "Suganya", "Vidya",
]
TAMIL_SURNAMES = [
    "Iyer", "Iyengar", "Pillai", "Naidu", "Chettiar", "Mudaliar", "Reddy",
    "Krishnan", "Subramaniam", "Raman", "Natarajan", "Venkatesan",
    "Srinivasan", "Ramachandran", "Sundaram",
]

# ---------- SOUTH INDIA — TELUGU ----------
TELUGU_FIRST_NAMES_MALE = [
    "Anil", "Anand", "Arjun", "Bharath", "Chaitanya", "Charan", "Goutham",
    "Karthik", "Kiran", "Krishna", "Manoj", "Naveen", "Pavan", "Phaneendra",
    "Prashanth", "Ravi", "Rohith", "Sai", "Sandeep", "Srikanth", "Sudhir",
    "Surya", "Teja", "Venkat", "Vijay", "Vinay",
]
TELUGU_FIRST_NAMES_FEMALE = [
    "Anjali", "Anusha", "Bhavani", "Deepika", "Divya", "Geetha", "Haritha",
    "Jhansi", "Kavya", "Keerthi", "Lavanya", "Madhavi", "Manasa", "Mounika",
    "Nandini", "Pavani", "Pranathi", "Priya", "Sahasra", "Sai Sri", "Sandhya",
    "Sirisha", "Sneha", "Sravani", "Sushma", "Swathi",
]
TELUGU_SURNAMES = [
    "Reddy", "Naidu", "Rao", "Sharma", "Raju", "Chowdhary", "Goud", "Yadav",
    "Varma", "Murthy", "Sastry", "Patnaik", "Babu",
]

# ---------- KARNATAKA — KANNADA ----------
KANNADA_FIRST_NAMES_MALE = [
    "Aakash", "Abhishek", "Adithya", "Akshay", "Anirudh", "Arjun", "Chetan",
    "Darshan", "Ganesh", "Harish", "Karthik", "Manjunath", "Naveen",
    "Pavan", "Prajwal", "Pranav", "Prashanth", "Rakshith", "Sandeep",
    "Shashank", "Sudeep", "Sundeep", "Tarun", "Yashas",
]
KANNADA_FIRST_NAMES_FEMALE = [
    "Aishwarya", "Ananya", "Anjali", "Anushka", "Apoorva", "Bhavana",
    "Chaitra", "Deepa", "Divya", "Jyothi", "Kavya", "Lakshmi", "Manasa",
    "Meghana", "Nayana", "Niveditha", "Pavithra", "Pooja", "Pranati",
    "Priya", "Ramya", "Shilpa", "Sindhu", "Spoorthi", "Sushma", "Trisha",
]
KANNADA_SURNAMES = [
    "Gowda", "Rao", "Hegde", "Shetty", "Pai", "Bhat", "Kulkarni", "Joshi",
    "Iyengar", "Reddy", "Acharya", "Patil", "Murthy", "Sastry",
]

# ---------- WEST BENGAL — BENGALI ----------
BENGALI_FIRST_NAMES_MALE = [
    "Aniket", "Aniruddha", "Arnab", "Arpan", "Arijit", "Avik", "Debojit",
    "Diptesh", "Indranil", "Joydeep", "Kaustubh", "Pritam", "Rohit",
    "Sandeep", "Sayantan", "Shubham", "Soumya", "Soumyadeep", "Souvik",
    "Subhajit", "Subhrajit", "Sudipto", "Sumit", "Tirthankar",
]
BENGALI_FIRST_NAMES_FEMALE = [
    "Ananya", "Anwesha", "Aparajita", "Debanjana", "Debjani", "Indrani",
    "Ishita", "Madhumita", "Mahasweta", "Moushumi", "Nandini", "Nilanjana",
    "Paramita", "Paroma", "Piyali", "Pratyusha", "Rituparna", "Sayani",
    "Shreya", "Sohini", "Sreyasi", "Sucharita", "Suchitra", "Susmita",
]
BENGALI_SURNAMES = [
    "Banerjee", "Chatterjee", "Mukherjee", "Bhattacharya", "Roy", "Dutta",
    "Sen", "Bose", "Ghosh", "Das", "Saha", "Mitra", "Chakraborty",
    "Sengupta", "Dasgupta", "Lahiri", "Majumdar", "Pal",
]

# ---------- MAHARASHTRA — MARATHI ----------
MARATHI_FIRST_NAMES_MALE = [
    "Aniket", "Atharva", "Chinmay", "Harshad", "Kaustubh", "Mandar",
    "Mihir", "Nilesh", "Omkar", "Onkar", "Parth", "Prasad", "Pratham",
    "Pratik", "Pushkar", "Rohan", "Rohit", "Sagar", "Sahil", "Sameer",
    "Sandip", "Sanket", "Shantanu", "Shreyas", "Soham", "Yash",
]
MARATHI_FIRST_NAMES_FEMALE = [
    "Aboli", "Aditi", "Aishwarya", "Aishwarya", "Apeksha", "Aparna", "Asawari",
    "Bhakti", "Gauri", "Indira", "Janhavi", "Komal", "Madhuri", "Mansi",
    "Manasi", "Mrunal", "Pranjal", "Prerna", "Radhika", "Rasika", "Sakshi",
    "Shraddha", "Shruti", "Smita", "Snehal", "Sonali", "Tejaswini",
]
MARATHI_SURNAMES = [
    "Patil", "Deshmukh", "Joshi", "Kulkarni", "Deshpande", "Pawar", "Jadhav",
    "Shinde", "More", "Bhosale", "Gaikwad", "Chavan", "Salunkhe", "Naik",
    "Marathe", "Kale", "Sawant", "Phadke", "Pandit",
]

# ---------- KERALA — MALAYALI ----------
MALAYALI_FIRST_NAMES_MALE = [
    "Abhinav", "Adithya", "Akhil", "Akshay", "Alok", "Anand", "Anirudh",
    "Arjun", "Aryan", "Ashwin", "Gokul", "Hari", "Jishnu", "Karthik",
    "Kishore", "Krishna", "Manu", "Nikhil", "Pranav", "Rahul", "Vishnu",
]
MALAYALI_FIRST_NAMES_FEMALE = [
    "Aiswarya", "Ananya", "Anjali", "Arya", "Devika", "Gayathri", "Keerthana",
    "Lakshmi", "Malavika", "Meera", "Nandana", "Niranjana", "Parvathy",
    "Pooja", "Sneha", "Vidya",
]
MALAYALI_SURNAMES = [
    "Nair", "Menon", "Pillai", "Kurup", "Warrier", "Iyer", "Krishnan",
    "Namboothiri", "Panicker", "Thampi", "Variar",
]

# ---------- GUJARAT — GUJARATI ----------
GUJARATI_FIRST_NAMES_MALE = [
    "Aarav", "Aayush", "Akshay", "Bhavik", "Chirag", "Darshan", "Dhruv",
    "Divyesh", "Harsh", "Hiren", "Jay", "Karan", "Kunal", "Manan",
    "Meet", "Nirav", "Parth", "Pratik", "Raj", "Ravi", "Smit", "Vivek",
]
GUJARATI_FIRST_NAMES_FEMALE = [
    "Aanya", "Avni", "Bhumi", "Charmi", "Dhwani", "Disha", "Drishti",
    "Foram", "Heli", "Heta", "Janvi", "Khushi", "Krupa", "Nidhi",
    "Pooja", "Priyanka", "Riya", "Tanvi", "Tisha", "Urvi",
]
GUJARATI_SURNAMES = [
    "Patel", "Shah", "Mehta", "Desai", "Modi", "Trivedi", "Joshi", "Pandya",
    "Dave", "Vyas", "Parikh", "Soni", "Thakkar", "Bhatt", "Acharya",
]


# =============================================================
# CITY DATA WITH REGIONAL MAPPING
# =============================================================

# (city, tier, region) — region determines name pool
CITY_REGISTRY = [
    # ----- TIER 1 -----
    ("Mumbai",      "tier_1", "marathi"),
    ("Delhi",       "tier_1", "north"),
    ("Bangalore",   "tier_1", "kannada"),
    ("Chennai",     "tier_1", "tamil"),
    ("Hyderabad",   "tier_1", "telugu"),
    ("Pune",        "tier_1", "marathi"),
    ("Kolkata",     "tier_1", "bengali"),
    ("Ahmedabad",   "tier_1", "gujarati"),

    # ----- TIER 2 -----
    ("Jaipur",      "tier_2", "north"),
    ("Lucknow",     "tier_2", "north"),
    ("Kanpur",      "tier_2", "north"),
    ("Nagpur",      "tier_2", "marathi"),
    ("Indore",      "tier_2", "north"),
    ("Bhopal",      "tier_2", "north"),
    ("Patna",       "tier_2", "north"),
    ("Surat",       "tier_2", "gujarati"),
    ("Vadodara",    "tier_2", "gujarati"),
    ("Coimbatore",  "tier_2", "tamil"),
    ("Visakhapatnam","tier_2", "telugu"),
    ("Bhubaneswar", "tier_2", "bengali"),  # Closest cultural fit
    ("Chandigarh",  "tier_2", "north"),
    ("Kochi",       "tier_2", "malayali"),
    ("Mysore",      "tier_2", "kannada"),
    ("Mangalore",   "tier_2", "kannada"),
    ("Madurai",     "tier_2", "tamil"),
    ("Trichy",      "tier_2", "tamil"),
    ("Salem",       "tier_2", "tamil"),
    ("Vijayawada",  "tier_2", "telugu"),
    ("Thiruvananthapuram", "tier_2", "malayali"),

    # ----- TIER 3 (Coaching hubs + smaller cities) -----
    ("Kota",        "tier_3", "north"),
    ("Sikar",       "tier_3", "north"),
    ("Aligarh",     "tier_3", "north"),
    ("Meerut",      "tier_3", "north"),
    ("Allahabad",   "tier_3", "north"),
    ("Varanasi",    "tier_3", "north"),
    ("Gorakhpur",   "tier_3", "north"),
    ("Jabalpur",    "tier_3", "north"),
    ("Gwalior",     "tier_3", "north"),
    ("Ranchi",      "tier_3", "north"),
    ("Dhanbad",     "tier_3", "north"),
    ("Jamshedpur",  "tier_3", "bengali"),
    ("Bhilai",      "tier_3", "north"),
    ("Raipur",      "tier_3", "north"),
    ("Hubli",       "tier_3", "kannada"),
    ("Belgaum",     "tier_3", "kannada"),
    ("Tirupati",    "tier_3", "telugu"),
    ("Guntur",      "tier_3", "telugu"),
    ("Kollam",      "tier_3", "malayali"),
    ("Rajkot",      "tier_3", "gujarati"),
    ("Nashik",      "tier_3", "marathi"),
    ("Aurangabad",  "tier_3", "marathi"),
    ("Solapur",     "tier_3", "marathi"),
]

KOTA_HUB_CITIES = {"Kota", "Sikar", "Hyderabad", "Delhi"}  # Coaching hubs

# Cities by tier (for sampling)
TIER_1_CITIES = [c for c in CITY_REGISTRY if c[1] == "tier_1"]
TIER_2_CITIES = [c for c in CITY_REGISTRY if c[1] == "tier_2"]
TIER_3_CITIES = [c for c in CITY_REGISTRY if c[1] == "tier_3"]


# =============================================================
# NAME POOL LOOKUP
# =============================================================
REGION_NAME_POOLS = {
    "north": {
        "male":    NORTH_FIRST_NAMES_MALE,
        "female":  NORTH_FIRST_NAMES_FEMALE,
        "surname": NORTH_SURNAMES,
    },
    "tamil": {
        "male":    TAMIL_FIRST_NAMES_MALE,
        "female":  TAMIL_FIRST_NAMES_FEMALE,
        "surname": TAMIL_SURNAMES,
    },
    "telugu": {
        "male":    TELUGU_FIRST_NAMES_MALE,
        "female":  TELUGU_FIRST_NAMES_FEMALE,
        "surname": TELUGU_SURNAMES,
    },
    "kannada": {
        "male":    KANNADA_FIRST_NAMES_MALE,
        "female":  KANNADA_FIRST_NAMES_FEMALE,
        "surname": KANNADA_SURNAMES,
    },
    "bengali": {
        "male":    BENGALI_FIRST_NAMES_MALE,
        "female":  BENGALI_FIRST_NAMES_FEMALE,
        "surname": BENGALI_SURNAMES,
    },
    "marathi": {
        "male":    MARATHI_FIRST_NAMES_MALE,
        "female":  MARATHI_FIRST_NAMES_FEMALE,
        "surname": MARATHI_SURNAMES,
    },
    "malayali": {
        "male":    MALAYALI_FIRST_NAMES_MALE,
        "female":  MALAYALI_FIRST_NAMES_FEMALE,
        "surname": MALAYALI_SURNAMES,
    },
    "gujarati": {
        "male":    GUJARATI_FIRST_NAMES_MALE,
        "female":  GUJARATI_FIRST_NAMES_FEMALE,
        "surname": GUJARATI_SURNAMES,
    },
}


# =============================================================
# SCHOOL NAME GENERATOR
# =============================================================
SCHOOL_PREFIXES = [
    "Delhi Public", "Kendriya Vidyalaya", "DAV Public", "Ryan International",
    "Bal Bharati", "Sanskriti", "Springdales", "Modern", "St. Xavier's",
    "Loyola", "Bishop Cotton", "St. Mary's", "Carmel", "Don Bosco",
    "Jawahar Navodaya Vidyalaya", "Army Public", "Chinmaya Vidyalaya",
    "Saraswati Vidya Mandir", "Holy Cross", "St. Joseph's", "Vidyamandir",
    "Vidyaniketan", "National Public", "Greenwood High", "Inventure Academy",
    "FIITJEE Junior College", "Narayana E-Techno", "Sri Chaitanya",
    "Allen Junior", "Aakash Junior",
]
SCHOOL_SUFFIXES = ["School", "Public School", "International School", "Vidyalaya", "Academy"]


# =============================================================
# PUBLIC API
# =============================================================
def sample_city(rng: random.Random) -> Tuple[str, str, str]:
    """Sample (city, tier, region) respecting tier distribution: 25/45/30."""
    r = rng.random()
    if r < 0.25:
        return rng.choice(TIER_1_CITIES)
    elif r < 0.70:
        return rng.choice(TIER_2_CITIES)
    else:
        return rng.choice(TIER_3_CITIES)


def sample_name(rng: random.Random, gender: str, region: str) -> Tuple[str, str]:
    """
    Sample (first_name, surname) from the regional pool.
    gender: 'male' | 'female'
    region: 'north' | 'tamil' | 'telugu' | 'kannada' | 'bengali' | 'marathi' | 'malayali' | 'gujarati'
    """
    pool = REGION_NAME_POOLS[region]
    first_name = rng.choice(pool[gender])
    surname = rng.choice(pool["surname"])
    return first_name, surname


def generate_email(rng: random.Random, first_name: str, surname: str, birth_year: int) -> str:
    """Generate realistic Indian student email pattern."""
    fn = first_name.lower().replace(" ", "")
    sn = surname.lower().replace(" ", "")
    domain = rng.choices(
        ["gmail.com", "yahoo.com", "outlook.com", "rediffmail.com"],
        weights=[0.75, 0.10, 0.12, 0.03],
        k=1,
    )[0]
    patterns = [
        f"{fn}.{sn}{birth_year % 100:02d}@{domain}",
        f"{fn}{sn}{birth_year % 100:02d}@{domain}",
        f"{fn}.{sn}@{domain}",
        f"{fn}{rng.randint(1, 999)}@{domain}",
        f"{fn[0]}{sn}{birth_year % 100:02d}@{domain}",
    ]
    return rng.choice(patterns)


def generate_phone(rng: random.Random) -> str:
    """Generate realistic Indian mobile number (10 digits, starts with 6-9)."""
    first_digit = rng.choice([6, 7, 8, 9])
    remaining = "".join(str(rng.randint(0, 9)) for _ in range(9))
    return f"+91{first_digit}{remaining}"


def generate_school_name(rng: random.Random, city: str) -> str:
    """Generate realistic school name."""
    prefix = rng.choice(SCHOOL_PREFIXES)
    # Some schools have city suffix
    if rng.random() < 0.4:
        return f"{prefix} School, {city}"
    suffix = rng.choice(SCHOOL_SUFFIXES)
    return f"{prefix} {suffix}"


def is_kota_hub(city: str) -> bool:
    """Whether the city is a major coaching hub."""
    return city in KOTA_HUB_CITIES


# =============================================================
# QUICK SANITY TEST
# =============================================================
if __name__ == "__main__":
    rng = random.Random(42)
    print("=" * 70)
    print("INDIAN IDENTITY GENERATOR — SAMPLE OUTPUT (20 students)")
    print("=" * 70)
    for i in range(20):
        city, tier, region = sample_city(rng)
        gender = rng.choice(["male", "female"])
        fn, sn = sample_name(rng, gender, region)
        birth_year = rng.randint(2006, 2010)
        email = generate_email(rng, fn, sn, birth_year)
        phone = generate_phone(rng)
        school = generate_school_name(rng, city)
        hub_tag = " 🏫KOTA-HUB" if is_kota_hub(city) else ""
        print(f"{i+1:2d}. {fn} {sn} ({gender[0].upper()}, age {2026-birth_year})")
        print(f"    📍 {city} [{tier}, {region}]{hub_tag}")
        print(f"    📧 {email}")
        print(f"    📱 {phone}")
        print(f"    🎓 {school}")
        print()