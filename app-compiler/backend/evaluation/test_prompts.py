REAL_PROMPTS = [
    "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.",
    "Build an e-commerce store with product listings, cart, checkout, payments, and order tracking.",
    "Build a hospital management system with patient records, doctor scheduling, and billing.",
    "Build a school LMS with courses, assignments, grading, and student/teacher roles.",
    "Build a SaaS dashboard with team collaboration, project management, and subscription billing.",
    "Build a food delivery app with restaurant listings, real-time order tracking, and payments.",
    "Build an HR tool with employee profiles, leave management, payroll, and admin approvals.",
    "Build a blog platform with posts, comments, categories, SEO metadata, and author roles.",
    "Build a salon booking system with appointments, staff management, and payment integration.",
    "Build a fintech app with KYC verification, wallet, transactions, and admin dashboard.",
]

EDGE_CASES = [
    "Build an app",
    "Login",
    "Same as Airbnb but better",
    "Build everything",
    "",
    "Build a CRM but also it should order pizza and control my smart home and also fly drones",
    "asdfghjkl qwerty",
    "Build an app with features and pages and users and also payments and also other stuff",
    "मुझे एक ऐप चाहिए जिसमें लॉगिन और डैशबोर्ड हो",
    "Build a platform that does everything Salesforce, Shopify, and Uber do combined",
]

ALL_PROMPTS = [
    {"id": i + 1, "type": "real", "prompt": p}
    for i, p in enumerate(REAL_PROMPTS)
] + [
    {"id": i + 11, "type": "edge_case", "prompt": p}
    for i, p in enumerate(EDGE_CASES)
]