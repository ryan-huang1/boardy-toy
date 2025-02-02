import requests
import random
from time import sleep

# Base URL - adjust this to match your server
BASE_URL = "https://dolphin-app-bsmq7.ondigitalocean.app/api/person"

# Sample data pools
first_names = [
    # Western names
    "James", "Emma", "Michael", "Olivia", "William", "Sophia", "Alexander", "Isabella",
    "Daniel", "Ava", "David", "Mia", "Joseph", "Charlotte", "Matthew", "Amelia",
    "Andrew", "Harper", "John", "Evelyn", "Robert", "Abigail", "Ryan", "Emily",
    "Thomas", "Elizabeth", "Christopher", "Sofia", "Nicholas", "Victoria",
    # Additional Western names
    "Benjamin", "Grace", "Samuel", "Zoe", "Nathan", "Luna", "Adrian", "Lily",
    "Lucas", "Chloe", "Henry", "Aria", "Sebastian", "Scarlett", "Jack", "Aurora",
    # Hispanic names
    "Carlos", "Maria", "Luis", "Ana", "Miguel", "Isabel", "Jose", "Carmen",
    "Antonio", "Elena", "Francisco", "Lucia", "Diego", "Rosa", "Pedro", "Valentina",
    # Asian names
    "Wei", "Mei", "Zhang", "Yuki", "Hiroshi", "Seo-yeon", "Jin", "Aisha",
    "Raj", "Priya", "Amit", "Zara", "Ming", "Li", "Kai", "Ying",
    # African/African American names
    "Malik", "Zara", "Jamal", "Aisha", "Marcus", "Imani", "DeShawn", "Aaliyah",
    "Xavier", "Kenya", "Tyrone", "Latoya", "Malcolm", "Ebony", "Isaiah", "Jasmine"
]

last_names = [
    # Common Western surnames
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    # Additional Western surnames
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen",
    "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera",
    # Asian surnames
    "Chen", "Wang", "Liu", "Zhang", "Kim", "Park", "Singh", "Patel",
    "Wu", "Lin", "Yang", "Suzuki", "Tanaka", "Kumar", "Shah", "Zhao",
    # Hispanic surnames
    "Morales", "Ortiz", "Cruz", "Reyes", "Moreno", "Romero", "Alvarez", "Torres",
    "Ruiz", "Delgado", "Castillo", "Jimenez", "Munoz", "Rivera", "Diaz", "Medina",
    # African/African American surnames
    "Washington", "Jefferson", "Banks", "Freeman", "Brooks", "Jenkins", "Coleman", "Sanders",
    "Booker", "Douglas", "Marshall", "Hayes", "Warren", "Dixon", "Howard", "Richardson"
]

programmer_skills = [
    "Python", "JavaScript", "Java", "C++", "React", "Node.js", "MongoDB",
    "Docker", "AWS", "TypeScript", "Go", "Ruby", "SQL", "GraphQL",
    "Kubernetes", "Machine Learning", "Git", "REST APIs", "DevOps"
]

programmer_interests = [
    "Open Source", "AI/ML", "Web Development", "Blockchain", "Cloud Computing",
    "Cybersecurity", "Game Development", "Mobile Apps", "Data Science",
    "System Architecture", "Tech Startups", "Coding", "Software Design"
]

