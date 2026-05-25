"""
Skill Similarity Mapping Configuration
Maps skills to similar/transferable alternatives with learning curves
"""
from typing import Dict, List, Any

# Skill similarity mappings with learning timelines
SKILL_SIMILARITY_MAP: Dict[str, Dict[str, Any]] = {
    # .NET Ecosystem
    ".NET": {
        "exact_alternatives": ["ASP.NET", "ASP.NET Core", ".NET Core", ".NET Framework"],
        "highly_similar": {
            "C#": {"similarity": 95, "learning_weeks": 1, "difficulty": "easy"},
            "Java": {"similarity": 85, "learning_weeks": 2, "difficulty": "easy"},
            "TypeScript": {"similarity": 75, "learning_weeks": 3, "difficulty": "medium"}
        },
        "transferable": {
            "Python": {"similarity": 65, "learning_weeks": 4, "difficulty": "medium"},
            "JavaScript": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"}
        },
        "category": "framework",
        "core_concepts": ["OOP", "MVC", "REST APIs", "Entity Framework"],
        "prerequisites": ["C# programming", "OOP concepts"]
    },
    
    "C#": {
        "exact_alternatives": ["C Sharp", "CSharp"],
        "highly_similar": {
            "Java": {"similarity": 90, "learning_weeks": 2, "difficulty": "easy"},
            ".NET": {"similarity": 95, "learning_weeks": 1, "difficulty": "easy"},
            "TypeScript": {"similarity": 80, "learning_weeks": 2, "difficulty": "easy"}
        },
        "transferable": {
            "C++": {"similarity": 75, "learning_weeks": 3, "difficulty": "medium"},
            "Python": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"}
        },
        "category": "programming_language",
        "core_concepts": ["OOP", "LINQ", "Async/Await", "Generics"],
        "prerequisites": ["OOP fundamentals"]
    },
    
    # Java Ecosystem
    "Java": {
        "exact_alternatives": ["Java SE", "Java EE", "OpenJDK"],
        "highly_similar": {
            "C#": {"similarity": 90, "learning_weeks": 2, "difficulty": "easy"},
            "Kotlin": {"similarity": 85, "learning_weeks": 2, "difficulty": "easy"},
            "Scala": {"similarity": 75, "learning_weeks": 4, "difficulty": "medium"}
        },
        "transferable": {
            "Python": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"},
            "TypeScript": {"similarity": 75, "learning_weeks": 3, "difficulty": "medium"}
        },
        "category": "programming_language",
        "core_concepts": ["OOP", "JVM", "Spring Framework", "Collections"],
        "prerequisites": ["OOP concepts", "Data structures"]
    },
    
    "Spring": {
        "exact_alternatives": ["Spring Boot", "Spring Framework", "Spring MVC"],
        "highly_similar": {
            ".NET": {"similarity": 85, "learning_weeks": 3, "difficulty": "medium"},
            "Django": {"similarity": 75, "learning_weeks": 3, "difficulty": "medium"},
            "Express.js": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"}
        },
        "transferable": {
            "Flask": {"similarity": 65, "learning_weeks": 4, "difficulty": "medium"},
            "FastAPI": {"similarity": 65, "learning_weeks": 4, "difficulty": "medium"}
        },
        "category": "framework",
        "core_concepts": ["Dependency Injection", "MVC", "REST", "JPA"],
        "prerequisites": ["Java", "Web development basics"]
    },
    
    # Cloud Platforms
    "Azure": {
        "exact_alternatives": ["Microsoft Azure", "Azure Cloud", "MS Azure"],
        "highly_similar": {
            "AWS": {"similarity": 85, "learning_weeks": 3, "difficulty": "medium"},
            "Google Cloud": {"similarity": 80, "learning_weeks": 3, "difficulty": "medium"},
            "GCP": {"similarity": 80, "learning_weeks": 3, "difficulty": "medium"}
        },
        "transferable": {
            "Docker": {"similarity": 60, "learning_weeks": 6, "difficulty": "medium"},
            "Kubernetes": {"similarity": 65, "learning_weeks": 5, "difficulty": "medium"}
        },
        "category": "cloud_platform",
        "core_concepts": ["Cloud Architecture", "Virtual Machines", "Blob Storage", "Azure Functions", "App Services"],
        "prerequisites": ["Cloud fundamentals", "Networking basics", "DevOps concepts"]
    },
    
    "AWS": {
        "exact_alternatives": ["Amazon Web Services", "Amazon AWS"],
        "highly_similar": {
            "Azure": {"similarity": 85, "learning_weeks": 3, "difficulty": "medium"},
            "Google Cloud": {"similarity": 85, "learning_weeks": 3, "difficulty": "medium"},
            "GCP": {"similarity": 85, "learning_weeks": 3, "difficulty": "medium"}
        },
        "transferable": {
            "Docker": {"similarity": 60, "learning_weeks": 6, "difficulty": "medium"},
            "Terraform": {"similarity": 70, "learning_weeks": 4, "difficulty": "medium"}
        },
        "category": "cloud_platform",
        "core_concepts": ["EC2", "S3", "Lambda", "RDS", "VPC", "IAM"],
        "prerequisites": ["Cloud fundamentals", "Linux basics"]
    },
    
    "Google Cloud": {
        "exact_alternatives": ["GCP", "Google Cloud Platform"],
        "highly_similar": {
            "AWS": {"similarity": 85, "learning_weeks": 3, "difficulty": "medium"},
            "Azure": {"similarity": 80, "learning_weeks": 3, "difficulty": "medium"}
        },
        "transferable": {
            "Docker": {"similarity": 60, "learning_weeks": 6, "difficulty": "medium"},
            "Kubernetes": {"similarity": 70, "learning_weeks": 4, "difficulty": "medium"}
        },
        "category": "cloud_platform",
        "core_concepts": ["Compute Engine", "Cloud Storage", "Cloud Functions", "BigQuery"],
        "prerequisites": ["Cloud fundamentals", "Networking"]
    },
    
    # Python Ecosystem
    "Python": {
        "exact_alternatives": ["Python3", "Python 3"],
        "highly_similar": {
            "JavaScript": {"similarity": 80, "learning_weeks": 2, "difficulty": "easy"},
            "Ruby": {"similarity": 75, "learning_weeks": 2, "difficulty": "easy"},
            "Go": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"}
        },
        "transferable": {
            "Java": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"},
            "C#": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"}
        },
        "category": "programming_language",
        "core_concepts": ["Scripting", "Data structures", "List comprehensions", "Decorators"],
        "prerequisites": ["Programming basics"]
    },

    "Django": {
        "exact_alternatives": ["Django Framework"],
        "highly_similar": {
            "Flask": {"similarity": 85, "learning_weeks": 2, "difficulty": "easy"},
            "FastAPI": {"similarity": 80, "learning_weeks": 2, "difficulty": "easy"},
            "Spring": {"similarity": 70, "learning_weeks": 4, "difficulty": "medium"}
        },
        "transferable": {
            "Express.js": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"},
            ".NET": {"similarity": 65, "learning_weeks": 4, "difficulty": "medium"}
        },
        "category": "framework",
        "core_concepts": ["MVT", "ORM", "REST Framework", "Authentication"],
        "prerequisites": ["Python", "Web development"]
    },

    # JavaScript Ecosystem
    "JavaScript": {
        "exact_alternatives": ["JS", "ECMAScript", "ES6"],
        "highly_similar": {
            "TypeScript": {"similarity": 90, "learning_weeks": 1, "difficulty": "easy"},
            "Python": {"similarity": 75, "learning_weeks": 2, "difficulty": "easy"},
            "Java": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"}
        },
        "transferable": {
            "C#": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"},
            "Go": {"similarity": 65, "learning_weeks": 3, "difficulty": "medium"}
        },
        "category": "programming_language",
        "core_concepts": ["Event-driven", "Async/Await", "Closures", "Prototypes"],
        "prerequisites": ["Programming basics"]
    },

    "React": {
        "exact_alternatives": ["React.js", "ReactJS"],
        "highly_similar": {
            "Vue": {"similarity": 85, "learning_weeks": 2, "difficulty": "easy"},
            "Angular": {"similarity": 75, "learning_weeks": 3, "difficulty": "medium"},
            "Svelte": {"similarity": 75, "learning_weeks": 2, "difficulty": "easy"}
        },
        "transferable": {
            "jQuery": {"similarity": 60, "learning_weeks": 4, "difficulty": "medium"},
            "Blazor": {"similarity": 65, "learning_weeks": 4, "difficulty": "medium"}
        },
        "category": "frontend_framework",
        "core_concepts": ["Components", "JSX", "Hooks", "State Management", "Virtual DOM"],
        "prerequisites": ["JavaScript", "HTML", "CSS"]
    },

    "Angular": {
        "exact_alternatives": ["Angular 2+", "AngularJS"],
        "highly_similar": {
            "React": {"similarity": 80, "learning_weeks": 3, "difficulty": "medium"},
            "Vue": {"similarity": 80, "learning_weeks": 3, "difficulty": "medium"}
        },
        "transferable": {
            "Svelte": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"}
        },
        "category": "frontend_framework",
        "core_concepts": ["TypeScript", "Components", "RxJS", "Dependency Injection"],
        "prerequisites": ["TypeScript", "JavaScript"]
    },

    "Node.js": {
        "exact_alternatives": ["NodeJS", "Node"],
        "highly_similar": {
            "Express.js": {"similarity": 90, "learning_weeks": 1, "difficulty": "easy"},
            "Deno": {"similarity": 80, "learning_weeks": 2, "difficulty": "easy"}
        },
        "transferable": {
            "Python": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"},
            "Go": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"}
        },
        "category": "runtime",
        "core_concepts": ["Event Loop", "NPM", "Async I/O", "Streams"],
        "prerequisites": ["JavaScript"]
    },

    # Databases
    "PostgreSQL": {
        "exact_alternatives": ["Postgres", "psql"],
        "highly_similar": {
            "MySQL": {"similarity": 90, "learning_weeks": 1, "difficulty": "easy"},
            "SQL Server": {"similarity": 85, "learning_weeks": 2, "difficulty": "easy"},
            "Oracle": {"similarity": 80, "learning_weeks": 2, "difficulty": "medium"}
        },
        "transferable": {
            "MongoDB": {"similarity": 60, "learning_weeks": 4, "difficulty": "medium"},
            "SQLite": {"similarity": 85, "learning_weeks": 1, "difficulty": "easy"}
        },
        "category": "database",
        "core_concepts": ["SQL", "ACID", "Indexing", "Joins", "Transactions"],
        "prerequisites": ["Database fundamentals", "SQL basics"]
    },

    "MySQL": {
        "exact_alternatives": ["My SQL"],
        "highly_similar": {
            "PostgreSQL": {"similarity": 90, "learning_weeks": 1, "difficulty": "easy"},
            "MariaDB": {"similarity": 95, "learning_weeks": 1, "difficulty": "easy"},
            "SQL Server": {"similarity": 85, "learning_weeks": 2, "difficulty": "easy"}
        },
        "transferable": {
            "MongoDB": {"similarity": 60, "learning_weeks": 4, "difficulty": "medium"}
        },
        "category": "database",
        "core_concepts": ["SQL", "Replication", "Indexing", "CRUD"],
        "prerequisites": ["SQL basics"]
    },

    "MongoDB": {
        "exact_alternatives": ["Mongo"],
        "highly_similar": {
            "DynamoDB": {"similarity": 80, "learning_weeks": 2, "difficulty": "easy"},
            "CouchDB": {"similarity": 75, "learning_weeks": 2, "difficulty": "easy"},
            "Cassandra": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"}
        },
        "transferable": {
            "PostgreSQL": {"similarity": 65, "learning_weeks": 3, "difficulty": "medium"},
            "Redis": {"similarity": 70, "learning_weeks": 2, "difficulty": "easy"}
        },
        "category": "database",
        "core_concepts": ["NoSQL", "Document Model", "Aggregation Pipeline", "Sharding"],
        "prerequisites": ["Database basics", "JSON"]
    },

    # DevOps & Tools
    "Docker": {
        "exact_alternatives": ["Docker Container"],
        "highly_similar": {
            "Kubernetes": {"similarity": 80, "learning_weeks": 3, "difficulty": "medium"},
            "Podman": {"similarity": 85, "learning_weeks": 1, "difficulty": "easy"}
        },
        "transferable": {
            "Azure": {"similarity": 60, "learning_weeks": 6, "difficulty": "medium"},
            "AWS": {"similarity": 60, "learning_weeks": 6, "difficulty": "medium"}
        },
        "category": "devops",
        "core_concepts": ["Containerization", "Images", "Dockerfile", "Volumes", "Networking"],
        "prerequisites": ["Linux basics", "Command line"]
    },

    "Kubernetes": {
        "exact_alternatives": ["K8s", "K8"],
        "highly_similar": {
            "Docker Swarm": {"similarity": 80, "learning_weeks": 2, "difficulty": "medium"},
            "OpenShift": {"similarity": 85, "learning_weeks": 2, "difficulty": "medium"}
        },
        "transferable": {
            "Docker": {"similarity": 75, "learning_weeks": 3, "difficulty": "medium"}
        },
        "category": "devops",
        "core_concepts": ["Orchestration", "Pods", "Services", "Deployments", "ConfigMaps"],
        "prerequisites": ["Docker", "YAML", "Networking"]
    },

    "Git": {
        "exact_alternatives": ["GitHub", "GitLab", "Bitbucket"],
        "highly_similar": {
            "SVN": {"similarity": 70, "learning_weeks": 2, "difficulty": "easy"},
            "Mercurial": {"similarity": 75, "learning_weeks": 2, "difficulty": "easy"}
        },
        "transferable": {},
        "category": "version_control",
        "core_concepts": ["Branching", "Merging", "Pull Requests", "Commits"],
        "prerequisites": ["Command line basics"]
    },

    # Mobile Development
    "React Native": {
        "exact_alternatives": ["ReactNative"],
        "highly_similar": {
            "Flutter": {"similarity": 75, "learning_weeks": 3, "difficulty": "medium"},
            "Ionic": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"}
        },
        "transferable": {
            "Swift": {"similarity": 60, "learning_weeks": 6, "difficulty": "hard"},
            "Kotlin": {"similarity": 60, "learning_weeks": 6, "difficulty": "hard"}
        },
        "category": "mobile_framework",
        "core_concepts": ["React", "Native Components", "Cross-platform"],
        "prerequisites": ["React", "JavaScript"]
    },

    "Flutter": {
        "exact_alternatives": [],
        "highly_similar": {
            "React Native": {"similarity": 75, "learning_weeks": 3, "difficulty": "medium"},
            "Xamarin": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"}
        },
        "transferable": {
            "Dart": {"similarity": 90, "learning_weeks": 1, "difficulty": "easy"}
        },
        "category": "mobile_framework",
        "core_concepts": ["Dart", "Widgets", "State Management", "Material Design"],
        "prerequisites": ["Dart", "Mobile development basics"]
    },

    # Data & ML
    "Machine Learning": {
        "exact_alternatives": ["ML"],
        "highly_similar": {
            "Deep Learning": {"similarity": 85, "learning_weeks": 4, "difficulty": "medium"},
            "Data Science": {"similarity": 80, "learning_weeks": 3, "difficulty": "medium"}
        },
        "transferable": {
            "Statistics": {"similarity": 70, "learning_weeks": 6, "difficulty": "medium"},
            "Python": {"similarity": 75, "learning_weeks": 4, "difficulty": "medium"}
        },
        "category": "ai_ml",
        "core_concepts": ["Algorithms", "Model Training", "Feature Engineering", "Evaluation"],
        "prerequisites": ["Python", "Mathematics", "Statistics"]
    },

    "TensorFlow": {
        "exact_alternatives": [],
        "highly_similar": {
            "PyTorch": {"similarity": 85, "learning_weeks": 2, "difficulty": "medium"},
            "Keras": {"similarity": 80, "learning_weeks": 2, "difficulty": "easy"}
        },
        "transferable": {
            "Scikit-learn": {"similarity": 70, "learning_weeks": 3, "difficulty": "medium"}
        },
        "category": "ai_ml",
        "core_concepts": ["Neural Networks", "Deep Learning", "Model Training"],
        "prerequisites": ["Python", "Machine Learning", "NumPy"]
    },
}

