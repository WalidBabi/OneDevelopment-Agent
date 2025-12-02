"""
Management command to add comprehensive career information to knowledge base
"""

from django.core.management.base import BaseCommand
from agent.models import KnowledgeBase
from knowledge.vector_store import get_vector_store
import uuid


class Command(BaseCommand):
    help = 'Add career opportunities information to knowledge base'

    def handle(self, *args, **kwargs):
        self.stdout.write('Adding career opportunities information...')
        
        # Career information about One Development
        career_entries = [
            {
                'title': 'Career Opportunities at One Development',
                'content': '''**Career Opportunities at One Development**

One Development is a leading luxury real estate developer in the UAE, and we are always looking for talented individuals to join our growing team.

**Why Join One Development?**

- **Industry Leader**: Work with one of the UAE's premier real estate developers
- **Growth Opportunities**: Fast-paced environment with opportunities for career advancement
- **Innovative Projects**: Be part of luxury developments that shape Dubai's skyline
- **Competitive Benefits**: Attractive compensation packages and benefits
- **Multicultural Environment**: Work with talented professionals from around the world
- **Prime Location**: Offices in Dubai's key business districts

**Typical Career Paths at One Development:**

1. **Property Development & Management**
   - Project Managers
   - Development Coordinators
   - Property Managers
   - Facility Management Specialists
   - Construction Oversight Roles

2. **Sales & Marketing**
   - Real Estate Sales Consultants
   - Senior Sales Executives
   - Marketing Managers
   - Digital Marketing Specialists
   - Business Development Managers
   - Client Relationship Managers

3. **Customer Support & Service**
   - Customer Service Representatives
   - After-Sales Support Specialists
   - Client Care Coordinators
   - Property Handover Specialists

4. **Investment & Finance**
   - Investment Advisors
   - Financial Analysts
   - Market Research Analysts
   - ROI Specialists

5. **Architecture & Design**
   - Architects
   - Interior Designers
   - Design Coordinators
   - Quality Assurance Specialists

6. **Legal & Compliance**
   - Legal Advisors
   - Contract Specialists
   - Compliance Officers

7. **Technology & Innovation**
   - PropTech Specialists
   - IT Support
   - Digital Transformation Managers
   - Data Analysts

**What We Look For:**

- **Real Estate Experience**: Background in UAE real estate is highly valued
- **Customer Focus**: Passion for delivering exceptional client experiences
- **Professionalism**: High standards of professional conduct
- **Communication Skills**: Excellent English; Arabic is a plus
- **Results-Driven**: Track record of achieving targets and goals
- **Team Player**: Ability to collaborate across departments
- **Adaptability**: Thrive in a dynamic, fast-growing environment

**Application Process:**

1. **Visit Our Careers Page**: Check oneuae.com for current openings
2. **Submit Your Application**: Send CV and cover letter
3. **Initial Screening**: HR review of applications
4. **Interview Process**: Typically 2-3 rounds including department head interview
5. **Offer & Onboarding**: Competitive offer with comprehensive onboarding

**How to Apply:**

📧 **Email**: Send your CV and cover letter through the contact form at oneuae.com
🌐 **Website**: Visit oneuae.com and navigate to the Careers section
💼 **LinkedIn**: Follow One Development on LinkedIn for job postings

**Currently Hiring For (General Roles):**

While specific openings vary, One Development frequently recruits for:
- Real Estate Sales Consultants
- Property Managers
- Customer Service Representatives
- Marketing Specialists
- Project Coordinators

**Note**: For the most current job openings and specific position requirements, please visit oneuae.com or contact our HR team directly.

**Contact for Career Inquiries:**

Visit: oneuae.com
Follow us on LinkedIn: One Development UAE

Join us in building Dubai's future luxury living!''',
                'source_type': 'manual',
                'summary': 'Comprehensive information about career opportunities at One Development, including typical roles, what we look for, and how to apply.'
            },
            {
                'title': 'One Development - Work Culture and Benefits',
                'content': '''**Work Culture at One Development**

At One Development, we pride ourselves on fostering a dynamic, innovative, and inclusive work environment.

**Our Culture:**

- **Excellence-Driven**: We maintain the highest standards in everything we do
- **Innovation**: Embracing new technologies and PropTech solutions
- **Collaboration**: Cross-functional teamwork across all departments
- **Client-Centric**: Every role contributes to exceptional client experiences
- **Diversity & Inclusion**: Welcoming talent from around the world
- **Growth Mindset**: Continuous learning and development opportunities

**Employee Benefits (Typical in UAE Real Estate Industry):**

1. **Compensation**
   - Competitive base salaries
   - Performance-based bonuses
   - Commission structures for sales roles
   - Annual increments based on performance

2. **Work-Life Balance**
   - Standard working hours with flexibility
   - UAE public holidays
   - Annual leave entitlement

3. **Professional Development**
   - Training programs
   - Industry certifications
   - Mentorship opportunities
   - Career progression paths

4. **Health & Wellness**
   - Health insurance coverage
   - Wellness programs

5. **Other Benefits**
   - Visa sponsorship for eligible candidates
   - Relocation assistance (case by case)
   - Dynamic team environment
   - Company events and team building

**Career Growth:**

One Development invests in employee development:
- Regular performance reviews
- Clear career progression paths
- Internal promotion opportunities
- Skill development programs
- Exposure to luxury real estate projects

**What Makes One Development Special:**

✨ **Prestigious Projects**: Work on luxury developments that define Dubai's landscape
🚀 **Fast-Growing Company**: Opportunities to grow with the company
🏆 **Industry Recognition**: Part of an award-winning developer
🌟 **Luxury Segment**: Experience working in high-end real estate
🤝 **Collaborative Teams**: Supportive colleagues and management

**Join Our Team:**

If you're passionate about real estate, driven by excellence, and ready to contribute to luxury development projects in Dubai, we want to hear from you!

For current openings and to apply, visit: **oneuae.com**

Follow us on LinkedIn to stay updated on new opportunities and company news.''',
                'source_type': 'manual',
                'summary': 'Information about work culture, benefits, and what makes One Development a great place to work.'
            },
            {
                'title': 'One Development - Internships and Graduate Programs',
                'content': '''**Internship and Graduate Opportunities at One Development**

One Development offers opportunities for students, recent graduates, and young professionals looking to start their careers in UAE real estate.

**Internship Programs:**

We occasionally offer internships in various departments:

- **Sales & Marketing Internships**: Learn about luxury property sales and digital marketing
- **Property Management Internships**: Understand day-to-day property operations
- **Business Development Internships**: Gain exposure to market research and client acquisition

**What Interns Gain:**

- Real-world experience in luxury real estate
- Mentorship from industry professionals
- Exposure to high-profile projects
- Networking opportunities
- Potential for full-time employment
- Understanding of UAE property market

**Graduate Programs:**

For recent graduates, we offer entry-level positions in:
- Sales Associate roles
- Junior Property Manager positions
- Marketing Assistant roles
- Customer Service positions

**Eligibility:**

- Currently enrolled in or recently graduated from university
- Relevant degree (Business, Marketing, Real Estate, Architecture, Engineering, etc.)
- Strong communication skills
- Passion for real estate
- Proficiency in English (Arabic is a plus)
- UAE residence or eligibility to obtain visa

**How to Apply for Internships:**

1. Send your CV and cover letter to oneuae.com contact form
2. Clearly mention "Internship Application" in subject
3. Specify which department you're interested in
4. Include your availability dates
5. Attach relevant academic transcripts or certificates

**For Students:**

If you're a student interested in learning about the UAE real estate industry, One Development can be an excellent place to gain practical experience. While internship availability varies, we encourage motivated students to reach out through oneuae.com.

**Note**: Internship and entry-level opportunities are subject to availability and company needs. Please check oneuae.com regularly or contact our HR team for current opportunities.

**Connect With Us:**

🌐 Website: oneuae.com
💼 LinkedIn: Follow One Development for updates
📧 Contact: Use the contact form at oneuae.com for career inquiries

Start your real estate career with One Development!''',
                'source_type': 'manual',
                'summary': 'Information about internships, graduate programs, and entry-level opportunities at One Development.'
            }
        ]
        
        # Get vector store
        vector_store = get_vector_store()
        
        # Add each entry to both database and vector store
        for entry_data in career_entries:
            # Check if entry with same title already exists
            existing = KnowledgeBase.objects.filter(title=entry_data['title']).first()
            
            if existing:
                self.stdout.write(
                    self.style.WARNING(f'Updating existing entry: {entry_data["title"]}')
                )
                existing.content = entry_data['content']
                existing.summary = entry_data['summary']
                existing.is_active = True
                existing.save()
            else:
                # Create new database entry
                kb_entry = KnowledgeBase.objects.create(
                    id=uuid.uuid4(),
                    source_type=entry_data['source_type'],
                    title=entry_data['title'],
                    content=entry_data['content'],
                    summary=entry_data['summary'],
                    is_active=True,
                    metadata={'category': 'career', 'verified': True}
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {entry_data["title"]}')
                )
            
            # Add to vector store
            try:
                vector_store.add_texts(
                    texts=[entry_data['content']],
                    metadatas=[{
                        'source': entry_data['source_type'],
                        'title': entry_data['title'],
                        'category': 'career'
                    }]
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Added to vector store: {entry_data["title"]}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error adding to vector store: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully added {len(career_entries)} career entries to knowledge base!'
            )
        )