other_professions = [
    {"profession": "Chef", 
     "skills": ["Culinary Arts", "Menu Planning", "Food Safety", "Kitchen Management", "Pastry Making", "Wine Pairing", "Inventory Management"],
     "interests": ["Cooking", "Food Photography", "Wine Tasting", "Restaurant Management", "Sustainable Food", "World Cuisines"]},
    
    {"profession": "Artist",
     "skills": ["Oil Painting", "Digital Art", "Sculpture", "Color Theory", "Art History", "Canvas Preparation", "Exhibition Design"],
     "interests": ["Contemporary Art", "Gallery Shows", "Art History", "Visual Design", "Photography", "Museum Curation"]},
    
    {"profession": "Teacher",
     "skills": ["Curriculum Development", "Classroom Management", "Educational Technology", "Student Assessment", "Special Education"],
     "interests": ["Education Innovation", "Child Development", "Educational Psychology", "Teaching Methods", "Online Learning"]},
    
    {"profession": "Marketing Manager",
     "skills": ["Digital Marketing", "Social Media", "Content Strategy", "Brand Management", "Analytics", "Campaign Planning"],
     "interests": ["Market Trends", "Consumer Behavior", "Brand Strategy", "Digital Innovation", "Social Media Trends"]},
    
    {"profession": "Nurse",
     "skills": ["Patient Care", "Medical Procedures", "Healthcare Technology", "Emergency Response", "Clinical Assessment"],
     "interests": ["Healthcare Innovation", "Medical Research", "Patient Advocacy", "Wellness", "Healthcare Education"]},
    
    {"profession": "Financial Analyst",
     "skills": ["Financial Modeling", "Data Analysis", "Risk Assessment", "Investment Strategy", "Market Research"],
     "interests": ["Stock Market", "Economic Trends", "Fintech", "Investment Strategies", "Cryptocurrency"]},
    
    {"profession": "Architect",
     "skills": ["AutoCAD", "3D Modeling", "Sustainable Design", "Project Management", "Building Codes"],
     "interests": ["Urban Planning", "Sustainable Architecture", "Design Innovation", "Historic Preservation", "Green Building"]},
    
    {"profession": "Personal Trainer",
     "skills": ["Fitness Programming", "Nutrition Planning", "Exercise Science", "Injury Prevention", "Client Assessment"],
     "interests": ["Fitness Trends", "Sports Science", "Nutrition", "Wellness Coaching", "Athletic Performance"]},
    
    {"profession": "Writer",
     "skills": ["Creative Writing", "Content Creation", "Editing", "Research", "Storytelling"],
     "interests": ["Literature", "Publishing", "Digital Media", "Creative Writing", "Journalism"]},
    
    {"profession": "Psychologist",
     "skills": ["Psychological Assessment", "Counseling", "Research Methods", "Behavioral Analysis", "Therapy Techniques"],
     "interests": ["Mental Health", "Cognitive Science", "Human Behavior", "Psychology Research", "Therapeutic Methods"]},
     
    {"profession": "Environmental Scientist",
     "skills": ["Data Analysis", "Field Research", "Environmental Monitoring", "GIS Mapping", "Lab Techniques", "Scientific Writing"],
     "interests": ["Climate Change", "Conservation", "Renewable Energy", "Biodiversity", "Sustainable Development"]},
     
    {"profession": "UX Designer",
     "skills": ["User Research", "Wireframing", "Prototyping", "Usability Testing", "Interface Design", "Design Systems"],
     "interests": ["Human-Computer Interaction", "Design Thinking", "Accessibility", "Mobile Design", "User Psychology"]},
     
    {"profession": "Data Scientist",
     "skills": ["Statistical Analysis", "Machine Learning", "Python", "R", "Data Visualization", "Big Data Technologies"],
     "interests": ["Artificial Intelligence", "Deep Learning", "Data Ethics", "Predictive Analytics", "Natural Language Processing"]},
     
    {"profession": "Veterinarian",
     "skills": ["Animal Medicine", "Surgery", "Diagnostic Imaging", "Preventive Care", "Emergency Medicine"],
     "interests": ["Animal Welfare", "Wildlife Conservation", "Veterinary Research", "Pet Nutrition", "Exotic Animal Care"]},
     
    {"profession": "Music Producer",
     "skills": ["Audio Engineering", "Music Theory", "Digital Audio Workstations", "Sound Design", "Mixing", "Mastering"],
     "interests": ["Music Technology", "Sound Innovation", "Audio Production", "Electronic Music", "Industry Trends"]},
     
    {"profession": "Civil Engineer",
     "skills": ["Structural Analysis", "Construction Management", "CAD", "Materials Science", "Site Planning"],
     "interests": ["Infrastructure Development", "Sustainable Construction", "Smart Cities", "Transportation", "Environmental Impact"]},
     
    {"profession": "Event Planner",
     "skills": ["Venue Management", "Budget Planning", "Vendor Relations", "Marketing", "Logistics Coordination"],
     "interests": ["Event Design", "Corporate Events", "Wedding Planning", "Virtual Events", "Sustainable Events"]},
     
    {"profession": "Pharmacist",
     "skills": ["Medication Management", "Patient Counseling", "Pharmacy Law", "Clinical Analysis", "Drug Safety"],
     "interests": ["Pharmaceutical Research", "Healthcare Technology", "Patient Care", "Drug Development", "Public Health"]},
     
    {"profession": "Interior Designer",
     "skills": ["Space Planning", "Color Theory", "CAD Software", "Materials Selection", "Project Management"],
     "interests": ["Sustainable Design", "Home Automation", "Architecture", "Furniture Design", "Design Psychology"]},
     
    {"profession": "Social Media Manager",
     "skills": ["Content Creation", "Community Management", "Analytics", "Social Media Strategy", "Influencer Marketing"],
     "interests": ["Digital Marketing", "Social Media Trends", "Brand Building", "Content Strategy", "Online Communities"]},
     
    {"profession": "Cybersecurity Analyst",
     "skills": ["Network Security", "Penetration Testing", "Incident Response", "Security Auditing", "Cryptography", "Threat Analysis"],
     "interests": ["Information Security", "Cyber Threats", "Privacy", "Blockchain Security", "Zero Trust Architecture"]},
     
    {"profession": "Renewable Energy Engineer",
     "skills": ["Solar System Design", "Wind Energy", "Energy Storage", "Grid Integration", "Environmental Impact Assessment"],
     "interests": ["Clean Energy", "Sustainability", "Climate Solutions", "Energy Innovation", "Green Technology"]},
     
    {"profession": "Food Scientist",
     "skills": ["Food Chemistry", "Product Development", "Quality Control", "Sensory Analysis", "Food Safety Regulations"],
     "interests": ["Food Innovation", "Sustainable Food", "Nutrition Science", "Food Technology", "Plant-based Foods"]},
     
    {"profession": "Biomedical Engineer",
     "skills": ["Medical Device Design", "Clinical Testing", "Biomechanics", "Regulatory Compliance", "Product Development"],
     "interests": ["Medical Innovation", "Healthcare Technology", "Biotechnology", "Prosthetics", "Digital Health"]},
     
    {"profession": "Game Designer",
     "skills": ["Game Mechanics", "Level Design", "Unity/Unreal Engine", "3D Modeling", "Scripting", "User Experience"],
     "interests": ["Video Games", "Interactive Storytelling", "Virtual Reality", "Game AI", "Player Psychology"]},
     
    {"profession": "Forensic Scientist",
     "skills": ["Crime Scene Analysis", "DNA Analysis", "Chemical Analysis", "Evidence Collection", "Laboratory Techniques"],
     "interests": ["Criminal Investigation", "Forensic Technology", "Scientific Research", "Legal Procedures", "Analytical Methods"]},
     
    {"profession": "Urban Planner",
     "skills": ["City Planning", "Zoning Laws", "GIS", "Public Policy", "Environmental Planning", "Transportation Planning"],
     "interests": ["Smart Cities", "Sustainable Development", "Public Spaces", "Urban Design", "Community Development"]},
     
    {"profession": "Marine Biologist",
     "skills": ["Marine Ecology", "Field Research", "Data Collection", "Species Identification", "Conservation Techniques"],
     "interests": ["Ocean Conservation", "Marine Life", "Climate Impact", "Ecosystem Research", "Sustainable Fishing"]},
     
    {"profession": "AI Ethics Researcher",
     "skills": ["AI Systems Analysis", "Policy Development", "Research Methods", "Technical Writing", "Impact Assessment"],
     "interests": ["Ethical AI", "Technology Impact", "AI Safety", "Digital Rights", "Future of AI"]},
     
    {"profession": "Quantum Computing Researcher",
     "skills": ["Quantum Mechanics", "Quantum Programming", "Algorithm Design", "Mathematics", "Physics"],
     "interests": ["Quantum Technology", "Computing Innovation", "Physics Research", "Cryptography", "Scientific Discovery"]},
     
    {"profession": "Robotics Engineer",
     "skills": ["Robot Programming", "Mechanical Design", "Control Systems", "Sensor Integration", "Prototyping"],
     "interests": ["Automation", "AI Integration", "Human-Robot Interaction", "Industrial Robotics", "Innovation"]},
     
    {"profession": "Blockchain Developer",
     "skills": ["Smart Contracts", "Distributed Systems", "Cryptography", "Solidity", "Web3"],
     "interests": ["Cryptocurrency", "DeFi", "Blockchain Innovation", "Digital Currency", "Decentralized Systems"]},
     
    {"profession": "Neuroscientist",
     "skills": ["Brain Imaging", "Data Analysis", "Clinical Research", "Experimental Design", "Neural Networks"],
     "interests": ["Brain Research", "Cognitive Science", "Mental Health", "Neurotechnology", "Brain-Computer Interfaces"]},
     
    {"profession": "Space Systems Engineer",
     "skills": ["Spacecraft Design", "Orbital Mechanics", "Propulsion Systems", "Systems Integration", "Mission Planning"],
     "interests": ["Space Exploration", "Satellite Technology", "Aerospace Innovation", "Mars Missions", "Space Science"]}
]