# Category-based learning difficulty
LEARNING_DIFFICULTY = {
    "programming_language": {
        "base_weeks": 2,
        "multiplier": 1.0,
        "prerequisites": ["Programming fundamentals", "Data structures"]
    },
    "framework": {
        "base_weeks": 3,
        "multiplier": 1.2,
        "prerequisites": ["Related programming language"]
    },
    "cloud_platform": {
        "base_weeks": 4,
        "multiplier": 1.5,
        "prerequisites": ["Networking", "Linux", "DevOps basics"]
    },
    "database": {
        "base_weeks": 2,
        "multiplier": 1.0,
        "prerequisites": ["SQL basics", "Database concepts"]
    },
    "devops": {
        "base_weeks": 3,
        "multiplier": 1.3,
        "prerequisites": ["Linux", "Command line", "Networking"]
    },
    "frontend_framework": {
        "base_weeks": 2,
        "multiplier": 1.1,
        "prerequisites": ["JavaScript", "HTML", "CSS"]
    },
    "mobile_framework": {
        "base_weeks": 4,
        "multiplier": 1.4,
        "prerequisites": ["Mobile development basics"]
    },
    "ai_ml": {
        "base_weeks": 6,
        "multiplier": 2.0,
        "prerequisites": ["Python", "Mathematics", "Statistics"]
    }
}

# Soft skills (no similar mappings needed, but included for completeness)
SOFT_SKILLS = [
    "Communication",
    "Leadership",
    "Teamwork",
    "Problem Solving",
    "Critical Thinking",
    "Time Management",
    "Adaptability",
    "Creativity",
    "Conflict Resolution",
    "Presentation Skills"
]

def get_skill_mapping(skill_name: str) -> dict:
    """Get skill mapping for a given skill (case-insensitive)"""
    skill_lower = skill_name.lower()

    # Direct match
    for key, value in SKILL_SIMILARITY_MAP.items():
        if key.lower() == skill_lower:
            return {**value, "primary_name": key}

    # Check exact alternatives
    for key, value in SKILL_SIMILARITY_MAP.items():
        if skill_lower in [alt.lower() for alt in value.get("exact_alternatives", [])]:
            return {**value, "primary_name": key}

    return None

def is_soft_skill(skill_name: str) -> bool:
    """Check if a skill is a soft skill"""
    return skill_name in SOFT_SKILLS or skill_name.lower() in [s.lower() for s in SOFT_SKILLS]

