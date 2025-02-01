import requests
import random
from time import sleep

# Base URL - adjust this to match your server
BASE_URL = "https://dolphin-app-bsmq7.ondigitalocean.app/api/person"

# Sample data pools
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
     "interests": ["Mental Health", "Cognitive Science", "Human Behavior", "Psychology Research", "Therapeutic Methods"]}
]

def generate_phone_number():
    """Generate a random phone number in E.164 format"""
    country_code = "+1"  # US code
    number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    return f"{country_code}{number}"

def create_programmer(index):
    """Create a programmer profile"""
    name = f"Tech {chr(65 + index)} Programmer"  # Tech A Programmer, Tech B Programmer, etc.
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
    name = f"{profession_data['profession']} {chr(65 + random.randint(0, 25))}"  # e.g., "Chef A"
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