def generate_phone_number():
    """Generate a random phone number in E.164 format"""
    country_code = "+1"  # US code
    number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    return f"{country_code}{number}"

def create_programmer(index):
    """Create a programmer profile"""
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    skills = random.sample(programmer_skills, random.randint(3, 6))
    interests = random.sample(programmer_interests, random.randint(2, 4))
    
    return {
        "phoneNumber": generate_phone_number(),
        "name": name,
        "skills": skills,
        "interests": interests,
        "bio": f"Software developer passionate about {', '.join(random.sample(interests, min(2, len(interests))))}",
        "location": random.choice(["San Francisco, CA", "Seattle, WA", "New York, NY", "Austin, TX", "Boston, MA"])
    }

def create_other_professional(profession_data):
    """Create a non-programmer profile"""
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    skills = random.sample(profession_data["skills"], random.randint(3, len(profession_data["skills"])))
    interests = random.sample(profession_data["interests"], random.randint(2, len(profession_data["interests"])))
    
    return {
        "phoneNumber": generate_phone_number(),
        "name": name,
        "skills": skills,
        "interests": interests,
        "bio": f"Experienced {profession_data['profession'].lower()} specializing in {', '.join(random.sample(skills, min(2, len(skills))))}",
        "location": random.choice(["Los Angeles, CA", "Chicago, IL", "Miami, FL", "Denver, CO", "Portland, OR"])
    }

def main():
    # Create 10 programmers
    print("Creating programmer profiles...")
    for i in range(10):
        try:
            person = create_programmer(i)
            response = requests.post(f"{BASE_URL}/create", json=person)
            response.raise_for_status()  # Raise an exception for bad status codes
            result = response.json()
            if result.get('success'):
                print(f"Created programmer: {person['name']}")
            else:
                print(f"Failed to create programmer {person['name']}: {result.get('error', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed for programmer {person['name']}: {str(e)}")
        except Exception as e:
            print(f"Error creating programmer {person['name']}: {str(e)}")
        sleep(0.5)  # Add small delay between requests
    
    # Create 10 other professionals
    print("\nCreating other professional profiles...")
    other_professions_sample = random.sample(other_professions, 10)
    for profession_data in other_professions_sample:
        try:
            person = create_other_professional(profession_data)
            response = requests.post(f"{BASE_URL}/create", json=person)
            response.raise_for_status()  # Raise an exception for bad status codes
            result = response.json()
            if result.get('success'):
                print(f"Created {profession_data['profession']}: {person['name']}")
            else:
                print(f"Failed to create {profession_data['profession']} {person['name']}: {result.get('error', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {profession_data['profession']} {person['name']}: {str(e)}")
        except Exception as e:
            print(f"Error creating {profession_data['profession']} {person['name']}: {str(e)}")
        sleep(0.5)  # Add small delay between requests

if __name__ == "__main__":
    main() 